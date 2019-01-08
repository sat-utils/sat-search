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

    num_scenes = 38

    def test_main(self):
        """ Run main function """
        items = main.main(datetime='2019-01-02', **{'collection': 'Landsat-8-l1'})
        self.assertEqual(len(items), self.num_scenes)

    def test_main_options(self):
        """ Test main program with output options """
        fname = os.path.join(testpath, 'test_main-save.json')
        items = main.main(datetime='2019-01-02', save=fname, printcal=True, print_md=[], **{'eo:platform': 'landsat-8'})
        self.assertEqual(len(items), self.num_scenes)
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
            items = main.cli()
            assert(len(items) == 0)

    def test_main_download(self):
        """ Test main program with downloading """
        with open(os.path.join(testpath, 'aoi1.geojson')) as f:
            aoi = json.dumps(json.load(f))
        config.DATADIR = os.path.join(testpath, "${eo:platform}")
        items = main.main(datetime='2017-01-05/2017-01-21', intersects=aoi, download=['thumbnail', 'MTL'], **{'eo:platform': 'landsat-8'})
        for item in items:
            self.assertTrue(os.path.exists(item.filenames['thumbnail']))
            self.assertTrue(os.path.exists(item.filenames['MTL']))
        #shutil.rmtree(os.path.join(testpath, item['eo:platform']))
        config.DATADIR = testpath
