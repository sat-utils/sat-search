import os
import unittest
from satsearch.parser import SatUtilsParser


testpath = os.path.dirname(__file__)


class Test(unittest.TestCase):
    """ Test main module """

    args = '--datetime 2017-01-01 --eo:cloud_cover 0/20 -p eo:platform=landsat-8'

    def test_empty_parse_args(self):
        """ Parse empty arguments """
        parser = SatUtilsParser()
        args = parser.parse_args([])
        self.assertEqual(len(args), 5)
        self.assertFalse(args['printsearch'])
        self.assertFalse(args['printcal'])

    def test_parse_args(self):
        """ Parse arguments """
        parser = SatUtilsParser()
        args = self.args.split(' ')
        args = parser.parse_args(args)
        self.assertEqual(len(args), 11)
        self.assertEqual(args['datetime'], '2017-01-01')
        assert(args['eo:cloud_cover'] == '0/20')
        #self.assertEqual(args['cloud_from'], 0)
        #self.assertEqual(args['cloud_to'], 20)
        #self.assertEqual(args['satellite_name'], 'Landsat-8')
        #self.assertEqual(args['dayOrNight'], 'DAY')

    def test_parse_args_badcloud(self):
        parser = SatUtilsParser()
        with self.assertRaises(ValueError):
            args = parser.parse_args('search --datetime 2017-01-01 --cloud 0.5 eo:platform Landsat-8'.split(' '))
