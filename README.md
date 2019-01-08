# SAT-SEARCH

[![CircleCI](https://circleci.com/gh/sat-utils/sat-search.svg?style=svg&circle-token=a66861b5cbba7acd4abd7975f804ab061a365e1b)](https://circleci.com/gh/sat-utils/sat-search)

Sat-search is a Python 2/3 library and a command line tool for discovering and downloading publicly available satellite imagery using a conformant API such as [sat-api](https://github.com/sat-utils/sat-api).

The STAC version supported by a given version of sat-api is shown in the table below. Additional information can be found in the [CHANGELOG](CHANGELOG.md)

| sat-search | STAC  |
| ---------- | ----  |
| 0.1.0      | 0.5.0 |
| 0.2.0      | 0.6.0 |


## Installation
It is recommended to use [pyenv](https://github.com/pyenv/pyenv) and [virtualenv](https://virtualenv.pypa.io/en/latest/) to to control Python versions and installed dependencies. sat-search can be conveniently installed from PyPi:

    # install the latest release version
    $ pip install sat-search

Sat-search is a very lightweight application, with the only dependency being [sat-stac](https://github.com/sat-utils/sat-stac), which in turn has two dependencies: `requests` and `python-dateutil`.

## Using sat-search

With sat-search you can search a STAC compliant API with full querying support (if supported by the API). Search results are saved as a GeoJSON FeatureCollection and can be loaded later. Assets can be easily downloaded by the key, or color if provided.

Sat-search comes with a Command Line Interface (CLI), but is also a Python library that can be incorporated into other applications. This README only covers use of the CLI.

#### The CLI
The sat-search CLI has an extensive online help that can be printed with the `-h` switch.
```
$ sat-search -h
usage: sat-search [-h] {search,load} ...

sat-search (v0.2.0b1)

positional arguments:
  {search,load}
    search       Perform new search of scenes
    load         Load scenes from previous search

optional arguments:
  -h, --help     show this help message and exit
```

As can be seen there are two subcommands, each of which has it's own online help (i.e. "sat-search search -h" and "sat-search load -h") and will be discussed in detail below.

#### Searching

```
usage: sat-search [-h] {search,load} ...

sat-search (v0.2.0b1)

positional arguments:
  {search,load}
    search       Perform new search of items
    load         Load items from previous search

optional arguments:
  -h, --help     show this help message and exit
(satutils) mhanson@clavius:~/devseed/sat-utils/sat-search/scratch$ sat-search search -h
usage: sat-search search [-h] [--version] [-v VERBOSITY]
                         [--print_md [PRINT_MD [PRINT_MD ...]]] [--print_cal]
                         [--save SAVE] [-c COLLECTION]
                         [--bbox BBOX BBOX BBOX BBOX]
                         [--intersects INTERSECTS] [--datetime DATETIME]
                         [--sort SORT] [-p [PROPERTY [PROPERTY ...]]]
                         [--url URL]

optional arguments:
  -h, --help            show this help message and exit
  --version             Print version and exit
  -v VERBOSITY, --verbosity VERBOSITY
                        0:quiet, 1:error, 2:warning, 3:info, 4:debug (default:
                        2)

output options:
  --print_md [PRINT_MD [PRINT_MD ...]]
                        Print specified metadata for matched scenes (default:
                        None)
  --print_cal           Print calendar showing dates (default: False)
  --save SAVE           Save results as GeoJSON (default: None)

search options:
  -c COLLECTION, --collection COLLECTION
                        Name of collection (default: None)
  --bbox BBOX BBOX BBOX BBOX
                        Bounding box (min lon, min lat, max lon, max lat)
                        (default: None)
  --intersects INTERSECTS
                        GeoJSON Feature (file or string) (default: None)
  --datetime DATETIME   Single date/time or begin and end date/time (e.g.,
                        2017-01-01/2017-02-15) (default: None)
  --sort SORT           Sort by fields (default: None)
  -p [PROPERTY [PROPERTY ...]], --property [PROPERTY [PROPERTY ...]]
                        Properties of form KEY=VALUE (<, >, <=, >=, =
                        supported) (default: None)
  --url URL             URL of the API (default: https://sat-api-
                        dev.developmentseed.org)
```

**Search options**

- **intersects** - Provide a GeoJSON Feature string or the name of a GeoJSON file containing a single Feature that is a Polygon of an AOI to be searched.
- **datetime** - Provide a single partial or full datetime (e.g., 2017, 2017-10, 2017-10-11, 2017-10-11T12:00), or two seperated by a slash that defines a range. e.g., 2017-01-01/2017-06-30 will search for scenes acquired in the first 6 months of 2017.
- **property** - Allows searching for any other scene properties by providing the pair as KEY=VALUE (e.g. `-p "landsat:row=42"`, `-p "eo:cloud_cover<10"`)
- **url** - The URL endpoint of a STAC compliant API, this can also be set with the environment variable SATUTILS_API_URL

**Output options**
These options control what to do with the search results, multiple switches can be provided.

- **print_md** - Prints a list of specific metadata fields for all the scenes. If given without any arguments it will print a list of the dates and scene IDs. Otherwise it will print a list of fields that are provided. (e.g., --print_md date eo:cloud_cover eo:platform will print a list of date, cloud cover, and the satellite platform such as WORLDVIEW03)
- **print_cal** - Prints a text calendar with specific days colored depending on the platform of the scene (e.g. landsat-8), along with a legend.
- **save** - Saves results as a FeatureCollection. The FeatureCollection 'properties' contains all of the arguments used in the search and the 'features' contain all of the individual scenes, with individual scene metadata merged with collection level metadata (metadata fields that are the same across all one collection, such as eo:platform)

#### Loading
Scenes that were previously saved with `sat-search search --save ...` can be loaded with the `load` subcommand.

```
$ sat-search load -h
usage: sat-search load [-h] [--version] [-v VERBOSITY]
                       [--print_md [PRINT_MD [PRINT_MD ...]]] [--print_cal]
                       [--save SAVE] [--datadir DATADIR] [--filename FILENAME]
                       [--download [DOWNLOAD [DOWNLOAD ...]]]
                       items

positional arguments:
  items                 GeoJSON file of Items

optional arguments:
  -h, --help            show this help message and exit
  --version             Print version and exit
  -v VERBOSITY, --verbosity VERBOSITY
                        0:quiet, 1:error, 2:warning, 3:info, 4:debug (default:
                        2)

output options:
  --print_md [PRINT_MD [PRINT_MD ...]]
                        Print specified metadata for matched scenes (default:
                        None)
  --print_cal           Print calendar showing dates (default: False)
  --save SAVE           Save results as GeoJSON (default: None)

download options:
  --datadir DATADIR     Directory pattern to save assets (default:
                        ./${eo:platform}/${date})
  --filename FILENAME   Save assets with this filename pattern based on
                        metadata keys (default: ${id})
  --download [DOWNLOAD [DOWNLOAD ...]]
                        Download assets (default: None)
```

Note that while the search options are gone, output options are still available and can be used with the search results loaded from the file. There is also a new series of options now, for downloading data.

#### Downloading assets
When loading results from a file, the user now has the option to download assets from the scenes.

**Download options**
These control the downloading of assets. Both datadir and filename can include metadata patterns that will be substituted per scene.
- **datadir** - This specifies where downloaded assets will be saved to. It can also be specified by setting the environment variable SATUTILS_DATADIR.
- **filename** - The name of the file to save. It can also be set by setting the environment variable SATUTILS_FILENAME
- **download** - Provide a list of keys to download these assets. More information on downloading data is provided below.

**Metadata patterns**
Metadata patterns can be within **datadir** and **filename** in order to have custom path and filenames based on the scene metadata. For instance specifying datadir as "./${eo:platform}/${date}" will save assets for each scene under directories of the platform and the date. So a landsat-8 scene from June 20, 2018 will have it's assets saved in a directory './landsat-8/2017-06-20'. For filenames these work exactly the same way, except the appropriate extension will be used at the end of the filename, depending on the asset.

**Assets**
The thumbnail for each scene in a *scenes.json* file can be downloaded with
```
    sat-search load scenes.json --download assetname1 assetname2 ...
```
The thumbnails will be saved using a directory and filename according to the `datadir` and `filename` options, and will also have a '_thumbnail` suffix. When thumbnails are downloaded an ESRI Worldfile (.wld) file is created, which is a sidecar file that describes the coordinates and resolution of the images. This enables the thumbnails to be viewed in a GIS program like QGIS in their proper geographical location. The world file does not set the spatial reference system used (lat/lon, or WGS-84, or EPSG:4326), so when opened in QGIS it will need to be selected (EPSG:4326).

## About
sat-search was created by [Development Seed](<http://developmentseed.org>) and is part of a collection of tools called [sat-utils](https://github.com/sat-utils).
