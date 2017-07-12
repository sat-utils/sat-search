import unittest
import satsearch.main as main


class TestMain(unittest.TestCase):
    """ Test main module """

    def test_parse_args(self):
        """ Parse arguments """
        args = main.parse_args(''.split(' '))
