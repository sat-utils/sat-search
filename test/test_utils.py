import os
import unittest
import satsearch.config as config
from satsearch.scene import Scenes


class Test(unittest.TestCase):

    path = os.path.dirname(__file__)

    @classmethod
    def setUpClass(cls):
        """ Configure testing class """
        config.DATADIR = cls.path

    def load_scenes(self):
        return Scenes.load(os.path.join(self.path, 'scenes.geojson'))

    def test_text_calendar(self):
        """ Get calendar """
        scenes = self.load_scenes()
        cal = scenes.text_calendar()
        self.assertEqual(len(cal), 576)
        self.assertTrue(' 2018 ' in cal)
        self.assertTrue(' January ' in cal)
        self.assertTrue(' March ' in cal)

    def test_text_calendar_multiyear(self):
        scenes = self.load_scenes()
        scenes[0].feature['properties']['datetime'] = '2010-02-01T00:00:00.000Z'
        cal = scenes.text_calendar()
        self.assertEqual(len(cal), 16654)
        self.assertTrue(' 2016 ' in cal)
        self.assertTrue(' 2017 ' in cal)
