import os
import sys
import unittest
from unittest.mock import patch
import json
import shutil

from satsearch.cli import main, SatUtilsParser, cli


testpath = os.path.dirname(__file__)


class Test(unittest.TestCase):
    """ Test main module """

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
        self.assertEqual(len(args), 4)
        self.assertFalse(args['found'])

    def test_parse_args(self):
        """ Parse arguments """
        parser = self.get_test_parser()
        args = 'search --datetime 2017-01-01 -q eo:cloud_cover<10 platform=sentinel-2a'.split(' ')
        
        args = parser.parse_args(args)
        self.assertEqual(len(args), 6)
        self.assertEqual(args['datetime'], '2017-01-01')
        #assert(args['eo:cloud_cover'] == '0/20')
        #self.assertEqual(args['cloud_from'], 0)
        #self.assertEqual(args['cloud_to'], 20)
        #self.assertEqual(args['satellite_name'], 'Landsat-8')
        #self.assertEqual(args['dayOrNight'], 'DAY')

    def _test_parse_args_badcloud(self):
        parser = self.get_test_parser()
        with self.assertRaises(ValueError):
            args = parser.parse_args('search --datetime 2017-01-01 -q platform=sentinel-2a'.split(' '))

    def test_main(self):
        """ Run main function """
        items = main(datetime='2020-01-01', collections=['sentinel-s2-l1c'], query=['eo:cloud_cover=0', 'data_coverage>80'])
        self.assertEqual(len(items), 207)

    def test_main_found(self):
        """ Run main function """
        found = main(datetime='2019-07-01', found=True)
        self.assertEqual(found, 24737)

    def test_main_load(self):
        items = main(items=os.path.join(testpath, 'scenes.geojson'))
        assert(len(items) == 2)

    def test_main_options(self):
        """ Test main program with output options """
        fname = os.path.join(testpath, 'test_main-save.json')
        items = main(datetime='2020-01-01', save=fname, printcal=True, printmd=[],
                     collections=['sentinel-s2-l2a'], query=['eo:cloud_cover=0', 'data_coverage>80'])
        self.assertEqual(len(items), 212)
        self.assertTrue(os.path.exists(fname))
        os.remove(fname)
        self.assertFalse(os.path.exists(fname))

    def test_cli(self):
        """ Run CLI program """
        with patch.object(sys, 'argv', 'sat-search search --datetime 2017-01-01 --found -q platform=sentinel-2b'.split(' ')):
            cli()

    def test_cli_intersects(self):
        cmd = 'sat-search search --intersects %s -q platform=sentinel-2b --found' % os.path.join(testpath, 'aoi1.geojson')
        with patch.object(sys, 'argv', cmd.split(' ')):
            cli()        

    def test_main_download(self):
        """ Test main program with downloading """
        with open(os.path.join(testpath, 'aoi1.geojson')) as f:
            aoi = json.load(f)
        filename_template = os.path.join(testpath, "test-download/${platform}/${id}")
        items = main(datetime='2020-06-07', intersects=aoi['geometry'],
                     filename_template=filename_template, download=['thumbnail', 'info'], **{'collections': ['sentinel-s2-l1c']})
        for item in items:
            bname = os.path.splitext(item.get_path(filename_template))[0]
            assert(os.path.exists(bname + '_thumbnail.jpg'))
            assert(os.path.exists(bname + '_info.json'))
        #shutil.rmtree(os.path.join(testpath,'landsat-8'))
