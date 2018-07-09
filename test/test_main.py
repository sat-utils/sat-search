import os
import sys
import unittest
from unittest.mock import patch
import json
import shutil
import satsearch.main as main
import satsearch.config as config


testpath = os.path.dirname(__file__)
config.DATADIR = testpath


class Test(unittest.TestCase):
    """ Test main module """

    num_scenes = 558

    def test_main(self):
        """ Run main function """
        scenes = main.main(datetime='2017-01-01', **{'c:id': 'Landsat-8-l1'})
        self.assertEqual(len(scenes.scenes), self.num_scenes)

    def test_main_options(self):
        """ Test main program with output options """
        fname = os.path.join(testpath, 'test_main-save.json')
        scenes = main.main(datetime='2017-01-01', save=fname, printcal=True, print_md=[], **{'eo:platform': 'landsat-8'})
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
        with patch.object(sys, 'argv', 'sat-search search --datetime 2017-01-01 -p eo:platform=landsat-8'.split(' ')):
            scenes = main.cli()

    def test_main_download(self):
        """ Test main program with downloading """
        with open(os.path.join(testpath, 'aoi1.geojson')) as f:
            aoi = json.dumps(json.load(f))
        config.DATADIR = os.path.join(testpath, "${eo:platform}")
        scenes = main.main(datetime='2017-01-05/2017-01-21', intersects=aoi, download=['thumbnail', 'MTL'], **{'eo:platform': 'landsat-8'})
        for scene in scenes.scenes:
            self.assertTrue(os.path.exists(scene.filenames['thumbnail']))
            self.assertTrue(os.path.exists(scene.filenames['MTL']))
        shutil.rmtree(os.path.join(testpath, scene['eo:platform']))
        config.DATADIR = testpath
