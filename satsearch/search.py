import collections
import os
import logging
import requests
import satsearch.config as config
from satsearch.scene import Scene, Scenes


logger = logging.getLogger(__name__)


class SatSearchError(Exception):
    pass


# from https://gist.github.com/angstwad/bf22d1822c38a92ec0a9#gistcomment-2622319
def dict_merge(dct, merge_dct, add_keys=True):
    """ Recursive dict merge. Inspired by :meth:``dict.update()``, instead of
    updating only top-level keys, dict_merge recurses down into dicts nested
    to an arbitrary depth, updating keys. The ``merge_dct`` is merged into
    ``dct``.

    This version will return a copy of the dictionary and leave the original
    arguments untouched.

    The optional argument ``add_keys``, determines whether keys which are
    present in ``merge_dict`` but not ``dct`` should be included in the
    new dict.

    Args:
        dct (dict) onto which the merge is executed
        merge_dct (dict): dct merged into dct
        add_keys (bool): whether to add new keys

    Returns:
        dict: updated dict
    """
    dct = dct.copy()
    if not add_keys:
        merge_dct = {
            k: merge_dct[k]
            for k in set(dct).intersection(set(merge_dct))
        }

    for k, v in merge_dct.items():
        if (k in dct and isinstance(dct[k], dict)
                and isinstance(merge_dct[k], collections.Mapping)):
            dct[k] = dict_merge(dct[k], merge_dct[k], add_keys=add_keys)
        else:
            dct[k] = merge_dct[k]

    return dct


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

    def query(self, **kwargs):
        """ Make single API call """
        kwargs.update(self.kwargs)
        url = os.path.join(config.API_URL, self.endpoint)
        response = requests.get(url, kwargs)

        logger.debug('Query URL: %s' % response.url)

        # API error
        if response.status_code != 200:
            raise SatSearchError(response.text)

        self.results = response.json()
        logger.debug(self.results['properties'])
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

    def scenes(self):
        """ Return all of the scenes """
        items = []
        for query in self.queries:
            items += query.items()
        # retrieve collections
        collections = {}
        for c in set([item['properties']['cx:id'] for item in items if 'cx:id' in item['properties']]):
            q = Query(**{"cx:id": c}, endpoint='collections')
            col = q.items()[0]
            collections[col['properties']['cx:id']] = col
        scenes = []
        for item in items:
            if 'cx:id' in item['properties']:
                item = dict_merge(item, collections[item['properties']['cx:id']])
            scenes.append(Scene(item))
        return scenes

    def collections(self):
        """ Search collections """
        collections = []
        for query in self.queries:
            collections += query.collections()
        return collections
