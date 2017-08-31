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
        self.filenames = {}
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
    def sources(self):
        return self.metadata['download_links'].keys()

    def links(self, source=_DEFAULT_SOURCE):
        """ Return dictionary of file key and download link """
        files = self.metadata['download_links'][source]
        prefix = os.path.commonprefix(files)
        keys = [os.path.splitext(f[len(prefix):])[0] for f in files]
        links = dict(zip(keys, files))
        if source == 'aws_s3' and 'aws_thumbnail' in self.metadata:
            links['thumb'] = self.metadata['aws_thumbnail']
        else:
            links['thumb'] = self.metadata['thumbnail']
        return links

    def geojson(self):
        """ Return metadata as GeoJSON """
        return {
            'type': 'Feature',
            'geometry': self.metadata['data_geometry'],
            'properties': self.metadata
        }

    def get_older_landsat_collection_links(self, link):
        """ From a link string, generate links for previous versions """
        sid = os.path.basename(link).split('_')[0]
        return [link.replace(sid, sid[0:-1] + str(s)) for s in reversed(range(0, int(sid[-1]) + 1))]

    def download(self, key=None, source=_DEFAULT_SOURCE, path=None, nosubdirs=None):
        """ Download this key (e.g., a band, or metadata file) from the scene """
        links = self.links(source=source)
        # default to all files if no key provided
        if key is None:
            keys = links.keys()
        else:
            keys = [key]
        # loop through keys and get files
        for k in keys:
            if k in links:
                # work around because aws landsat not up to collection 1
                # so try to download older collection data if data not available
                if self.platform == 'landsat-8' and source == 'aws_s3':
                    link = self.get_older_landsat_collection_links(links[k])
                else:
                    link = [links[k]]
                for l in link:
                    try:
                        self.filenames[k] = self.download_file(l, path=path, nosubdirs=nosubdirs)
                        break
                    except Exception:
                        logger.error('Unable to download %s' % l)
                if k in self.filenames:
                    #self.metadata['download_links'][source][k] = l
                    logger.info('Downloaded %s as %s' % (l, self.filenames[k]))
        return self.filenames

    @classmethod
    def mkdirp(cls, path):
        """ Recursively make directory """
        if not os.path.isdir(path):
            os.makedirs(path)
        return path

    def download_file(self, url, path=None, nosubdirs=None):
        """ Download a file """
        if path is None:
            path = config.DATADIR
        if nosubdirs is None:
            nosubdirs = config.NOSUBDIRS

        # output path
        if not nosubdirs:
            path = os.path.join(path, self.platform, self.scene_id)
        # make output path if it does not exist
        self.mkdirp(path)
        #if not os.path.exists(path):
        #    os.makedirs(path, exist_ok=True)
        # if basename not provided use basename of url
        filename = os.path.join(path, os.path.basename(url))
        # download file
        logger.info('Downloading %s as %s' % (url, filename))
        resp = requests.get(url, stream=True)
        if resp.status_code != 200:
            raise Exception("Unable to download file %s" % url)
        with open(filename, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=1024):
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
        return sorted([datetime.strptime(s.date, '%Y-%m-%d').date() for s in self.scenes])

    def print_summary(self):
        """ Print summary of all scenes """
        [s.print_summary() for s in self.scenes]

    def text_calendar(self):
        """ Get calendar for dates """
        # start and end dates
        dates = self.dates()
        year1 = dates[0].year
        year2 = dates[-1].year

        # start and end rows
        cols = 3
        row1 = dates[0].month % cols - 1
        row2 = dates[-1].month % cols

        # generate base calendar array
        cal = calendar.Calendar()
        years = []
        for yr in range(year1, year2+1):
            ycal = cal.yeardatescalendar(yr, width=cols)
            if yr == year1 and yr == year2:
                ycal = ycal[row1:row2]
            elif yr == year1:
                ycal = ycal[row1:]
            elif yr == year2:
                ycal = ycal[:row2]
            years.append(ycal)
        return years

        # month and day headers
        months = calendar.month_name
        days = 'Mo Tu We Th Fr Sa Su'
        hformat = '{:^20}  {:^20}  {:^20}\n'
        rformat = ' '.join(['{:>2}'] * 7) + '  '

        # create output
        out = ''
        for iy, yrcal in enumerate(years):
            out += '{:^64}\n\n'.format(year1 + iy)
            for im, mrow in enumerate(yrcal):
                names = [months[im*cols+1], months[im*cols+2], months[im*cols+3]]
                out += hformat.format(names[0], names[1], names[2])
                out += hformat.format(days, days, days)
                for r in range(0, len(mrow[0])):
                    for c in range(0, cols):
                        if len(mrow[c]) == 4:
                            mrow[c].append([''] * 7)
                        if len(mrow[c]) == 5:
                            mrow[c].append([''] * 7)
                        wk = []
                        for d in mrow[c][r]:
                            if d == '' or d.month != im * cols + c + 1:
                                wk.append('')
                            else:
                                if d in dates:
                                    wk.append('\033[31m%s\033[0m' % str(d.day).rjust(2, ' '))
                                else:
                                    wk.append(d.day)
                        out += rformat.format(*wk)

                    out += '\n'
                out += '\n'
        return out

    def save(self, filename):
        """ Save scene metadata """
        with open(filename, 'w') as f:
            f.write(json.dumps(self.geojson()))

    def geojson(self):
        """ Get all metadata as GeoJSON """
        features = [s.geojson() for s in self.scenes]
        return {
            'type': 'FeatureCollection',
            'features': features
        }

    @classmethod
    def load(cls, filename):
        """ Load a collections class from a file of metadata """
        with open(filename) as f:
            metadata = json.loads(f.read())['features']
        scenes = [Scene(**(md['properties'])) for md in metadata]
        return Scenes(scenes)

    def download(self, **kwargs):
        return [s.download(**kwargs) for s in self.scenes]
