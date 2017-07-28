import os
import sys
import unittest
from mock import patch
import json
import shutil
import satsearch.main as main


testpath = os.path.dirname(__file__)


class Test(unittest.TestCase):
    """ Test main module """

    args = '--date 2017-01-01 --satellite_name Landsat-8'.split(' ')

    def test_empty_parse_args(self):
        """ Parse arguments """
        args = main.parse_args([])
        self.assertEqual(len(args), 5)
        self.assertFalse(args['printsum'])
        self.assertFalse(args['printcal'])

    def test_parse_args(self):
        """ Parse arguments """
        args = main.parse_args(self.args)
        self.assertEqual(len(args), 7)
        self.assertEqual(args['date'], '2017-01-01')
        self.assertEqual(args['satellite_name'], 'Landsat-8')

    def test_parse_args_with_geojson(self):
        """ Test parsing of arguments with geojson file input """
        args = ('--intersects %s' % os.path.join(testpath, 'aoi1.geojson')).split(' ')
        args = main.parse_args(args)
        aoi = json.loads(args['intersects'])
        self.assertEqual(aoi['type'], 'Feature')

    def test_main(self):
        """ Run main function """
        scenes = main.main(date='2017-01-01', satellite_name='Landsat-8')
        self.assertEqual(len(scenes.scenes), 564)

    def test_main_options(self):
        """ Test main program with output options """
        fname = os.path.join(testpath, 'test_main-save.json')
        scenes = main.main(date='2017-01-01', satellite_name='Landsat-8', save=fname, printcal=True, printsum=True)
        self.assertEqual(len(scenes.scenes), 564)
        self.assertTrue(os.path.exists(fname))
        os.remove(fname)
        self.assertFalse(os.path.exists(fname))

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
                           intersects=aoi, download=['thumb', 'MTL'], datadir=testpath)

        self.assertEqual(len(scenes), 2)
        for scene in scenes.scenes:
            self.assertTrue(os.path.exists(scene.filenames['thumb']))
            self.assertTrue(os.path.exists(scene.filenames['MTL']))
        shutil.rmtree(os.path.join(testpath, scene.platform))
