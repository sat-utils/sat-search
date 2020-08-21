import json
import os
import logging
import requests

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

    def __init__(self, url=os.getenv('STAC_API_URL', None), **kwargs):
        """ Initialize a Search object with parameters """
        if url is None:
            raise SatSearchError("URL not provided, pass into Search or define STAC_API_URL environment variable")
        self.url = url.rstrip("/") + "/"
        self.kwargs = kwargs
        self.limit = int(self.kwargs['limit']) if 'limit' in self.kwargs else None

    @classmethod
    def search(cls, headers=None, **kwargs):
        if 'query' in kwargs and isinstance(kwargs['query'], list):
            queries = {}
            for q in kwargs['query']:
                for s in Search.search_op_list:
                    parts = q.split(s)
                    if len(parts) == 2:
                        queries = dict_merge(queries, {parts[0]: {Search.search_op_to_stac_op[s]: parts[1]}})
                        break
            kwargs['query'] = queries
        directions = {'-': 'desc', '+': 'asc'}
        if 'sortby' in kwargs and isinstance(kwargs['sortby'], list):
            sorts = []
            for a in kwargs['sortby']:
                if a[0] not in directions:
                    a = '+' + a
                sorts.append({
                    'field': a[1:],
                    'direction': directions[a[0]]
                })
            kwargs['sortby'] = sorts
        return Search(**kwargs)

    def found(self, headers=None):
        """ Small query to determine total number of hits """
        kwargs = {
            'limit': 0
        }
        kwargs.update(self.kwargs)
        url = urljoin(self.url, 'search')
        
        results = self.query(url=url, headers=headers, **kwargs)
        # TODO - check for status_code
        logger.debug(f"Found: {json.dumps(results)}")
        found = 0
        if 'context' in results:
            found = results['context']['matched']
        elif 'numberMatched' in results:
            found = results['numberMatched']
        return found

    def query(self, url=None, headers=None, **kwargs):
        """ Get request """
        url = url or urljoin(self.url, 'search')
        logger.debug('Query URL: %s, Body: %s' % (url, json.dumps(kwargs)))
        response = requests.post(url, json=kwargs, headers=headers)
        logger.debug(f"Response: {response.text}")
        # API error
        if response.status_code != 200:
            raise SatSearchError(response.text)
        return response.json()

    def collection(self, cid, headers=None):
        """ Get a Collection record """
        url = urljoin(self.url, 'collections/%s' % cid)
        return Collection(self.query(url=url, headers=headers))

    def items(self, limit=10000, page_limit=500, headers=None):
        """ Return all of the Items and Collections for this search """
        found = self.found(headers=headers)
        limit = self.limit or limit
        if found > limit:
            logger.warning('There are more items found (%s) than the limit (%s) provided.' % (found, limit))

        nextlink = {
            'method': 'POST',
            'href': urljoin(self.url, 'search'),
            'headers': headers,
            'body': self.kwargs,
            'merge': False
        }

        items = []
        while nextlink and len(items) < limit:
            if nextlink.get('method', 'GET') == 'GET':
                resp = self.query(url=nextlink['href'], headers=headers, **self.kwargs)
            else:
                _headers = nextlink.get('headers', {})
                _body = nextlink.get('body', {})
                _body.update({'limit': page_limit})
                
                if nextlink.get('merge', False):
                    _headers.update(headers)
                    _body.update(self.kwargs)
                resp = self.query(url=nextlink['href'], headers=_headers, **_body)
            items += [Item(i) for i in resp['features']]
            links = [l for l in resp['links'] if l['rel'] == 'next']
            nextlink = links[0] if len(links) == 1 else None

        # retrieve collections
        collections = []
        try:
            for c in set([item._data['collection'] for item in items if 'collection' in item._data]):
                collections.append(self.collection(c, headers=headers))
                #del collections[c]['links']
        except:
            pass
        logger.debug(f"Found: {len(items)}")
        return ItemCollection(items, collections=collections)
