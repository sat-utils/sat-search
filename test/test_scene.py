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
            'datetime': '2017-01-01T00:00:00.0000Z'
        },
        'geometry': {},
        'assets': {
            'MTL': {
                'href': '%sMTL.txt' % prefix
            },
            'B1': {
                'href': '%sB1.TIF' % prefix
            },
            'thumbnail': {
                'href': 'http://landsat-pds.s3.amazonaws.com/L8/007/029/LC80070292016240LGN00/LC80070292016240LGN00_thumb_small.jpg'
            }
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

    def test_init(self):
        """ Initialize a scene """
        scene = self.get_test_scene()
        dt, tm = self.item['properties']['datetime'].split('T')
        self.assertEqual(str(scene.date), dt)
        self.assertEqual(scene.id, self.item['properties']['id'])
        self.assertEqual(scene.geometry, self.item['geometry'])
        self.assertEqual(str(scene), self.item['properties']['id'])

    def test_assets(self):
        """ Get assets for download """
        scene = self.get_test_scene()
        self.assertEqual(scene.assets['B1']['href'], self.item['assets']['B1']['href'])

    def test_download_thumbnail(self):
        """ Get thumbnail for scene """
        scene = self.get_test_scene()
        fname = scene.download(key='thumbnail')
        self.assertTrue(os.path.exists(fname))
        os.remove(fname)
        self.assertFalse(os.path.exists(fname))
        shutil.rmtree(os.path.join(testpath, self.item['properties']['collection']))

    def test_download(self):
        """ Retrieve a data file """
        scene = self.get_test_scene()
        fname = scene.download(key='MTL')
        self.assertTrue(os.path.exists(fname))
        os.remove(fname)
        self.assertFalse(os.path.exists(fname))
        shutil.rmtree(os.path.join(testpath, self.item['properties']['collection']))

    def test_download_all(self):
        """ Retrieve all data files from a source """
        scene = self.get_test_scene()
        fnames = [scene.download(a) for a in scene.assets]
        for f in fnames:
            self.assertTrue(os.path.exists(f))
            os.remove(f)
            self.assertFalse(os.path.exists(f))


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
        self.assertEqual(len(dates), 2)

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
