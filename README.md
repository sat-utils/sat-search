# sat-search

[![CircleCI](https://circleci.com/gh/sat-utils/sat-search.svg?style=svg&circle-token=a66861b5cbba7acd4abd7975f804ab061a365e1b)](https://circleci.com/gh/sat-utils/sat-search)

Sat-search is a Python 2/3 library and a command line tool for discovering and downloading publicly available satellite imagery using a conformant API such as [sat-api](https://github.com/sat-utils/sat-api).

The legacy version of sat-search (<1.0.0) can be used with the legacy version of sat-api (<1.0.0), currently deployed at https://api.developmentseed.org/satellites.

## Installation
It is recommended to use [pyenv](https://github.com/pyenv/pyenv) and [virtualenv](https://virtualenv.pypa.io/en/latest/) to to control Python versions and installed dependencies. sat-search can be conveniently installed from PyPi:

    # install the latest release version
    $ pip install satsearch

## CLI Usage
The command line program, *sat-search*, allows the user to query for available 

```
$ sat-search -h
(satutils) una:~/work/sat-search $ sat-search -h
usage: sat-search [-h] [--satellite_name SATELLITE_NAME]
                  [--scene_id [SCENE_ID [SCENE_ID ...]]]
                  [--intersects INTERSECTS] [--contains CONTAINS]
                  [--date DATE] [--clouds CLOUDS]
                  [--param [PARAM [PARAM ...]]] [--url URL] [--load LOAD]
                  [--save SAVE] [--append] [--datadir DATADIR]
                  [--subdirs SUBDIRS] [--filename FILENAME]
                  [--download [DOWNLOAD [DOWNLOAD ...]]] [--printsearch]
                  [--printmd [PRINTMD [PRINTMD ...]]] [--printcal] [--review]
                  [-v VERBOSITY]

sat-search (v0.1.0)

optional arguments:
  -h, --help            show this help message and exit
  -v VERBOSITY, --verbosity VERBOSITY
                        0:all, 1:debug, 2:info, 3:warning, 4:error, 5:critical
                        (default: 2)

search parameters:
  --satellite_name SATELLITE_NAME
                        Name of satellite (default: None)
  --scene_id [SCENE_ID [SCENE_ID ...]]
                        One or more scene IDs (default: None)
  --intersects INTERSECTS
                        GeoJSON Feature (file or string) (default: None)
  --contains CONTAINS   lon,lat points (default: None)
  --date DATE           Single date or begin and end date (e.g.,
                        2017-01-01,2017-02-15 (default: None)
  --clouds CLOUDS       Range of acceptable cloud cover (e.g., 0,20) (default:
                        None)
  --param [PARAM [PARAM ...]]
                        Additional parameters of form KEY=VALUE (default:
                        None)
  --url URL             URL of the API (default:
                        https://api.developmentseed.org/satellites)

saving/loading parameters:
  --load LOAD           Load search results from file (ignores other search
                        parameters) (default: None)
  --save SAVE           Save scenes metadata as GeoJSON (default: None)
  --append              Append scenes to GeoJSON file (specified by save)
                        (default: False)

download parameters:
  --datadir DATADIR     Local directory to save images (default: ./)
  --subdirs SUBDIRS     Save in subdirs based on these metadata keys (default:
                        ${satellite_name}/${date})
  --filename FILENAME   Save files with this filename pattern based on
                        metadata keys (default: ${scene_id})
  --download [DOWNLOAD [DOWNLOAD ...]]
                        Download files (default: None)

search output:
  --printsearch         Print search parameters (default: False)
  --printmd [PRINTMD [PRINTMD ...]]
                        Print specified metadata for matched scenes (default:
                        None)
  --printcal            Print calendar showing dates (default: False)
  --review              Interactive review of thumbnails (default: False)
```

All of the search parameters are parameters that are sent directly to the API. Most of the common parameters are given in the help as explicit switches (e.g., --date_from, --date_to). However, the --param switch allows any arbitrary search parameters to be passed to the API call as a key=value pair.

```
$ sat-search --param path=7 row=4
Searching for scenes matching criteria:
  path: 7
  row: 4
Found 46 matching scenes
```

### Output Options
The output options control various ways of saving or displaying the information about the scenes. A summary (--printsum) of scenes or calendar showing dates (--printcal) can be printed to the terminal. The --printmd switch allows printing of arbitrary metadata fields as columns.

Printing the resutls to the screen is meant to be a summary. Use the --save switch to save the results as a GeoJSON FeatureCollection. The top level FeatureCollection has a "metadata" field that contains the original search AOI, and each Feature in the collection is a scene.

The saved GeoJSON can be loaded later with the --load switch so that the contents can be summarized with one of the 'search output' switches.

  $ sat-search --load mysearch.geojson --printcal

### Downloading data
Downloading data files for scenes is done with the --download switch where the file key is passed in. The 'thumb' key is the thumbnail.

- **landsat-8 file keys**: B1, B2, B3, B4, B5, B6, B7, B8, B9, B10, B11, BQA, MTL, ANG, thumb
- **sentinel-2A file keys**: B01, B02, B03, B04, B05, B06, B07, B08, B8A, B09, B10, B11, B12, thumb

#### Local data directory
The --datadir, --nosubdirs, switches control the directories where the data is stored while --filename controls the name of the file it is saved to:

- **datadir**: The top level directory where the data is to be stored. Defaults to SATUTILS_DATADIR environment variable OR the current directory if no envvar set
- **subdirs**: Specify metadata fields that will be used to create directories the files will be stored in. For instance, by default *subdirs* is '${satellite_name}/${date}' so stores it under a subdirectory of the satellite name and the date of the scene (e.g., ./landsat-8/LC80120302017021LGN01/). Any combination of strings and metadata fields can be used (e.g., 'sat_${satellite_name}' => ./sat_landsat-8/). subdirs can be set with the SATUTILS_SUBDIRS environment variable.
- **filename**: Like subdirs, the filename can be any combination of strings and metadata fields expressed with environment variables. The default is '${scene_id}', stored in the SATUTILS_FILENAME environment variable.

## Library

The sat-search library is made up of several Python classes. The *Scene* class represents a single set of images for an indentical date (or daterange) and footprint. The *Scenes* class is a collection of *Scene* objects that makes it easier to iterate through them and perform common tasks over all the scenes, such as downloading data.

The *Query* class is a single set of arguments for searching scenes, functions for querying the API with those arguments (and handling of multiple pages if needed) as well storing the results. The higher level *Search* class which is more often used, can deal with multiple *Query* objects, such as individual Scene ids or disparate date ranges that must be issued to the API with different arguments.

## About
sat-search was created by [Development Seed](<http://developmentseed.org>) and is part of a collection of tools called [sat-utils](https://github.com/sat-utils).