import logging
import requests
import satsearch.config as config
from satsearch.scene import Scene


logger = logging.getLogger(__name__)


class SatSearchError(Exception):
    pass


class Search(object):
    """ A single search to sat-api """

    def __init__(self, **kwargs):
        """ Initialize a query object with parameters """
        self.kwargs = kwargs
        self.results = None

    def found(self):
        """ Small query to determine total number of hits """
        if self.results is None:
            self.query(limit=0)
        return self.results['meta']['found']

    def query(self, **kwargs):
        """ Make single query """
        kwargs.update(self.kwargs)
        response = requests.get(config.SAT_API, kwargs)

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
