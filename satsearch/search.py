import os
import logging
import requests
from satsearch.scene import Scene

logger = logging.getLogger(__name__)


SAT_API = os.getenv('SAT_API', 'https://api.developmentseed.org/satellites')


class SatSearchError(Exception):
    pass


class Search(object):
    """ A single search to sat-api """

    _DEFAULT_LIMIT = 100

    def __init__(self, **kwargs):
        """ Initialize a query object with parameters """
        self.kwargs = kwargs
        self.results = None

    def found(self):
        """ Small query to determine total number of hits """
        if self.results is None:
            self._query(limit=0)
        return self.results['meta']['found']

    def _query(self, **kwargs):
        """ Make single query """
        kwargs.update(self.kwargs)
        response = requests.get(SAT_API, kwargs)

        # API error
        if response.status_code != 200:
            raise SatSearchError(response.message)

        self.results = response.json()
        logger.debug(self.results['meta'])
        return self.results

    def query(self, limit=10):
        """ Query and return up to limit results """
        if limit < 0:
            limit = self.found()
        limit = min(limit, self.found())
        page_size = min(limit, 1000)

        self.scenes = []
        page = 1
        while len(self.scenes) < limit:
            results = self._query(page=page, limit=page_size)['results']

            self.scenes += [Scene(**r) for r in results]
            page += 1

        return self.scenes
