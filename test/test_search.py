import os
import glob
import json
import unittest

from satstac import Item
from satsearch.search import SatSearchError, Search, API_URL


class Test(unittest.TestCase):

    path = os.path.dirname(__file__)
    results = []

    @classmethod
    def setUpClass(cls):
        fnames = glob.glob(os.path.join(cls.path, '*-item*.json'))
        for fname in fnames:
            with open(fname) as f:
                cls.results.append(json.load(f))

    def get_searches(self):
        """ Initialize and return search object """
        return [Search(datetime=r['properties']['datetime']) for r in self.results]

    def test_search_init(self):
        """ Initialize a search object """
        search = self.get_searches()[0]
        dts = [r['properties']['datetime'] for r in self.results]
        
        assert(len(search.kwargs) == 1)
        assert('datetime' in search.kwargs)
        for kw in search.kwargs:
            self.assertTrue(search.kwargs[kw] in dts)

    def _test_search_for_items_by_date(self):
        """ Search for specific item """
        search = self.get_searches()[0]
        sids = [r['id'] for r in self.results]
        items = search.items()
        assert(len(items) == 1)
        for s in items:
            self.assertTrue(s.id in sids)

    def test_empty_search(self):
        """ Perform search for 0 results """
        search = Search(datetime='2001-01-01')
        self.assertEqual(search.found(), 0)

    def test_geo_search(self):
        """ Perform simple query """
        with open(os.path.join(self.path, 'aoi1.geojson')) as f:
            aoi = json.load(f)
        search = Search(datetime='2020-06-07', intersects=aoi['geometry'])
        assert(search.found() == 12)
        items = search.items()
        assert(len(items) == 12)
        assert(isinstance(items[0], Item))

    def test_search_sort(self):
        """ Perform search with sort """
        with open(os.path.join(self.path, 'aoi1.geojson')) as f:
            aoi = json.load(f)
        search = Search.search(datetime='2020-06-07', intersects=aoi['geometry'], sortby=['-properties.datetime'])
        items = search.items()
        assert(len(items) == 12)

    def test_get_ids_search(self):
        """ Get Items by ID through normal search """
        ids = ['S2A_28QBH_20200611_0_L2A', 'S2A_28QCH_20200611_0_L2A']
        search = Search.search(ids=ids)
        items = search.items()
        assert(search.found() == 4)
        assert(len(items) == 4)

    def _test_query_bad_url(self):
        with self.assertRaises(SatSearchError):
            Search.query(url=os.path.join(API_URL, 'collections/nosuchcollection'))

    def test_search_query_operator(self):
        expected = {'collections': ['sentinel-s2-l1c'], 'query': {'eo:cloud_cover': {'lte': '10'}, 'data_coverage': {'gt': '80'}}}
        instance = Search.search(collections=['sentinel-s2-l1c'],
                                 query=['eo:cloud_cover<=10', 'data_coverage>80'])
        assert instance.kwargs == expected
