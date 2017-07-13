# sat-search

[![CircleCI](https://circleci.com/gh/sat-utils/sat-search.svg?style=svg&circle-token=a66861b5cbba7acd4abd7975f804ab061a365e1b)](https://circleci.com/gh/sat-utils/sat-search)

A python3 library and a command line tool for searching publicly available satellite imagery using a conformant API, such as [sat-api](https://github.com/sat-utils/sat-api).

## Installation
sat-search has been developed and tested using Python 3.6 and Python2 is not supported. It is recommended [pyenv](https://github.com/pyenv/pyenv) is used to control Python versions, along with a virtual environment.
sat-search can be conveniently installed from PyPi:

    # install the latest release version
    $ pip install satsearch
    # install the latest pre-release version
    $ pip install satsearch --pre
    
Or, it can be installed directly from the repository on GitHub where BRANCHNAME is the branch to install such as *master* or *develop*.

    $ pip install git+git://github.com/sat-utils/sat-search.git@BRANCHNAME

## Usage

sat-search can be used as a simple command line program, or the library can be used in other Python applications.

### CLI

The command line program, *sat-search*, allows the user to query for available 


### Library







Example
=======

```
from ssearch import Search
results = Search.query(scene_id='LC81230172016109LGN00')
results.returned
results.returned
1
results.query
{'scene_id': 'LC81230172016109LGN00', 'limit': 100}
results.scenes
[LC81230172016109LGN00]
results.scenes[0].cloud_coverage
46.24

## Development

    # or, clone with ssh and then install
    $ git clone git@github.com:sat-utils/sat-search.git
    $ cd sat-search
    $ 

### Running tests

```
$ python setup.py test
```

## About
sat-search was created by [Development Seed](<http://developmentseed.org>) and is part of a collection of tools called [sat-utils](https://github.com/sat-utils).