import os
import unittest
import shutil
import satsearch.config as config
from satsearch.scene import Scene, Scenes, SatSceneError
from nose.tools import raises


testpath = os.path.dirname(__file__)


class TestScene(unittest.TestCase):

    path = os.path.dirname(__file__)

    prefix = {
        'aws_s3': 'http://landsat-pds.s3.amazonaws.com/L8/007/029/LC80070292016240LGN00/LC80070292016240LGN00_',
        'google': 'https://storage.cloud.google.com/gcp-public-data-landsat/LC08/01/007/029/'
                  'LC08_L1TP_007029_20160827_20170321_01_T1/LC08_L1TP_007029_20160827_20170321_01_T1_'
    }

    md = {
        'scene_id': 'testscene',
        'satellite_name': 'test_satellite',
        'date': '2017-01-01',
        'data_geometry': {},
        'thumbnail': '%sthumb_large.jpg' % prefix['aws_s3'],
        'download_links': {
            'aws_s3': [
                '%sB1.TIF' % prefix['aws_s3'],
                '%sMTL.txt' % prefix['aws_s3']
            ],
            'test': [
                '%sANG.TIF' % prefix['aws_s3'],
                '%sMTL.txt' % prefix['aws_s3']
            ],
            "google": [
                '%sANG.txt' % prefix['google'],
                '%sMTL.txt' % prefix['google']
            ]
        }
    }

    @classmethod
    def setUpClass(cls):
        """ Configure testing class """
        config.DATADIR = testpath

    def get_test_scene(self):
        """ Get valid test scene """
        return Scene(**self.md)

    @raises(SatSceneError)
    def test_invalid_init(self):
        """ Initialize a scene with insufficient metadata """
        Scene(meaninglesskwarg='meaninglessstring')

    def test_init(self):
        """ Initialize a scene """
        scene = self.get_test_scene()
        self.assertEqual(scene.date, self.md['date'])
        self.assertEqual(scene.scene_id, self.md['scene_id'])
        self.assertEqual(scene.geometry, self.md['data_geometry'])
        self.assertEqual(scene.sources, self.md['download_links'].keys())

    def test_links(self):
        """ Get links for download """
        scene = self.get_test_scene()
        links = scene.links()
        self.assertEqual(links['B1'], self.md['download_links']['aws_s3'][0])

    def test_download_thumbnail(self):
        """ Get thumbnail for scene """
        scene = self.get_test_scene()
        fname = scene.download(key='thumb')['thumb']
        self.assertTrue(os.path.exists(fname))
        os.remove(fname)
        self.assertFalse(os.path.exists(fname))
        shutil.rmtree(os.path.join(testpath, self.md['satellite_name']))

    def test_download(self):
        """ Retrieve a data file """
        scene = self.get_test_scene()
        fnames = scene.download(key='MTL')
        for f in fnames.values():
            self.assertTrue(os.path.exists(f))
            os.remove(f)
            self.assertFalse(os.path.exists(f))
        shutil.rmtree(os.path.join(testpath, self.md['satellite_name']))

    def test_download_all(self):
        """ Retrieve all data files from a source """
        scene = self.get_test_scene()
        fnames = scene.download(source='test')
        for f in fnames.values():
            self.assertTrue(os.path.exists(f))
            os.remove(f)
            self.assertFalse(os.path.exists(f))

    def test_print_summary(self):
        """ Print summary metadata """
        scene = self.get_test_scene()
        scene.print_summary()


class TestScenes(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """ Configure testing class """
        config.DATADIR = testpath

    def load_scenes(self):
        return Scenes.load(os.path.join(testpath, 'scenes.json'))

    def test_load(self):
        """ Initialize Scenes with list of Scene objects """
        scenes = self.load_scenes()
        self.assertEqual(len(scenes), 10)
        self.assertTrue(isinstance(scenes.scenes[0], Scene))

    def test_save(self):
        """ Save scenes list """
        scenes = self.load_scenes()
        fname = os.path.join(testpath, 'save-test.json')
        scenes.save(fname)
        self.assertTrue(os.path.exists(fname))
        os.remove(fname)
        self.assertFalse(os.path.exists(fname))

    def test_print_summary(self):
        """ Print summary of scenes """
        scenes = self.load_scenes()
        scenes.print_summary()

    def test_dates(self):
        """ Get dates of all scenes """
        scenes = self.load_scenes()
        dates = scenes.dates()
        self.assertEqual(len(dates), 10)

    def test_print_calendar(self):
        """ Print calendar showing dates """
        scenes = self.load_scenes()
        scenes.print_calendar()

    def test_download_thumbnails(self):
        """ Download all thumbnails """
        scenes = self.load_scenes()
        fnames = scenes.download(key='thumb')
        for f in fnames[0].values():
            self.assertTrue(os.path.exists(f))
            os.remove(f)
            self.assertFalse(os.path.exists(f))
        shutil.rmtree(os.path.join(testpath, 'landsat-8'))

    def test_download(self):
        """ Download a data file from all scenes """
        scenes = self.load_scenes()
        dls = scenes.download(key='MTL')
        for s in dls:
            for f in s.values():
                self.assertTrue(os.path.exists(f))
                os.remove(f)
                self.assertFalse(os.path.exists(f))
        shutil.rmtree(os.path.join(testpath, 'landsat-8'))
