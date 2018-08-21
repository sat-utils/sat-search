import json
import os
import logging
import requests
import satsearch.config as config
from satsearch.scene import Scene, Scenes
from satsearch.utils import dict_merge


logger = logging.getLogger(__name__)


class SatSearchError(Exception):
    pass


class Query(object):
    """ One search query (possibly multiple pages) """

    def __init__(self, endpoint='search/stac', **kwargs):
        """ Initialize a Query object with parameters """
        self.endpoint = endpoint
        self.kwargs = kwargs
        self.results = None

    def found(self):
        """ Small query to determine total number of hits """
        if self.results is None:
            self.query(limit=0)
        return self.results['properties']['found']

    @classmethod
    def _query(cls, url,**kwargs):
        for k in kwargs:
            if isinstance(kwargs[k], list) and k is not "geometry":
                kwargs[k] = '"%s"' % (','.join(kwargs[k]))
        
        response = requests.get(url, kwargs)
        logger.debug('Query URL: %s' % response.url)
        # API error
        if response.status_code != 200:
            raise SatSearchError(response.text)
        return response.json()

    def query(self, **kwargs):
        """ Make single API call """
        kwargs.update(self.kwargs)
        url = os.path.join(config.API_URL, self.endpoint)
        self.results = self._query(url, **kwargs)
        return self.results

    def items(self, limit=None):
        """ Query and return up to limit results """
        if limit is None:
            limit = self.found()
        limit = min(limit, self.found())
        # split into multiple pages to retrieve
        page_size = min(limit, 1000)
        items = []
        page = 1
        while len(items) < limit:
            results = self.query(page=page, limit=page_size)['features']
            items += results
            #for r in results:
            #    items.append(Scene(r))
            page += 1

        return items


class Search(object):
    """ Search the API with multiple queries and combine """

    def __init__(self, id=[], **kwargs):
        """ Initialize a Search object with parameters """
        self.kwargs = kwargs
        for k in self.kwargs:
            if isinstance(kwargs[k], dict):
                kwargs[k] = json.dumps(kwargs[k])
        self.queries = []
        if len(id) == 0:
            self.queries.append(Query(**kwargs))
        else:
            for s in id:
                kwargs.update({'id': s})
                self.queries.append(Query(**kwargs))

    def found(self):
        """ Total number of found scenes """
        found = 0
        for query in self.queries:
            found += query.found()
        return found

    @classmethod
    def collection(cls, cid):
        """ Get a Collection record """
        url = os.path.join(config.API_URL, 'collections', cid, 'definition')
        return Query._query(url)['features'][0]

    def scenes(self):
        """ Return all of the scenes """
        items = []
        for query in self.queries:
            items += query.items()
        # retrieve collections
        collections = {}
        for c in set([item['properties']['c:id'] for item in items if 'c:id' in item['properties']]):
            collections[c] = self.collection(c)
            del collections[c]['links']
        scenes = []
        for item in items:
            if 'c:id' in item['properties']:
                item = dict_merge(item, collections[item['properties']['c:id']])
            scenes.append(Scene(item))
        return scenes

    def collections(self):
        """ Search collections """
        collections = []
        for query in self.queries:
            collections += query.collections()
        return collections
