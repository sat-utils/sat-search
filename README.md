# sat-search

[![CircleCI](https://circleci.com/gh/sat-utils/sat-search.svg?style=svg&circle-token=a66861b5cbba7acd4abd7975f804ab061a365e1b)](https://circleci.com/gh/sat-utils/sat-search)

A python3 library and a command line tool for discovering and downloading publicly available satellite imagery using a conformant API, such as [sat-api](https://github.com/sat-utils/sat-api).

## Installation
sat-search has been developed and tested using Python 3.6 and Python2 is not supported. It is recommended [pyenv](https://github.com/pyenv/pyenv) is used to control Python versions, along with a virtual environment.
sat-search can be conveniently installed from PyPi:

    # install the latest release version
    $ pip install satsearch
    # install the latest pre-release version
    $ pip install satsearch --pre
    
Or, it can be installed directly from the repository on GitHub where BRANCHNAME is the branch to install such as *master* or *develop*.

    $ pip install git+git://github.com/sat-utils/sat-search.git@BRANCHNAME

## CLI Usage
The command line program, *sat-search*, allows the user to query for available 

```
$ sat-search -h
usage: sat-search [-h] [--satellite_name SATELLITE_NAME] [--sensor SENSOR]
                  [--date DATE] [--date_from DATE_FROM] [--date_to DATE_TO]
                  [--intersects INTERSECTS] [--contains CONTAINS]
                  [--scene_id [SCENE_ID [SCENE_ID ...]]]
                  [--cloud_from CLOUD_FROM] [--cloud_to CLOUD_TO]
                  [--param [PARAM [PARAM ...]]] [--printsum] [--printcal]
                  [--save SAVE] [--datadir DATADIR] [--nosubdirs] [--dlthumbs]
                  [--dlfiles [DLFILES [DLFILES ...]]]

sat-search (v0.1.0b1)

optional arguments:
  -h, --help            show this help message and exit

Platform search parameters:
  --satellite_name SATELLITE_NAME
  --sensor SENSOR

Temporal search parameters:
  --date DATE
  --date_from DATE_FROM
  --date_to DATE_TO

Spatial search parameters:
  --intersects INTERSECTS
                        GeoJSON Feature (file or string) (default: None)
  --contains CONTAINS   long,lat points (default: None)

Other search parameters:
  --scene_id [SCENE_ID [SCENE_ID ...]]
                        One or more scene IDs (default: None)
  --cloud_from CLOUD_FROM
                        Lower limit for cloud coverage (default: None)
  --cloud_to CLOUD_TO   Upper limit for cloud coverage (default: None)
  --param [PARAM [PARAM ...]]
                        Additional parameters of form KEY=VALUE (default:
                        None)

Output:
  --printsum            Print basic metadata for matched scenes (default:
                        False)
  --printcal            Print calendar showing dates (default: False)
  --save SAVE           Save metadata of all scenes as file (default: None)
  --datadir DATADIR     Local directory to save images (default:
                        /home/mhanson/satutils-data)
  --nosubdirs           When saving, do not create directories usng scene_id
                        (default: False)

Download:
  --dlthumbs            Download thumbnails (default: False)
  --dlfiles [DLFILES [DLFILES ...]]
                        Download files (default: None)
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
The output options control various ways of saving or displaying the information about the scenes. A summary (--printsum) of scenes or calendar showing dates (--printcal) can be printed to the terminal. Or witht The metadata of all the scenes can be printed to the terminal or saved as a JSON file. 

### Downloading data
Downloading data files for scenes is done with the --dlthumbs and --dlfiles switches. The --dlfiles switch is given a list of keys of files to download (specific to each sensor).

- **landsat-8 file keys**: B1, B2, B3, B4, B5, B6, B7, B8, B9, B10, B11, BQA, MTL, ANG
- **sentinel-2A file keys**: B01, B02, B03, B04, B05, B06, B07, B08, B8A, B09, B10, B11, B12

#### Local data directory
The --datadir and --nosubdirs switches control where data is stored. They default to:

- **datadir**: SATUTILS_DATADIR environment variable OR ~/satutils-data if no envvar set
- **nosubdirs**: By default data files for a scene will be saved to the datadir within subdirectories: *platform/scene_id* (e.g., ~/satutils-data/landsat-8/LC80120302017021LGN01/)

## Library

The sat-search library is made up of several Python classes. The *Scene* class represents a single set of images for an indentical date (or daterange) and footprint. The *Scenes* class is a collection of *Scene* objects that makes it easier to iterate through them and perform common tasks over all the scenes, such as downloading data.

The *Query* class is a single set of arguments for searching scenes, functions for querying the API with those arguments (and handling of multiple pages if needed) as well storing the results. The higher level *Search* class which is more often used, can deal with multiple *Query* objects, such as individual Scene ids or disparate date ranges that must be issued to the API with different arguments.

## Development

    # or, clone with ssh and then install
    $ git clone git@github.com:sat-utils/sat-search.git
    $ cd sat-search
    $ 

### Running tests
To run the tests and get a coverage report, use the Python [Nose](http://nose.readthedocs.io/en/latest/) library with the nosetests program.
```
$ nosetests -v --with-coverage --cover-package satsearch
```

## About
sat-search was created by [Development Seed](<http://developmentseed.org>) and is part of a collection of tools called [sat-utils](https://github.com/sat-utils).