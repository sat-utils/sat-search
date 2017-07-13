import os
import sys
import unittest
from mock import patch
import satsearch.main as main


testpath = os.path.dirname(__file__)


class TestMain(unittest.TestCase):
    """ Test main module """

    args = '--date 2017-01-01 --satellite_name Landsat-8'.split(' ')

    def test_empty_parse_args(self):
        """ Parse arguments """
        args = main.parse_args([])
        self.assertEqual(len(args), 2)
        self.assertFalse(args['printsum'])
        self.assertFalse(args['printcal'])

    def test_parse_args(self):
        """ Parse arguments """
        args = main.parse_args(self.args)
        self.assertEqual(len(args), 4)
        self.assertEqual(args['date'], '2017-01-01')
        self.assertEqual(args['satellite_name'], 'Landsat-8')

    def test_main(self):
        """ Run main function """
        scenes = main.main(date='2017-01-01', satellite_name='Landsat-8')
        self.assertEqual(len(scenes), 564)

    def test_main_options(self):
        fname = os.path.join(testpath, 'test_main-save.json')
        scenes = main.main(date='2017-01-01', satellite_name='Landsat-8', save=fname, printcal=True, printsum=True)
        self.assertEqual(len(scenes), 564)
        self.assertTrue(os.path.exists(fname))
        os.remove(fname)
        self.assertFalse(os.path.exists(fname))

    def test_cli(self):
        """ Run CLI program """
        with patch.object(sys, 'argv', ['testprog'] + self.args):
            n = main.cli()
            self.assertEqual(n, 564)
