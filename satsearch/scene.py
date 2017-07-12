import os
import logging
import requests


logger = logging.getLogger(__name__)


_DEFAULT_SOURCE = 'aws_s3'


class SatSceneError(Exception):
    pass


class Scene(object):

    def __init__(self, **kwargs):
        """ Initialize a scene object """
        self.metadata = kwargs
        required = ['scene_id', 'date', 'data_geometry', 'download_links']
        logger.debug('Creating Scene object with', kwargs)
        if not set(required).issubset(kwargs.keys()):
            raise SatSceneError('Invalid Scene (required parameters: %s' % ' '.join(required))
        # TODO - check validity of date and geometry, at least one download link

    def __repr__(self):
        return self.scene_id

    @property
    def scene_id(self):
        return self.metadata['scene_id']

    @property
    def date(self):
        return self.metadata['date']

    @property
    def geometry(self):
        return self.metadata['data_geometry']

    @property
    def download_sources(self):
        return self.metadata['download_links'].keys()

    def download_links(self, source=_DEFAULT_SOURCE):
        """ Return dictionary of file key and download link """
        files = self.metadata['download_links'][source]
        prefix = os.path.commonprefix(files)
        keys = [os.path.splitext(f[len(prefix):])[0] for f in files]
        return dict(zip(keys, files))

    def get_thumbnail(self, path=''):
        """ Download thumbnail(s) for this scene """
        fname = os.path.join(path, os.path.basename(self.metadata['thumbnail']))
        self.get_file(self.metadata['thumbnail'], fname)
        # download
        return fname

    def get(self, key, source=_DEFAULT_SOURCE, path=''):
        """ Download this key (e.g., a band, or metadata file) from the scene """
        url = self.download_links(source)[key]
        fname = os.path.join(path, os.path.basename(url))
        return self.get_file(url, fname)

    def get_all(self, source=_DEFAULT_SOURCE, path=''):
        """ Download all files """
        links = self.download_links(source=source)
        fnames = {key: self.get(key, source=source, path=path) for key in links}
        return fnames

    def get_file(self, url, filename):
        """ Download a file """
        logger.info('Downloading %s as %s' % (url, filename))
        r = requests.get(url, stream=True)
        with open(filename, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024):
                if chunk:  # filter out keep-alive new chunks
                    f.write(chunk)
        return filename
