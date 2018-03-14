import os
import logging
import requests
import json
from string import Formatter, Template
from datetime import datetime
import satsearch.utils as utils
import satsearch.config as config


logger = logging.getLogger(__name__)


class SatSceneError(Exception):
    pass


class Scene(object):

    def __init__(self, feature, source='aws_s3'):
        """ Initialize a scene object """
        required = ['scene_id', 'date', 'download_links']
        if 'geometry' not in feature:
            raise SatSceneError('No geometry supplied')
        if not set(required).issubset(feature['properties'].keys()):
            raise SatSceneError('Invalid Scene (required parameters: %s' % ' '.join(required))
        self.geometry = feature['geometry']
        self.metadata = feature['properties']
        self.metadata['date'] = self.metadata['date'].replace('/', '-')
        self.filenames = {}
        self.source = source
        # TODO - check validity of date and geometry, at least one download link

    @classmethod
    def create_from_satapi_v0(cls, metadata):
        """ Create a Scene from sat-api v1 """
        feature = {
            'type': 'Feature',
            'geometry': metadata.pop('data_geometry'),
            'properties': metadata
        }
        return cls(feature)

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
        pattern = '%Y-%m-%d' if '-' in self.metadata['date'] else '%Y/%m/%d'
        return datetime.strptime(self.metadata['date'], pattern).date()

    @property
    def sources(self):
        return self.metadata['download_links'].keys()

    def links(self):
        """ Return dictionary of file key and download link """
        files = self.metadata['download_links'][self.source]
        prefix = os.path.commonprefix(files)
        keys = [os.path.splitext(f[len(prefix):])[0] for f in files]
        links = dict(zip(keys, files))
        if self.source == 'aws_s3' and 'aws_thumbnail' in self.metadata:
            links['thumb'] = self.metadata['aws_thumbnail']
        else:
            links['thumb'] = self.metadata['thumbnail']
        return links

    def geojson(self):
        """ Return metadata as GeoJSON """
        return {
            'type': 'Feature',
            'geometry': self.geometry,
            'properties': self.metadata
        }

    def bbox(self):
        """ Get bounding box of scene """
        lats = [c[1] for c in self.geometry['coordinates'][0]]
        lons = [c[0] for c in self.geometry['coordinates'][0]]
        return [min(lons), min(lats), max(lons), max(lats)]

    def get_older_landsat_collection_links(self, link):
        """ From a link string, generate links for previous versions """
        sid = os.path.basename(link).split('_')[0]
        return [link.replace(sid, sid[0:-1] + str(s)) for s in reversed(range(0, int(sid[-1]) + 1))]

    def download(self, key=None, path=None, subdirs=None, overwrite=False):
        """ Download this key (e.g., a band, or metadata file) from the scene """
        links = self.links()
        # default to all files if no key provided
        if key is None:
            keys = links.keys()
        else:
            keys = [key]

        path = self.get_path(path=path, subdirs=subdirs)

        # loop through keys and get files
        for key in [k for k in keys if k in links]:
            # work around because aws landsat not up to collection 1
            # so try to download older collection data if data not available
            if self.platform == 'landsat-8' and self.source == 'aws_s3':
                link = self.get_older_landsat_collection_links(links[key])
            else:
                link = [links[key]]
            for l in link:
                try:
                    ext = os.path.splitext(l)[1]
                    fout = os.path.join(path, self.get_filename(suffix=key) + ext)
                    if os.path.exists(fout) and overwrite is False:
                        self.filenames[key] = fout
                    else:
                        self.filenames[key] = self.download_file(l, fout=fout)
                    break
                except Exception as e:
                    print(e)
                    pass
            if key in self.filenames:
                #self.metadata['download_links'][source][k] = l
                logger.info('Downloaded %s as %s' % (l, self.filenames[key]))
            else:
                logger.error('Unable to download %s' % l)
        return self.filenames

    @classmethod
    def mkdirp(cls, path):
        """ Recursively make directory """
        if not os.path.isdir(path):
            os.makedirs(path)
        return path

    def get_path(self, path=None, subdirs=None, no_create=False):
        """ Get local path for this scene """
        if path is None:
            path = config.DATADIR
        if subdirs is None:
            subdirs = config.SUBDIRS
        # create path for this scene
        subs = {}
        for key in [i[1] for i in Formatter().parse(subdirs.rstrip('/')) if i[1] is not None]:
            subs[key] = self.metadata[key]
        _path = os.path.join(path, Template(subdirs).substitute(**subs))
        # make output path if it does not exist
        if not no_create and _path != '':
            self.mkdirp(_path)
        return _path

    def get_filename(self, pattern=None, suffix=None):
        """ Get local filename for this scene """
        fname = config.FILENAME if pattern is None else pattern
        subs = {}
        for key in [i[1] for i in Formatter().parse(fname) if i[1] is not None]:
            subs[key] = self.metadata[key].replace('/', '-')
        fname = Template(fname).substitute(**subs)
        if suffix is not None:
            fname = fname + suffix
        return fname

    def download_file(self, url, fout=None):
        """ Download a file """
        fout = os.path.basename(url) if fout is None else fout
        logger.info('Downloading %s as %s' % (url, fout))
        resp = requests.get(url, stream=True)
        if resp.status_code != 200:
            raise Exception("Unable to download file %s" % url)
        with open(fout, 'wb') as f:
            for chunk in resp.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        return fout

    def review_thumbnail(self):
        """ Display image and give user prompt to keep or discard """
        fname = self.download('thumb')['thumb']
        imgcat = os.getenv('IMGCAT', None)
        if imgcat is None:
            raise Exception("Set $IMGCAT to a terminal display program")
        cmd = '%s %s' % (imgcat, fname)
        print(cmd)
        os.system(cmd)
        print("Press Y to keep, N to delete, or any key to quit")
        while True:
            char = getch()
            if char.lower() == 'y':
                return True
            elif char.lower() == 'n':
                return False
            raise Exception('Cancel')


class Scenes(object):
    """ A collection of Scene objects """

    def __init__(self, scenes, metadata={}):
        """ Initialize with a list of Scene objects """
        self.scenes = sorted(scenes, key=lambda s: s.date)
        self.metadata = metadata

    def __len__(self):
        """ Number of scenes """
        return len(self.scenes)

    def __getitem__(self, index):
        return self.scenes[index]

    def __setitem__(self, index, value):
        self.scenes[index] = value

    def __delitem__(self, index):
        self.scenes.delete(index)

    def dates(self):
        """ Get sorted list of dates for all scenes """
        return sorted([s.date for s in self.scenes])

    def bbox(self):
        """ Get bounding box of search """
        if 'aoi' in self.metadata:
            lats = [c[1] for c in self.metadata['aoi']['coordinates'][0]]
            lons = [c[0] for c in self.metadata['aoi']['coordinates'][0]]
            return [min(lons), min(lats), max(lons), max(lats)]
        else:
            return []

    def center(self):
        if 'aoi' in self.metadata:
            lats = [c[1] for c in self.metadata['aoi']['coordinates'][0]]
            lons = [c[0] for c in self.metadata['aoi']['coordinates'][0]]
            return [(min(lats) + max(lats))/2.0, (min(lons) + max(lons))/2.0]
        else:
            return 0, 0

    def sensors(self, date=None):
        """ List of all available sensors across scenes """
        if date is None:
            return list(set([s.platform for s in self.scenes]))
        else:
            return list(set([s.platform for s in self.scenes if s.date == date]))

    def print_scenes(self, params=[]):
        """ Print summary of all scenes """
        if len(params) == 0:
            params = ['date', 'scene_id']
        txt = 'Scenes (%s):\n' % len(self.scenes)
        txt += ''.join(['{:^20}'.format(p) for p in params]) + '\n'
        for s in self.scenes:
            txt += ''.join(['{:^20}'.format(s.metadata[p]) for p in params]) + '\n'
        print(txt)

    def text_calendar(self):
        """ Get calendar for dates """
        date_labels = {}
        for d in self.dates():
            sensors = self.sensors(d)
            if len(sensors) > 1:
                date_labels[d] = 'Multiple'
            else:
                date_labels[d] = sensors[0]
        return utils.get_text_calendar(date_labels)

    def save(self, filename, append=False):
        """ Save scene metadata """
        if append and os.path.exists(filename):
            with open(filename) as f:
                geoj = json.loads(f.read())
                #metadata = geoj.get('metadata', {})
                features = geoj['features']
        else:
            #metadata = {}
            features = []
        geoj = self.geojson()
        #for key in geoj.get('metadata', {}):
        #    oldmd = metadata.get(key, [])
        #    geoj['metadata'][key] = oldmd + [geoj['metadata'][key]]
        geoj['features'] = features + geoj['features']
        with open(filename, 'w') as f:
            f.write(json.dumps(geoj))

    def geojson(self):
        """ Get all metadata as GeoJSON """
        features = [s.geojson() for s in self.scenes]
        return {
            'type': 'FeatureCollection',
            'features': features,
            'metadata': self.metadata
        }

    @classmethod
    def load(cls, filename):
        """ Load a collections class from a GeoJSON file of metadata """
        with open(filename) as f:
            geoj = json.loads(f.read())
        scenes = [Scene(feature) for feature in geoj['features']]
        metadata = geoj.get('metadata', {})
        return Scenes(scenes, metadata=metadata)

    def filter(self, key, values):
        """ Filter scenes on key matching value """
        scenes = []
        for val in values:
            scenes += list(filter(lambda x: x.metadata[key] == val, self.scenes))
        self.scenes = scenes

    def download(self, **kwargs):
        return [s.download(**kwargs) for s in self.scenes]

    def review_thumbnails(self):
        """ Review all thumbnails in scenes """
        new_scenes = []
        for scene in self.scenes:
            try:
                keep = scene.review_thumbnail()
                if keep:
                    new_scenes.append(scene)
            except Exception as e:
                return
        self.scenes = new_scenes


try:
    from msvcrt import getch
except ImportError:
    def getch():
        import sys, tty, termios
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(sys.stdin.fileno())
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch
