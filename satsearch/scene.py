import os
import logging
import requests
import json
from datetime import datetime
import calendar
import satsearch.config as config


logger = logging.getLogger(__name__)


class SatSceneError(Exception):
    pass


class Scene(object):

    _DEFAULT_SOURCE = 'aws_s3'

    def __init__(self, **kwargs):
        """ Initialize a scene object """
        self.metadata = kwargs
        required = ['scene_id', 'date', 'data_geometry', 'download_links']
        if not set(required).issubset(kwargs.keys()):
            raise SatSceneError('Invalid Scene (required parameters: %s' % ' '.join(required))
        # TODO - check validity of date and geometry, at least one download link

    def __repr__(self):
        return self.scene_id

    @property
    def scene_id(self):
        return self.metadata['scene_id']

    @property
    def platform(self):
        return self.metadata.get('satellite_name', '')

    @property
    def date(self):
        return self.metadata['date']

    @property
    def geometry(self):
        return self.metadata['data_geometry']

    @property
    def download_sources(self):
        return self.metadata['download_links'].keys()

    def download_links(self, source=_DEFAULT_SOURCE):
        """ Return dictionary of file key and download link """
        files = self.metadata['download_links'][source]
        prefix = os.path.commonprefix(files)
        keys = [os.path.splitext(f[len(prefix):])[0] for f in files]
        return dict(zip(keys, files))

    def save_thumbnail(self, path=None, nosubdirs=None):
        """ Download thumbnail(s) for this scene """
        url = self.metadata['thumbnail'] if 'aws_thumbnail' not in self.metadata else self.metadata['aws_thumbnail']
        return self.save_file(url, path=path, nosubdirs=nosubdirs)

    def save(self, key=None, source=_DEFAULT_SOURCE, path=None, nosubdirs=None):
        """ Download this key (e.g., a band, or metadata file) from the scene """
        links = self.download_links(source=source)
        # default to all files if no key provided
        if key is None:
            keys = links.keys()
        else:
            keys = [key]
        # loop through keys and get files
        return {k: self.save_file(links[k], path=path, nosubdirs=nosubdirs) for k in keys}

    def save_file(self, url, path=None, nosubdirs=None):
        """ Download a file """
        if path is None:
            path = config.DATADIR
        if nosubdirs is None:
            nosubdirs = config.NOSUBDIRS

        # output path
        if not nosubdirs:
            path = os.path.join(path, self.platform, self.scene_id)
        # make output path if it does not exist
        if not os.path.exists(path):
            os.makedirs(path, exist_ok=True)
        # if basename not provided use basename of url
        filename = os.path.join(path, os.path.basename(url))
        # download file
        logger.info('Downloading %s as %s' % (url, filename))
        r = requests.get(url, stream=True)
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        return filename

    def print_summary(self):
        """ Print summary of metadata """
        print('%s: %s' % (self.date, self.scene_id))


class Scenes(object):
    """ A collection of Scene objects """

    def __init__(self, scenes):
        """ Initialize with a list of Scene objects """
        self.scenes = sorted(scenes, key=lambda s: s.date)

    def __len__(self):
        """ Number of scenes """
        return len(self.scenes)

    def dates(self):
        """ Get sorted list of dates for all scenes """
        return sorted([datetime.strptime(s.date, '%Y-%m-%d') for s in self.scenes])

    def print_summary(self):
        """ Print summary of all scenes """
        [s.print_summary() for s in self.scenes]

    def print_calendar(self):
        """ Print a calendar in terminal indicating which days there are scenes for """
        dates = self.dates()

        # create strings for printed calendar
        total_months = lambda dt: dt.month + 12 * dt.year
        cals = {}
        for tot_m in range(total_months(dates[0])-1, total_months(dates[-1])):
            y, m = divmod(tot_m, 12)
            cals['%s-%s' % (y, m+1)] = calendar.month(y, m+1)

        # color dates in calendar
        for d in dates:
            key = '%s-%s' % (d.year, d.month)
            if cals[key].find(' %s ' % d.day) != -1:
                cals[key] = cals[key].replace(' %s ' % d.day, ' \033[1;31m%s\033[0m ' % d.day)
            elif cals[key].find(' %s\n' % d.day) != -1:
                cals[key] = cals[key].replace(' %s\n' % d.day, ' \033[1;31m%s\033[0m\n' % d.day)
            elif cals[key].find('%s ' % d.day) != -1:
                cals[key] = cals[key].replace('%s ' % d.day, '\033[1;31m%s\033[0m ' % d.day)

        for m in cals:
            print(cals[m])

    def save(self, filename):
        """ Save scene metadata """
        scenes = [s.metadata for s in self.scenes]
        with open(filename, 'w') as f:
            f.write(json.dumps({'scenes': scenes}))

    @classmethod
    def load(cls, filename):
        """ Load a collections class from a file of metadata """
        with open(filename) as f:
            metadata = json.loads(f.read())['scenes']
        scenes = [Scene(**md) for md in metadata]
        return Scenes(scenes)

    def save_thumbnails(self, **kwargs):
        return [s.save_thumbnail(**kwargs) for s in self.scenes]

    def save_files(self, **kwargs):
        return [s.save(**kwargs) for s in self.scenes]
