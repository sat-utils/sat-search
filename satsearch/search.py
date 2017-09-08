import logging
import requests
import satsearch.config as config
from satsearch.scene import Scene


logger = logging.getLogger(__name__)


class SatSearchError(Exception):
    pass


class Query(object):
    """ One search query (possibly multiple pages) """

    def __init__(self, **kwargs):
        """ Initialize a Query object with parameters """
        self.kwargs = kwargs
        self.results = None

    def found(self):
        """ Small query to determine total number of hits """
        if self.results is None:
            self.query(limit=0)
        return self.results['meta']['found']

    def query(self, **kwargs):
        """ Make single API call """
        kwargs.update(self.kwargs)
        response = requests.get(config.SAT_API, kwargs)

        logger.debug('Query URL: %s' % response.url)

        # API error
        if response.status_code != 200:
            raise SatSearchError(response.text)

        self.results = response.json()
        logger.debug(self.results['meta'])
        return self.results

    def scenes(self, limit=None):
        """ Query and return up to limit results """
        if limit is None:
            limit = self.found()
        limit = min(limit, self.found())
        page_size = min(limit, 1000)

        scenes = []
        page = 1
        while len(scenes) < limit:
            results = self.query(page=page, limit=page_size)['results']
            scenes += [Scene(**r) for r in results]
            page += 1

        return scenes


class Search(object):
    """ Search the API with multiple queries and combine """

    def __init__(self, scene_id=[], **kwargs):
        """ Initialize a Search object with parameters """
        self.queries = []
        if len(scene_id) == 0:
            self.queries.append(Query(**kwargs))
        else:
            for s in scene_id:
                kwargs.update({'scene_id': s})
                self.queries.append(Query(**kwargs))

    def found(self):
        """ Total number of found scenes """
        found = 0
        for query in self.queries:
            found += query.found()
        return found

    def scenes(self):
        """ Return all of the scenes """
        scenes = []
        for query in self.queries:
            scenes += query.scenes()
        return scenes
