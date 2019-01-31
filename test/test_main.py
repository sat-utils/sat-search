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

    num_scenes = 653

    def test_main(self):
        """ Run main function """
        items = main.main(datetime='2019-01-02', **{'collection': 'landsat-8-l1'})
        self.assertEqual(len(items), self.num_scenes)

    def test_main_found(self):
        """ Run main function """
        found = main.main(datetime='2019-01-02', found=True, **{'collection': 'landsat-8-l1'})
        self.assertEqual(found, self.num_scenes)

    def test_main_load(self):
        items = main.main(items=os.path.join(testpath, 'scenes.geojson'))
        assert(len(items) == 2)

    def test_main_options(self):
        """ Test main program with output options """
        fname = os.path.join(testpath, 'test_main-save.json')
        items = main.main(datetime='2019-01-02', save=fname, printcal=True, printmd=[], property=['eo:platform=landsat-8'])
        self.assertEqual(len(items), self.num_scenes)
        self.assertTrue(os.path.exists(fname))
        os.remove(fname)
        self.assertFalse(os.path.exists(fname))

    def test_cli(self):
        """ Run CLI program """
        with patch.object(sys, 'argv', 'sat-search search --datetime 2017-01-01 --found -p eo:platform=landsat-8'.split(' ')):
            main.cli()

    def test_cli_intersects(self):
        cmd = 'sat-search search --intersects %s -p eo:platform=landsat-8 --found' % os.path.join(testpath, 'aoi1.geojson')
        with patch.object(sys, 'argv', cmd.split(' ')):
            main.cli()        

    def test_main_download(self):
        """ Test main program with downloading """
        with open(os.path.join(testpath, 'aoi1.geojson')) as f:
            aoi = json.dumps(json.load(f))
        config.DATADIR = os.path.join(testpath, "${eo:platform}")
        items = main.main(datetime='2017-01-05/2017-01-21', intersects=aoi, download=['thumbnail', 'MTL'], **{'collection': 'landsat-8-l1'})
        for item in items:
            bname = os.path.splitext(item.get_filename(config.DATADIR))[0]
            assert(os.path.exists(bname + '_thumbnail.jpg'))
            if not os.path.exists(bname + '_MTL.txt'):
                import pdb; pdb.set_trace()
            assert(os.path.exists(bname + '_MTL.txt'))
        shutil.rmtree(os.path.join(testpath,'landsat-8'))
        config.DATADIR = testpath
