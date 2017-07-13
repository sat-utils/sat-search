import unittest
import satsearch.main as main


class TestMain(unittest.TestCase):
    """ Test main module """

    def test_empty_parse_args(self):
        """ Parse arguments """
        args = main.parse_args([])
        self.assertEqual(len(args), 2)
        self.assertFalse(args['printcal'])
        self.assertFalse(args['save'])

    def test_parse_args(self):
        """ Parse arguments """
        args = main.parse_args('--date 2017-01-01 --satellite_name Landsat-8'.split(' '))
        self.assertEqual(len(args), 4)
        self.assertEqual(args['date'], '2017-01-01')
        self.assertEqual(args['satellite_name'], 'Landsat-8')

    def test_main(self):
        """ Run main function """
        scenes = main.main(date='2017-01-01')
        self.assertEqual(len(scenes), 4279)
