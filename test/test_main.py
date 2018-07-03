import os
import sys
import unittest
from mock import patch
import json
import shutil
import satsearch.main as main
import satsearch.config as config


testpath = os.path.dirname(__file__)
config.DATADIR = testpath


class Test(unittest.TestCase):
    """ Test main module """

    args = '--date 2017-01-01 --satellite_name Landsat-8'.split(' ')
    num_scenes = 562

    def test_main(self):
        """ Run main function """
        scenes = main.main(date='2017-01-01', collection='Landsat-8-l1')
        import pdb; pdb.set_trace()
        self.assertEqual(len(scenes.scenes), self.num_scenes)

    def test_main_options(self):
        """ Test main program with output options """
        fname = os.path.join(testpath, 'test_main-save.json')
        scenes = main.main(date='2017-01-01', satellite_name='Landsat-8', save=fname, printsearch=True, printcal=True, printmd=[])
        self.assertEqual(len(scenes.scenes), self.num_scenes)
        self.assertTrue(os.path.exists(fname))
        os.remove(fname)
        self.assertFalse(os.path.exists(fname))

    def _test_main_review_error(self):
        """ Run review feature without envvar set """
        #os.setenv('IMGCAT', None)
        with self.assertRaises(ValueError):
            scenes = main.main(date='2017-01-01', satellite_name='Landsat-8', review=True)

    def test_cli(self):
        """ Run CLI program """
        with patch.object(sys, 'argv', ['search'] + self.args):
            n = main.cli()
            self.assertEqual(n, self.num_scenes)

    def test_main_download(self):
        """ Test main program with downloading """
        with open(os.path.join(testpath, 'aoi1.geojson')) as f:
            aoi = json.dumps(json.load(f))
        scenes = main.main(date_from='2017-01-05', date_to='2017-01-21', satellite_name='Landsat-8',
                           intersects=aoi, download=['thumbnail', 'metadata'])
        for scene in scenes.scenes:
            self.assertTrue(os.path.exists(scene.filenames['thumbnail']))
            self.assertTrue(os.path.exists(scene.filenames['metadata']))
        shutil.rmtree(os.path.join(testpath, scene.platform))
