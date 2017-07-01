import requests


class SatSearchError(Exception):
    pass


class Scene(object):

    def __init__(self, scene_id, satellite_name, cloud_coverage,
                 date, thumbnail, data_geometry, **kwargs):

        self.scene_id = scene_id
        self.satellite_name = satellite_name
        self.cloud_coverage = cloud_coverage
        self.date = date
        self.thumbnail = thumbnail
        self.data_geometry = data_geometry
        self.metadata = kwargs

    def __repr__(self):
        return self.scene_id


class Results(object):

    def __init__(self, query, found, limit, page, **kwargs):

        self.query = query
        self.found = found
        self.limit = limit
        self.page = page
        self.scenes = []

    @property
    def returned(self):
        return len(self.scenes)

    def add(self, result):
        assert isinstance(result, Scene)
        self.scenes.append(result)

    def __repr__(self):
        return '%s results for %s' % (self.returned, self.query)


class Search(object):

    end_point = 'https://3u27f95avd.execute-api.us-east-1.amazonaws.com/dev/'
    default_limit = 100

    @classmethod
    def query(cls, **kwargs):

        if 'limit' not in kwargs:
            kwargs['limit'] = cls.default_limit

        r = requests.get(cls.end_point, params=kwargs)
        out = r.json()

        if r.status_code != 200:
            raise SatSearchError(out.message)

        if r.status_code == 200:
            meta = out['meta']
            results = Results(kwargs, meta['found'], meta['limit'], meta['page'])

            if results.found > 0:
                for result in out['results']:
                    results.add(Scene(
                        scene_id=result.pop('scene_id'),
                        satellite_name=result.pop('satellite_name'),
                        cloud_coverage=result.pop('cloud_coverage'),
                        date=result.pop('date'),
                        thumbnail=result.pop('thumbnail'),
                        data_geometry=result.pop('data_geometry'),
                        **result
                    ))
            else:
                raise SatSearchError('No results were found')

            return results
