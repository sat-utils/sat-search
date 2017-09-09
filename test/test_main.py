import os
import sys
import unittest
from mock import patch
import json
import shutil
import satsearch.main as main
import satsearch.config as config
from nose.tools import raises


testpath = os.path.dirname(__file__)
config.DATADIR = testpath


class Test(unittest.TestCase):
    """ Test main module """

    args = '--date 2017-01-01 --satellite_name Landsat-8'.split(' ')

    def test_main(self):
        """ Run main function """
        scenes = main.main(date='2017-01-01', satellite_name='Landsat-8')
        self.assertEqual(len(scenes.scenes), 564)

    def test_main_options(self):
        """ Test main program with output options """
        fname = os.path.join(testpath, 'test_main-save.json')
        scenes = main.main(date='2017-01-01', satellite_name='Landsat-8', save=fname, printcal=True, printmd=[])
        self.assertEqual(len(scenes.scenes), 564)
        self.assertTrue(os.path.exists(fname))
        os.remove(fname)
        self.assertFalse(os.path.exists(fname))

    @raises(ValueError)
    def test_main_review_error(self):
        """ Run review feature without envvar set """
        scenes = main.main(date='2017-01-01', satellite_name='Landsat-8', review=True)

    def test_cli(self):
        """ Run CLI program """
        with patch.object(sys, 'argv', ['testprog'] + self.args):
            n = main.cli()
            self.assertEqual(n, 564)

    def test_main_download(self):
        """ Test main program with downloading """
        with open(os.path.join(testpath, 'aoi1.geojson')) as f:
            aoi = json.dumps(json.load(f))
        scenes = main.main(date_from='2017-01-05', date_to='2017-01-21', satellite_name='Landsat-8',
                           intersects=aoi, download=['thumb', 'MTL'])
        for scene in scenes.scenes:
            self.assertTrue(os.path.exists(scene.filenames['thumb']))
            self.assertTrue(os.path.exists(scene.filenames['MTL']))
        shutil.rmtree(os.path.join(testpath, scene.platform))
