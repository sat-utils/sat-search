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

    def __init__(self, feature):
        """ Initialize a scene object """
        required = ['id', 'datetime']
        if 'geometry' not in feature:
            raise SatSceneError('No geometry supplied')
        if not set(required).issubset(feature['properties'].keys()):
            raise SatSceneError('Invalid Scene (required parameters: %s' % ' '.join(required))
        self.feature = feature

        # QGIS altered date format when editing this GeoJSON file
        #self['datetime'] = self['datetime'].replace('/', '-')
        self.filenames = {}
        # TODO - add validator

    def __repr__(self):
        return self['id']

    def __getitem__(self, key):
        try:
            return getattr(self, key)
        except:
            return self.feature['properties'][key]

    def keys(self):
        return self.feature['properties'].keys()

    @property
    def id(self):
        return self.feature['properties']['id']

    @property
    def geometry(self):
        return self.feature['geometry']

    @property
    def date(self):
        dt = self['datetime'].replace('/', '-')
        pattern = "%Y-%m-%dT%H:%M:%S.%fZ"
        return datetime.strptime(dt, pattern).date()

    @property
    def assets(self):
        """ Return dictionary of file key and download link """
        return self.feature['assets']
        #prefix = os.path.commonprefix(files)
        #keys = [os.path.splitext(f[len(prefix):])[0] for f in files]
        #links = dict(zip(keys, files))

    @property
    def links(self):
        """ Return dictionary of links """
        return self.feature['links']

    @property
    def bbox(self):
        """ Get bounding box of scene """
        lats = [c[1] for c in self.geometry['coordinates'][0]]
        lons = [c[0] for c in self.geometry['coordinates'][0]]
        return [min(lons), min(lats), max(lons), max(lats)]

    def download(self, key, overwrite=False):
        """ Download this key (e.g., a band, or metadata file) from the scene """
 
        # legacy hack - this function used to download multiple keys, now just one
        keys = [key]

        path = self.get_path()
        # loop through keys and get files
        for key in [k for k in keys if k in self.assets]:
            try:
                href = self.assets[key]['href']
                
                ext = os.path.splitext(href)[1]
                fout = os.path.join(path, self.get_filename(suffix='_'+key) + ext)
                if os.path.exists(fout) and overwrite is False:
                    self.filenames[key] = fout
                else:
                    self.filenames[key] = self.download_file(href, fout=fout)
            except Exception as e:
                logger.error('Unable to download %s: %s' % (href, str(e)))
        if key in self.filenames:
            return self.filenames[key]
        else:
            return None

    @classmethod
    def mkdirp(cls, path):
        """ Recursively make directory """
        if not os.path.isdir(path):
            os.makedirs(path)
        return path

    def string_sub(self, string):
        string = string.replace(':', '_colon_')
        subs = {}
        for key in [i[1] for i in Formatter().parse(string.rstrip('/')) if i[1] is not None]:
            if key == 'date':
                subs[key] = self.date
            else:
                subs[key] = self[key.replace('_colon_', ':')]
        return Template(string).substitute(**subs)        

    def get_path(self, no_create=False):
        """ Get local path for this scene """
        path = self.string_sub(config.DATADIR)
        if not no_create and path != '':
            self.mkdirp(path)       
        return path

    def get_filename(self, suffix=None):
        """ Get local filename for this scene """
        fname = self.string_sub(config.FILENAME)
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
        bname, ext = os.path.splitext(fout)
        #if ext == '.jpg':
        #    wldfile = bname + '.wld'
        #    coords = self.geometry['coordinates'][0]
        #    lats = [c[1] for c in coords]
        #    lons = [c[0] for c in coords]
        #    with open(wldfile, 'w') as f:
        #        f.write('%s\n' % ((max(lons)-min(lons))/1155))
        #        f.write('0.0\n0.0\n')
        #        f.write('%s\n' % (-(max(lats)-min(lats))/1174))
        #        f.write('%s\n%s\n' % (min(lons), max(lats)))

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

    def __init__(self, scenes, properties={}):
        """ Initialize with a list of Scene objects """
        self.scenes = sorted(scenes, key=lambda s: s.date)
        self.properties = properties
        for p in properties:
            if isinstance(properties[p], str):
                try:
                    _p = json.loads(properties[p])
                    self.properties[p] = _p
                except:
                    self.properties[p] = properties[p]
        self.collections

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

    def collections(self):
        """ Get collection records for this list of scenes """
        return self.collections

    def bbox(self):
        """ Get bounding box of search """
        if 'intersects' in self.properties:
            coords = self.properties['intersects']['geometry']['coordinates']
            lats = [c[1] for c in coords[0]]
            lons = [c[0] for c in coords[0]]
            return [min(lons), min(lats), max(lons), max(lats)]
        else:
            return []

    def center(self):
        if 'intersects' in self.properties:
            coords = self.properties['intersects']['geometry']['coordinates']
            lats = [c[1] for c in coords[0]]
            lons = [c[0] for c in coords[0]]
            return [(min(lats) + max(lats))/2.0, (min(lons) + max(lons))/2.0]
        else:
            return 0, 0

    #def __getitem__(self, key):
    #    return self.feature['properties'][key]

    def platforms(self, date=None):
        """ List of all available sensors across scenes """
        if date is None:
            return list(set([s['eo:platform'] for s in self.scenes]))
        else:
            return list(set([s['eo:platform'] for s in self.scenes if s.date == date]))

    def print_scenes(self, params=[]):
        """ Print summary of all scenes """
        if len(params) == 0:
            params = ['date', 'id']
        txt = 'Scenes (%s):\n' % len(self.scenes)
        txt += ''.join(['{:<20}'.format(p) for p in params]) + '\n'
        for s in self.scenes:
            # NOTE - the string conversion is because .date returns a datetime obj
            txt += ''.join(['{:<20}'.format(str(s[p])) for p in params]) + '\n'
        print(txt)

    def text_calendar(self):
        """ Get calendar for dates """
        date_labels = {}
        dates = self.dates()
        if len(dates) == 0:
            return ''
        for d in self.dates():
            sensors = self.platforms(d)
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
                features = geoj['features']
                # TODO - figure out what to when new Scenes properties!
        else:
            properties = {}
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
        features = [s.feature for s in self.scenes]
        return {
            'type': 'FeatureCollection',
            'features': features,
            'properties': self.properties
        }

    @classmethod
    def load(cls, filename):
        """ Load a collections class from a GeoJSON file of metadata """
        with open(filename) as f:
            geoj = json.loads(f.read())
        scenes = [Scene(feature) for feature in geoj['features']]
        return Scenes(scenes, properties=geoj.get('properties', {}))

    def filter(self, key, values):
        """ Filter scenes on key matching value """
        scenes = []
        for val in values:
            scenes += list(filter(lambda x: x[key] == val, self.scenes))
        self.scenes = scenes

    def download(self, **kwargs):
        dls = []
        for s in self.scenes:
            fname = s.download(**kwargs)
            if fname is not None:
                dls.append(fname)
        return dls

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
