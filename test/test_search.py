import os
import glob
import json
import unittest

import satsearch.config as config

from satstac import Item
from satsearch.search import SatSearchError, Search


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
        assert('time' in search.kwargs)
        for kw in search.kwargs:
            self.assertTrue(search.kwargs[kw] in dts)

    def test_search_for_items_by_date(self):
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
            aoi = json.dumps(json.load(f))
        search = Search(datetime='2019-07-01', intersects=aoi)
        assert(search.found() == 13)
        items = search.items()
        assert(len(items) == 13)
        assert(isinstance(items[0], Item))

    def test_search_sort(self):
        """ Perform search with sort """
        with open(os.path.join(self.path, 'aoi1.geojson')) as f:
            aoi = json.dumps(json.load(f))
        search = Search.search(datetime='2019-07-01/2019-07-07', intersects=aoi, sort=['<datetime'])
        items = search.items()
        assert(len(items) == 27)

    def test_get_items_by_id(self):
        """ Get Items by ID """
        ids = ['LC81692212019263', 'LC81691102019263']
        items = Search.items_by_id(ids, collection='landsat-8-l1')
        assert(len(items) == 2)

    def test_get_ids_search(self):
        """ Get Items by ID through normal search """
        ids = ['LC81692212019263', 'LC81691102019263']
        search = Search.search(ids=ids, collection='landsat-8-l1')
        items = search.items()
        assert(search.found() == 2)
        assert(len(items) == 2)

    def test_get_ids_without_collection(self):
        with self.assertRaises(SatSearchError):
            search = Search.search(ids=['LC80340332018034LGN00'])
            items = search.items()

    def test_query_bad_url(self):
        with self.assertRaises(SatSearchError):
            Search.query(url=os.path.join(config.API_URL, 'collections/nosuchcollection'))

    def test_search_property_operator(self):
        expected = {'query': {'eo:cloud_cover': {'lte': '10'}, 'collection': {'eq': 'sentinel-2-l1c'}}}
        instance = Search.search(collection='sentinel-2-l1c',
                                 property=['eo:cloud_cover<=10'])
        actual = instance.kwargs
        assert actual == expected
