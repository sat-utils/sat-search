

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
