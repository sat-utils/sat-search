import os
import unittest
from satsearch.scene import Scene, SatSceneError
from nose.tools import raises


class TestScene(unittest.TestCase):

    path = os.path.dirname(__file__)

    md = {
        'scene_id': 'testscene',
        'date': '2017-01-01',
        'data_geometry': {},
        'thumbnail': 'http://earthexplorer.usgs.gov/browse/landsat_8/2016/007/029/LC08_L1TP_007029_20160827_20170321_01_T1.jpg',
        'download_links': {
            'aws_s3': []
        }
    }

    def get_test_scene(self):
        """ Get valid test scene """
        return Scene(**self.md)

    @raises(SatSceneError)
    def test_invalid_init(self):
        """ Initialize a scene with insufficient metadata """
        scene = Scene(meaninglesskwarg='meaninglessstring')

    def test_init(self):
        """ Initialize a scene """
        scene = self.get_test_scene()
        self.assertEqual(scene.date, self.md['date'])
        self.assertEqual(scene.scene_id, self.md['scene_id'])
        self.assertEqual(scene.geometry, self.md['data_geometry'])
        self.assertEqual(scene.download_sources, self.md['download_links'].keys())

    def test_get_thumbnail(self):
        """ Get thumbnail for scene """
        scene = self.get_test_scene()
        fname = scene.get_thumbnail(path=self.path)
        self.assertTrue(os.path.exists(fname))
