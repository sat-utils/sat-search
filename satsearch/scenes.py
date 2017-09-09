import json
from satsearch.scene import Scene
import satsearch.utils as utils


class Scenes(object):
    """ A collection of Scene objects """

    def __init__(self, scenes):
        """ Initialize with a list of Scene objects """
        self.scenes = sorted(scenes, key=lambda s: s.date)

    def __len__(self):
        """ Number of scenes """
        return len(self.scenes)

    def __getitem__(self, index):
        return self.scenes[index]

    def dates(self):
        """ Get sorted list of dates for all scenes """
        return sorted([s.date for s in self.scenes])

    def sensors(self, date=None):
        """ List of all available sensors across scenes """
        if date is None:
            return list(set([s.platform for s in self.scenes]))
        else:
            return list(set([s.platform for s in self.scenes if s.date == date]))

    def print_scenes(self, params=[]):
        """ Print summary of all scenes """
        if len(params) == 0:
            params = ['date', 'scene_id']
        txt = 'Scenes (%s):\n' % len(self.scenes)
        txt += ''.join(['{:^20}'.format(p) for p in params]) + '\n'
        for s in self.scenes:
            txt += ''.join(['{:^20}'.format(s.metadata[p]) for p in params]) + '\n'
        print(txt)

    def text_calendar(self):
        """ Get calendar for dates """
        date_labels = {}
        for d in self.dates():
            sensors = self.sensors(d)
            if len(sensors) > 1:
                date_labels[d] = 'Multiple'
            else:
                date_labels[d] = sensors[0]
        return utils.get_text_calendar(date_labels)

    def save(self, filename):
        """ Save scene metadata """
        with open(filename, 'w') as f:
            f.write(json.dumps(self.geojson()))

    def geojson(self):
        """ Get all metadata as GeoJSON """
        features = [s.geojson() for s in self.scenes]
        return {
            'type': 'FeatureCollection',
            'features': features
        }

    @classmethod
    def load(cls, filename):
        """ Load a collections class from a GeoJSON file of metadata """
        with open(filename) as f:
            metadata = json.loads(f.read())['features']
        scenes = [Scene(**(md['properties'])) for md in metadata]
        return Scenes(scenes)

    def download(self, **kwargs):
        return [s.download(**kwargs) for s in self.scenes]

    def review_thumbnails(self):
        """ Review all thumbnails in scenes """
        new_scenes = []
        for scene in self.scenes:
            try:
                keep = scene.review_thumbnail()
                if keep:
                    new_scenes.append(scene)
            except Exception as e:
                return
        self.scenes = new_scenes
