import os
import unittest
from satsearch.scene import Scene, SatSceneError
from nose.tools import raises


class TestScene(unittest.TestCase):

    path = os.path.dirname(__file__)

    prefix = {
        'aws_s3': 'http://landsat-pds.s3.amazonaws.com/L8/007/029/LC80070292016240LGN00/LC80070292016240LGN00_',
        'google': 'https://storage.cloud.google.com/gcp-public-data-landsat/LC08/01/007/029/'
                  'LC08_L1TP_007029_20160827_20170321_01_T1/LC08_L1TP_007029_20160827_20170321_01_T1_'
    }

    md = {
        'scene_id': 'testscene',
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
        self.assertEqual(scene.download_sources, self.md['download_links'].keys())

    def test_download_links(self):
        """ Get links for download """
        scene = self.get_test_scene()
        links = scene.download_links()
        self.assertEqual(links['B1'], self.md['download_links']['aws_s3'][0])

    def test_get_thumbnail(self):
        """ Get thumbnail for scene """
        scene = self.get_test_scene()
        fname = scene.get_thumbnail(path=self.path)
        self.assertTrue(os.path.exists(fname))
        os.remove(fname)
        self.assertFalse(os.path.exists(fname))

    def test_get(self):
        """ Retrieve a data file """
        scene = self.get_test_scene()
        fname = scene.get('MTL', path=self.path)
        self.assertTrue(os.path.exists(fname))
        os.remove(fname)
        self.assertFalse(os.path.exists(fname))

    def test_get_all(self):
        """ Retrieve all data files from a source """
        scene = self.get_test_scene()
        fnames = scene.get_all(source='test', path=self.path)
        for f in fnames.values():
            self.assertTrue(os.path.exists(f))
            os.remove(f)
            self.assertFalse(os.path.exists(f))
