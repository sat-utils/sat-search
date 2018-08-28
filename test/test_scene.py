import datetime
import os
import unittest
import shutil
import satsearch.config as config
from satsearch.scene import Scene, Scenes, SatSceneError


testpath = os.path.dirname(__file__)


class TestScene(unittest.TestCase):

    path = os.path.dirname(__file__)

    prefix = 'http://landsat-pds.s3.amazonaws.com/L8/007/029/LC80070292016240LGN00/LC80070292016240LGN00_',

    item = {
        'geometry': {},
        'properties': {
            'id': 'testscene',
            'collection': 'test_collection',
            'datetime': '2017-01-01T00:00:00.0000Z',
            'eo:platform': 'test_platform'
        },
        "bbox": [
            -71.46676936182894,
            42.338371079679106,
            -70.09532154452742,
            43.347431265475954
        ],
        "geometry": {
            "type": "Polygon",
            "coordinates": [
                [
                    [
                        -71.46676936182894,
                        43.32623760511659
                    ],
                    [
                        -70.11293433656888,
                        43.347431265475954
                    ],
                    [
                        -70.09532154452742,
                        42.35884880571144
                    ],
                    [
                        -71.42776890002204,
                        42.338371079679106
                    ],
                    [
                        -71.46676936182894,
                        43.32623760511659
                    ]
                ]
            ]
        },
        'assets': {
            'MTL': {
                'href': '%sMTL.txt' % prefix
            },
            'B1': {
                'href': '%sB1.TIF' % prefix,
                'eo:bands': ['B1']
            },
            'fake_asset': {
                'href': 'nourl',
            },
            'thumbnail': {
                'href': 'http://landsat-pds.s3.amazonaws.com/L8/007/029/LC80070292016240LGN00/LC80070292016240LGN00_thumb_small.jpg'
            }
        },
        'links': {
            'self': {'href': 'link/to/self'}
        },
        'eo:bands': {
            'B1': {'common_name': 'coastal'}
        }
    }

    @classmethod
    def setUpClass(cls):
        """ Configure testing class """
        config.DATADIR = os.path.join(testpath, config.DATADIR)

    def get_test_scene(self):
        """ Get valid test scene """
        return Scene(self.item)

    def test_invalid_init(self):
        """ Initialize a scene with insufficient metadata """
        with self.assertRaises(SatSceneError):
            Scene({'meaninglesskey': 'meaninglessstring'})
        with self.assertRaises(SatSceneError):
            Scene({'geometry': {}})

    def test_init(self):
        """ Initialize a scene """
        scene = self.get_test_scene()
        dt, tm = self.item['properties']['datetime'].split('T')
        self.assertEqual(str(scene.date), dt)
        self.assertEqual(scene.id, self.item['properties']['id'])
        self.assertEqual(scene.geometry, self.item['geometry'])
        self.assertEqual(str(scene), self.item['properties']['id'])
        assert(list(scene.keys()) == ['id', 'collection', 'datetime', 'eo:platform'])

    def test_class_properties(self):
        """ Test the property functions of the Scene class """
        scene = self.get_test_scene()
        assert(scene.links['self']['href'] == 'link/to/self')
        assert(scene.bbox == [-71.46676936182894, 42.338371079679106, -70.09532154452742, 43.347431265475954])

    def test_assets(self):
        """ Get assets for download """
        scene = self.get_test_scene()
        assert(scene.assets['B1']['href'] == self.item['assets']['B1']['href'])
        assert(scene.asset('coastal')['href'] == self.item['assets']['B1']['href'])

    def test_download_thumbnail(self):
        """ Get thumbnail for scene """
        scene = self.get_test_scene()
        fname = scene.download(key='thumbnail')
        self.assertTrue(os.path.exists(fname))
        os.remove(fname)
        self.assertFalse(os.path.exists(fname))
        #shutil.rmtree(os.path.join(testpath, self.item['properties']['collection']))

    def test_download(self):
        """ Retrieve a data file """
        scene = self.get_test_scene()
        fname = scene.download(key='MTL')
        self.assertTrue(os.path.exists(fname))
        fname = scene.download(key='MTL')
        assert(os.path.exists(fname))
        os.remove(fname)
        self.assertFalse(os.path.exists(fname))
        #shutil.rmtree(os.path.join(testpath, self.item['properties']['collection']))

    def test_download_paths(self):
        """ Testing of download paths and filenames """
        scene = self.get_test_scene()
        datadir = config.DATADIR
        filename = config.FILENAME
        config.DATADIR = os.path.join(testpath, '${date}')
        config.FILENAME = '${date}_${id}'
        fname = scene.download('MTL')
        _fname = os.path.join(testpath, '2017-01-01/2017-01-01_testscene_MTL.txt')
        assert(fname == _fname)
        assert(os.path.exists(fname))
        config.DATADIR = datadir
        config.FILENAME = filename
        shutil.rmtree(os.path.join(testpath, '2017-01-01'))
        assert(os.path.exists(fname) == False)

    def test_download_nonexist(self):
        """ Test downloading of non-existent file """
        scene = self.get_test_scene()
        fname = scene.download(key='fake_asset')
        assert(fname is None)

    def test_download_all(self):
        """ Retrieve all data files from a source """
        scene = self.get_test_scene()
        fnames = [scene.download(a) for a in scene.assets if a != 'fake_asset']
        for f in fnames:
            self.assertTrue(os.path.exists(f))
            os.remove(f)
            self.assertFalse(os.path.exists(f))

    def test_create_derived(self):
        """ Create single derived scene """
        scenes = [self.get_test_scene(), self.get_test_scene()]
        scene = Scene.create_derived(scenes)
        assert(scene.date == scenes[0].date)
        assert(scene['c:id'] == scenes[0]['c:id'])


class TestScenes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """ Configure testing class """
        config.DATADIR = testpath

    def load_scenes(self):
        return Scenes.load(os.path.join(testpath, 'scenes.geojson'))

    def test_load(self):
        """ Initialize Scenes with list of Scene objects """
        scenes = self.load_scenes()
        self.assertEqual(len(scenes), 2)
        self.assertTrue(isinstance(scenes.scenes[0], Scene))

    def test_save(self):
        """ Save scenes list """
        scenes = self.load_scenes()
        fname = os.path.join(testpath, 'save-test.json')
        scenes.save(fname)
        self.assertTrue(os.path.exists(fname))
        os.remove(fname)
        self.assertFalse(os.path.exists(fname))

    def test_print_scenes(self):
        """ Print summary of scenes """
        scenes = self.load_scenes()
        scenes.print_scenes()

    def test_dates(self):
        """ Get dates of all scenes """
        scenes = self.load_scenes()
        dates = scenes.dates()
        self.assertEqual(len(dates), 1)

    def test_text_calendar(self):
        """ Get calendar """
        scenes = self.load_scenes()
        cal = scenes.text_calendar()
        self.assertTrue(len(cal) > 250)

    def test_download_thumbnails(self):
        """ Download all thumbnails """
        scenes = self.load_scenes()
        fnames = scenes.download(key='thumbnail')
        for f in fnames:
            self.assertTrue(os.path.exists(f))
            os.remove(f)
            self.assertFalse(os.path.exists(f))
        #shutil.rmtree(os.path.join(testpath, 'landsat-8-l1'))

    def test_filter(self):
        scenes = self.load_scenes()
        scenes.filter('eo:platform', ['landsat-8'])
        assert(len(scenes) == 1)

    def test_download(self):
        """ Download a data file from all scenes """
        scenes = self.load_scenes()
        
        fnames = scenes.download(key='MTL')
        assert(len(fnames) == 1)
        for f in fnames:
            self.assertTrue(os.path.exists(f))
            os.remove(f)
            self.assertFalse(os.path.exists(f))
        #shutil.rmtree(os.path.join(testpath, 'landsat-8-l1'))
