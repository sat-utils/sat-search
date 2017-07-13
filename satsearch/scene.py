import os
import logging
import requests
from datetime import datetime
import calendar


logger = logging.getLogger(__name__)


class SatSceneError(Exception):
    pass


class Scene(object):

    _DEFAULT_SOURCE = 'aws_s3'

    def __init__(self, savepath='', id_as_dir=True, **kwargs):
        """ Initialize a scene object """
        self.metadata = kwargs
        required = ['scene_id', 'date', 'data_geometry', 'download_links']
        if not set(required).issubset(kwargs.keys()):
            raise SatSceneError('Invalid Scene (required parameters: %s' % ' '.join(required))

        self.path = savepath
        if id_as_dir:
            self.path = os.path.join(self.path, self.metadata['scene_id'])
        # TODO - check validity of date and geometry, at least one download link

    def __repr__(self):
        return self.scene_id

    @property
    def scene_id(self):
        return self.metadata['scene_id']

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

    def get_thumbnail(self):
        """ Download thumbnail(s) for this scene """
        fname = os.path.join(self.path, os.path.basename(self.metadata['thumbnail']))
        thumb = self.metadata['thumbnail'] if 'aws_thumbnail' not in self.metadata else self.metadata['aws_thumbnail']
        self.get_file(thumb, fname)
        return fname

    def get(self, key, source=_DEFAULT_SOURCE):
        """ Download this key (e.g., a band, or metadata file) from the scene """
        url = self.download_links(source)[key]
        fname = os.path.join(self.path, os.path.basename(url))
        return self.get_file(url, fname)

    def get_all(self, source=_DEFAULT_SOURCE):
        """ Download all files """
        links = self.download_links(source=source)
        fnames = {key: self.get(key, source=source) for key in links}
        return fnames

    def get_file(self, url, filename):
        """ Download a file """
        if not os.path.exists(self.path):
            os.makedirs(self.path, exist_ok=True)
        logger.info('Downloading %s as %s' % (url, filename))
        r = requests.get(url, stream=True)
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        return filename


class Scenes(object):
    """ A collection of Scene objects """

    def __init__(self, scenes):
        """ Initialize with a list of Scene objects """
        self.scenes = scenes

    def dates(self):
        """ Get sorted list of dates for all scenes """
        return sorted([datetime.strptime(s.date, '%Y-%m-%d') for s in self.scenes])

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
