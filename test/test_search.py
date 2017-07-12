import os
import glob
import json
import unittest
from satsearch.scene import Scene
from satsearch.search import Search
from nose.tools import set_trace

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
        return {s: Search(scene_id=self.results[s]['results'][0]['scene_id'], limit=1) for s in self.results}

    def _test_results(self):

        r = Results(query={},
                    found=1,
                    limit=1,
                    page=1)

        self.assertEqual(r.returned, 0)
        self.assertEqual(r.found, 1)
        self.assertEqual(r.query, {})

        r.add(Scene(
            scene_id='some scene',
            satellite_name='landsat',
            cloud_coverage=10,
            date='2016-01-01',
            thumbnail='http://example.com/test.jpg',
            data_geometry={},
            **{'extra': 'meta'}
        ))

        self.assertEqual(r.returned, 1)

        scene = r.scenes[0]

        self.assertTrue(isinstance(scene, Scene))
        self.assertEqual(scene.scene_id, 'some scene')
        self.assertEqual(scene.metadata['extra'], 'meta')

    def test_search_init(self):
        """ Initialize a search object """
        for s, search in self.get_searches().items():
            self.assertEqual(search.kwargs['scene_id'], self.results[s]['results'][0]['scene_id'])

    def test_simple_search(self):
        """ Perform simple query """
        for search in self.get_searches().values():
            results = search.query()
            self.assertEqual(results.found, 1)
            self.assertTrue(isinstance(results.scenes[0], Scene))

    def test_empty_search(self):
        """ Perform search for 0 results """
        search = Search(scene_id='nosuchscene')
        results = search.query()
        self.assertEqual(search.found, 0)

        # search sentinel scene
        #query = {'scene_id': 'S2A_tile_20160418_36UUA_0', 'limit': 1}
        #r = Search.query(**query)

        #self.assertEqual(r.returned, 1)
        #self.assertEqual(r.found, 1)
        #self.assertEqual(r.query, query)
        #self.assertTrue(isinstance(r.scenes[0], Scene))

        # search for something that doesn't exist
        #query = {'scene_id': 'some unknown scene', 'limit': 1}
        #with self.assertRaises(SatSearchError):
        #    r = Search.query(**query)
