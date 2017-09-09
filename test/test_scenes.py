import os
import unittest
import shutil
from satsearch import Scene, Scenes
import satsearch.config as config


class TestScenes(unittest.TestCase):

    path = os.path.dirname(__file__)

    @classmethod
    def setUpClass(cls):
        """ Configure testing class """
        config.DATADIR = cls.path

    def load_scenes(self):
        return Scenes.load(os.path.join(self.path, 'scenes.geojson'))

    def test_load(self):
        """ Initialize Scenes with list of Scene objects """
        scenes = self.load_scenes()
        self.assertEqual(len(scenes), 10)
        self.assertTrue(isinstance(scenes[0], Scene))
        self.assertEqual(len(scenes.sensors()), 1)

    def test_save(self):
        """ Save scenes list """
        scenes = self.load_scenes()
        fname = os.path.join(self.path, 'save-test.json')
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
        self.assertEqual(len(dates), 10)

    def test_text_calendar(self):
        """ Get calendar """
        scenes = self.load_scenes()
        cal = scenes.text_calendar()
        self.assertTrue(len(cal) > 250)

    def test_download_thumbnails(self):
        """ Download all thumbnails """
        scenes = self.load_scenes()
        fnames = scenes.download(key='thumb')
        for f in fnames[0].values():
            self.assertTrue(os.path.exists(f))
            os.remove(f)
            self.assertFalse(os.path.exists(f))
        shutil.rmtree(os.path.join(self.path, 'landsat-8'))

    def test_download(self):
        """ Download a data file from all scenes """
        scenes = self.load_scenes()
        dls = scenes.download(key='MTL')
        for s in dls:
            for f in s.values():
                self.assertTrue(os.path.exists(f))
                os.remove(f)
                self.assertFalse(os.path.exists(f))
        shutil.rmtree(os.path.join(self.path, 'landsat-8'))
