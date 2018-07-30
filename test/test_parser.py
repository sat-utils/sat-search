import os
import unittest
from satsearch.parser import SatUtilsParser


testpath = os.path.dirname(__file__)


class Test(unittest.TestCase):
    """ Test main module """

    args = 'search --datetime 2017-01-01 --eo:cloud_cover 0/20 -p eo:platform=landsat-8'

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
        self.assertEqual(len(args), 2)
        self.assertFalse(args['print_cal'])

    def test_parse_args(self):
        """ Parse arguments """
        parser = self.get_test_parser()
        args = self.args.split(' ')
        
        args = parser.parse_args(args)
        self.assertEqual(len(args), 5)
        self.assertEqual(args['datetime'], '2017-01-01')
        assert(args['eo:cloud_cover'] == '0/20')
        #self.assertEqual(args['cloud_from'], 0)
        #self.assertEqual(args['cloud_to'], 20)
        #self.assertEqual(args['satellite_name'], 'Landsat-8')
        #self.assertEqual(args['dayOrNight'], 'DAY')

    def _test_parse_args_badcloud(self):
        parser = self.get_test_parser()
        with self.assertRaises(ValueError):
            args = parser.parse_args('search --datetime 2017-01-01 --cloud 0.5 eo:platform Landsat-8'.split(' '))
