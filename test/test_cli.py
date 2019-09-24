import os
import sys
import unittest
from unittest.mock import patch
import json
import shutil
import satsearch.config as config

from satsearch.cli import main, SatUtilsParser, cli


testpath = os.path.dirname(__file__)
config.DATADIR = testpath


class Test(unittest.TestCase):
    """ Test main module """

    num_scenes = 740

    args = 'search --datetime 2017-01-01 -p eo:cloud_cover=0/20 eo:platform=landsat-8'

    @classmethod
    def get_test_parser(cls):
        """ Get testing parser with search and load subcommands """
        parser = SatUtilsParser.newbie(description='sat-search testing')
        return parser

    def test_empty_parse_args(self):
        """ Parse empty arguments """
        parser = self.get_test_parser()        #import pdb; pdb.set_trace()
        with self.assertRaises(SystemExit):
            args = parser.parse_args([])   

    def test_empty_parse_search_args(self):
        """ Parse empty arguments """
        parser = self.get_test_parser()
        args = parser.parse_args(['search'])
        self.assertEqual(len(args), 3)
        self.assertFalse(args['printcal'])

    def test_parse_args(self):
        """ Parse arguments """
        parser = self.get_test_parser()
        args = self.args.split(' ')
        
        args = parser.parse_args(args)
        self.assertEqual(len(args), 5)
        self.assertEqual(args['datetime'], '2017-01-01')
        #assert(args['eo:cloud_cover'] == '0/20')
        #self.assertEqual(args['cloud_from'], 0)
        #self.assertEqual(args['cloud_to'], 20)
        #self.assertEqual(args['satellite_name'], 'Landsat-8')
        #self.assertEqual(args['dayOrNight'], 'DAY')

    def _test_parse_args_badcloud(self):
        parser = self.get_test_parser()
        with self.assertRaises(ValueError):
            args = parser.parse_args('search --datetime 2017-01-01 --cloud 0.5 eo:platform Landsat-8'.split(' '))

    def test_main(self):
        """ Run main function """
        items = main(datetime='2019-07-01', **{'collection': 'landsat-8-l1'})
        self.assertEqual(len(items), self.num_scenes)

    def test_main_found(self):
        """ Run main function """
        found = main(datetime='2019-07-01', found=True, **{'collection': 'landsat-8-l1'})
        self.assertEqual(found, self.num_scenes)

    def test_main_load(self):
        items = main(items=os.path.join(testpath, 'scenes.geojson'))
        assert(len(items) == 2)

    def test_main_options(self):
        """ Test main program with output options """
        fname = os.path.join(testpath, 'test_main-save.json')
        items = main(datetime='2019-07-01', save=fname, printcal=True, printmd=[], property=['eo:platform=landsat-8'])
        self.assertEqual(len(items), self.num_scenes)
        self.assertTrue(os.path.exists(fname))
        os.remove(fname)
        self.assertFalse(os.path.exists(fname))

    def test_cli(self):
        """ Run CLI program """
        with patch.object(sys, 'argv', 'sat-search search --datetime 2017-01-01 --found -p eo:platform=landsat-8'.split(' ')):
            cli()

    def test_cli_intersects(self):
        cmd = 'sat-search search --intersects %s -p eo:platform=landsat-8 --found' % os.path.join(testpath, 'aoi1.geojson')
        with patch.object(sys, 'argv', cmd.split(' ')):
            cli()        

    def test_main_download(self):
        """ Test main program with downloading """
        with open(os.path.join(testpath, 'aoi1.geojson')) as f:
            aoi = json.dumps(json.load(f))
        config.DATADIR = os.path.join(testpath, "${eo:platform}")
        items = main(datetime='2019-06-05/2019-06-21', intersects=aoi, download=['thumbnail', 'MTL'], **{'collection': 'landsat-8-l1'})
        for item in items:
            bname = os.path.splitext(item.get_filename(config.DATADIR))[0]
            assert(os.path.exists(bname + '_thumbnail.jpg'))
            if not os.path.exists(bname + '_MTL.txt'):
                import pdb; pdb.set_trace()
            assert(os.path.exists(bname + '_MTL.txt'))
        shutil.rmtree(os.path.join(testpath,'landsat-8'))
        config.DATADIR = testpath
