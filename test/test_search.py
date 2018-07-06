import os
import glob
import json
import unittest
from satsearch.scene import Scene
from satsearch.search import SatSearchError, Query, Search


class TestQuery(unittest.TestCase):

    path = os.path.dirname(__file__)
    results = {}
    num_landsat = 558
    num_sentinel = 3854

    @classmethod
    def setUpClass(cls):
        fnames = glob.glob(os.path.join(cls.path, '*-response.json'))
        for fname in fnames:
            with open(fname) as f:
                cls.results[os.path.basename(fname)[:-14]] = json.load(f)

    def get_queries(self):
        """ Initialize and return search object """
        return {s: Query(id=self.results[s]['features'][0]['properties']['id']) for s in self.results}

    def test_search_init(self):
        """ Initialize a search object """
        for s, search in self.get_queries().items():
            self.assertEqual(search.kwargs['id'], self.results[s]['features'][0]['properties']['id'])

    def test_hits(self):
        """ Check total number of results """
        search = Query(datetime='2017-01-01')
        hits = search.found()
        self.assertEqual(hits, 4412)
        #self.assertEqual(hits, 4267)

    def test_empty_search(self):
        """ Perform search for 0 results """
        search = Query(id='nosuchscene')
        self.assertEqual(search.found(), 0)

    def test_bad_search(self):
        """ Run a bad query """
        q = Query(limit='a')
        with self.assertRaises(SatSearchError):
            q.found()

    def test_simple_search(self):
        """ Perform simple query """
        for search in self.get_queries().values():
            self.assertEqual(search.found(), 1)
            scenes = search.items()
            assert(isinstance(scenes, list))
            assert(isinstance(scenes[0], dict))

    def test_big_landsat_search(self):
        """ Search for a bunch of Landsat data """
        search = Query(**{'datetime': '2017-01-01', 'eo:platform': 'landsat-8'})
        self.assertEqual(search.found(), self.num_landsat)
        
        scenes = search.items()
        
        self.assertEqual(len(scenes), self.num_landsat)
        # verify this is 564 unique scenes (it is not)
        #ids = set([s.scene_id for s in scenes])
        #self.assertEqual(len(ids), self.num_landsat)

    def test_big_sentinel_search(self):
        """ Search for a bunch of Sentinel data """
        search = Query(**{'datetime': '2017-01-01', 'eo:platform': 'sentinel-2a'})
        self.assertEqual(search.found(), self.num_sentinel)
        scenes = search.items()
        self.assertEqual(len(scenes), self.num_sentinel)


class TestSearch(unittest.TestCase):

    path = os.path.dirname(__file__)
    results = {}

    @classmethod
    def setUpClass(cls):
        fnames = glob.glob(os.path.join(cls.path, '*-response.json'))
        for fname in fnames:
            with open(fname) as f:
                cls.results[os.path.basename(fname)[:-14]] = json.load(f)

    def get_search(self):
        """ Initialize and return search object """
        sids = [self.results[s]['features'][0]['properties']['id'] for s in self.results]
        return Search(id=sids)

    def test_search_init(self):
        """ Initialize a search object """
        search = self.get_search()
        sids = [self.results[s]['features'][0]['properties']['id'] for s in self.results]
        for s in search.scenes():
            self.assertTrue(s.id in sids)

    def test_empty_search(self):
        """ Perform search for 0 results """
        search = Search(id=['nosuchscene'])
        self.assertEqual(search.found(), 0)

    def test_search(self):
        """ Perform simple query """
        with open(os.path.join(self.path, 'aoi1.geojson')) as f:
            aoi = json.dumps(json.load(f))
        search = Search(datetime='2017-01-05', intersects=aoi)
        self.assertEqual(search.found(), 1)
        scenes = search.scenes()
        self.assertTrue(isinstance(scenes[0], Scene))
