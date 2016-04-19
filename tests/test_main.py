import unittest

from ssearch import Results, Scene, Search, SatSearchError


class Tests(unittest.TestCase):

    def test_results(self):

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

    def test_search_query(self):

        # search landsat scene
        query = {'scene_id': 'LC81230172016109LGN00', 'limit': 1}
        r = Search.query(**query)

        self.assertEqual(r.returned, 1)
        self.assertEqual(r.found, 1)
        self.assertEqual(r.query, query)
        self.assertTrue(isinstance(r.scenes[0], Scene))

        # search sentinel scene
        query = {'scene_id': 'S2A_tile_20160418_36UUA_0', 'limit': 1}
        r = Search.query(**query)

        self.assertEqual(r.returned, 1)
        self.assertEqual(r.found, 1)
        self.assertEqual(r.query, query)
        self.assertTrue(isinstance(r.scenes[0], Scene))

        # search for something that doesn't exist
        query = {'scene_id': 'some unknown scene', 'limit': 1}
        with self.assertRaises(SatSearchError):
            r = Search.query(**query)


if __name__ == '__main__':
    unittest.main()
