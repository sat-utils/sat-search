import json
import os
import logging
import requests

import satsearch.config as config

from satstac import Collection, Item, Items
from satstac.utils import dict_merge


logger = logging.getLogger(__name__)


class SatSearchError(Exception):
    pass


class Search(object):
    """ One search query (possibly multiple pages) """

    search_endpoint = 'stac/search'
    collections_endpoint = 'collections'

    def __init__(self, **kwargs):
        """ Initialize a Search object with parameters """
        self.kwargs = kwargs
        for k in self.kwargs:
            if isinstance(kwargs[k], dict):
                kwargs[k] = json.dumps(kwargs[k])
            if k == 'datetime':
                self.kwargs['time'] = self.kwargs['datetime']
                del self.kwargs['datetime']

    def found(self):
        """ Small query to determine total number of hits """
        kwargs = {
            'page': 1,
            'limit': 0
        }
        kwargs.update(self.kwargs)
        results = self.query(**kwargs)
        return results['meta']['found']

    @classmethod
    def _query(cls, url, **kwargs):
        """ Get request """
        response = requests.get(url, kwargs)
        logger.debug('Query URL: %s' % response.url)
        # API error
        if response.status_code != 200:
            raise SatSearchError(response.text)
        return response.json()

    @classmethod
    def query(cls, **kwargs):
        url = os.path.join(config.API_URL, cls.search_endpoint)
        for k in kwargs:
            if isinstance(kwargs[k], list) and k is not "geometry":
                kwargs[k] = '"%s"' % (','.join(kwargs[k]))
        return cls._query(url, **kwargs)

    @classmethod
    def collection(cls, cid):
        """ Get a Collection record """
        url = os.path.join(config.API_URL, cls.collections_endpoint, cid)
        return Collection(cls._query(url))

    def items(self, limit=1000):
        """ Return all of the Items and Collections for this search """
        items = []
        found = self.found()
        kwargs = {
            'page': 1,
            'limit': min(limit, found)
        }
        kwargs.update(self.kwargs)
        while len(items) < found:
            items += [Item(i) for i in self.query(**kwargs)['features']]
            kwargs['page'] += 1

        # retrieve collections
        collections = []
        for c in set([item.properties['collection'] for item in items if 'collection' in item.properties]):
            collections.append(self.collection(c))
            #del collections[c]['links']

        # merge collections into items
        #_items = []
        #for item in items:
        #    import pdb; pdb.set_trace()
        #    if 'collection' in item['properties']:
        #        item = dict_merge(item, collections[item['properties']['collection']])
        #    _items.append(Item(item))
        
        return Items(items, collections=collections, search=self.kwargs)
