import os
import glob
import json
import unittest
from satsearch.scene import Scene
from satsearch.search import Search


class TestSearch(unittest.TestCase):

    path = os.path.dirname(__file__)
    results = {}

    @classmethod
    def setUpClass(cls):
        fnames = glob.glob(os.path.join(cls.path, '*.json'))
        for fname in fnames:
            with open(fname) as f:
                cls.results[os.path.basename(fname)[:-14]] = json.load(f)

    def get_searches(self):
        """ Initialize and return search object """
        return {s: Search(scene_id=self.results[s]['results'][0]['scene_id']) for s in self.results}

    def test_search_init(self):
        """ Initialize a search object """
        for s, search in self.get_searches().items():
            self.assertEqual(search.kwargs['scene_id'], self.results[s]['results'][0]['scene_id'])

    def test_hits(self):
        """ Check total number of results """
        search = Search(date='2017-01-01')
        hits = search.found()
        self.assertEqual(hits, 4279)

    def test_empty_search(self):
        """ Perform search for 0 results """
        search = Search(scene_id='nosuchscene')
        search.query()
        self.assertEqual(search.found(), 0)

    def test_simple_search(self):
        """ Perform simple query """
        for search in self.get_searches().values():
            search.query()
            self.assertEqual(search.found(), 1)
            self.assertTrue(isinstance(search.scenes[0], Scene))

    def test_big_landsat_search(self):
        """ Search for a bunch of Landsat data """
        search = Search(date='2017-01-01', satellite_name='Landsat-8')
        self.assertEqual(search.found(), 564)
        search.query(limit=-1)
        self.assertEqual(len(search.scenes), 564)
        # verify this is 564 unique scenes
        ids = set([s.scene_id for s in search.scenes])
        self.assertEqual(len(ids), 564)

    def test_big_sentinel_search(self):
        """ Search for a bunch of Sentinel data """
        search = Search(date='2017-01-01', satellite_name='Sentinel-2A')
        self.assertEqual(search.found(), 3715)
        search.query(limit=-1)
        self.assertEqual(len(search.scenes), 3715)
