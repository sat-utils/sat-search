import json
import os
import logging
import requests

import satsearch.config as config

from satstac import Collection, Item, ItemCollection
from satstac.utils import dict_merge
from urllib.parse import urljoin


logger = logging.getLogger(__name__)


class SatSearchError(Exception):
    pass


class Search(object):
    """ One search query (possibly multiple pages) """
    search_op_list = ['>=', '<=', '=', '>', '<']
    search_op_to_stac_op = {'>=': 'gte', '<=': 'lte', '=': 'eq', '>': 'gt', '<': 'lt'}

    def __init__(self, **kwargs):
        """ Initialize a Search object with parameters """
        self.kwargs = kwargs

    @classmethod
    def search(cls, **kwargs):
        if 'property' in kwargs and isinstance(kwargs['property'], list):
            queries = {}
            for prop in kwargs['property']:
                for s in Search.search_op_list:
                    parts = prop.split(s)
                    if len(parts) == 2:
                        queries = dict_merge(queries, {parts[0]: {Search.search_op_to_stac_op[s]: parts[1]}})
                        break
            del kwargs['property']
            kwargs['query'] = queries
        directions = {'>': 'desc', '<': 'asc'}
        if 'sort' in kwargs and isinstance(kwargs['sort'], list):
            sorts = []
            for a in kwargs['sort']:
                if a[0] not in directions:
                    a = '>' + a
                sorts.append({
                    'field': a[1:],
                    'direction': directions[a[0]]
                })
            del kwargs['sort']
            kwargs['sort'] = sorts
        return Search(**kwargs)

    def found(self):
        """ Small query to determine total number of hits """
        if 'ids' in self.kwargs:
            cid = self.kwargs['query']['collection']['eq']
            return len(self.items_by_id(self.kwargs['ids'], cid))
        kwargs = {
            'page': 1,
            'limit': 0
        }
        kwargs.update(self.kwargs)
        results = self.query(**kwargs)
        logger.debug(f"Found results: {json.dumps(results)}")
        return results['context']['matched']

    @classmethod
    def query(cls, url=urljoin(config.API_URL, 'search'), **kwargs):
        """ Get request """
        logger.debug('Query URL: %s, Body: %s' % (url, json.dumps(kwargs)))
        response = requests.post(url, data=json.dumps(kwargs))
        # API error
        if response.status_code != 200:
            raise SatSearchError(response.text)
        return response.json()

    @classmethod
    def collection(cls, cid):
        """ Get a Collection record """
        url = urljoin(config.API_URL, 'collections/%s' % cid)
        return Collection(cls.query(url=url))

    @classmethod
    def items_by_id(cls, ids, collection):
        """ Return Items from collection with matching ids """
        col = cls.collection(collection)
        items = []
        base_url = urljoin(config.API_URL, 'collections/%s/items/' % collection)
        for id in ids:
            try:
                items.append(Item(cls.query(urljoin(base_url, id))))
            except SatSearchError as err:
                pass
        return ItemCollection(items, collections=[col])

    def items(self, limit=10000):
        """ Return all of the Items and Collections for this search """
        _limit = 500
        if 'ids' in self.kwargs:
            col = self.kwargs.get('query', {}).get('collection', {}).get('eq', None)
            if col is None:
                raise SatSearchError('Collection required when searching by id')
            return self.items_by_id(self.kwargs['ids'], col)

        items = []
        found = self.found()
        if found > limit:
            logger.warning('There are more items found (%s) than the limit (%s) provided.' % (found, limit))
        maxitems = min(found, limit)
        kwargs = {
            'page': 1,
            'limit': min(_limit, maxitems)
        }
        kwargs.update(self.kwargs)
        while len(items) < maxitems:
            items += [Item(i) for i in self.query(**kwargs)['features']]
            kwargs['page'] += 1

        # retrieve collections
        collections = []
        for c in set([item._data['collection'] for item in items if 'collection' in item._data]):
            collections.append(self.collection(c))
            #del collections[c]['links']

        # merge collections into items
        #_items = []
        #for item in items:
        #    import pdb; pdb.set_trace()
        #    if 'collection' in item['properties']:
        #        item = dict_merge(item, collections[item['properties']['collection']])
        #    _items.append(Item(item))

        search = {
            'endpoint': config.API_URL,
            'parameters': self.kwargs
        }
        return ItemCollection(items, collections=collections, search=search)
