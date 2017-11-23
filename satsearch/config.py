import os

# API URL
SAT_API = os.getenv('SAT_API', 'https://api.developmentseed.org/satellites')

# data directory to store downloaded imagery
DATADIR = os.getenv('SATUTILS_DATADIR', './')

# do not create subdirectories of satellite_name/scene_id when saving imagery
SUBDIRS = os.getenv('SATUTILS_SUBDIRS', '${satellite_name}/${date}')

# filename pattern for saving files
FILENAME = os.getenv('SATUTILS_FILENAME', '${scene_id}')
