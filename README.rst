sat-search
++++++++++++++

.. image:: https://travis-ci.org/sat-utils/sat-search.svg?branch=master
    :target: https://travis-ci.org/sat-utils/sat-search

A python wrapper for sat-api


Installation
============

::

    $ python setup.py install

or::

    $ pip install git+git://github.com/sat-utils/sat-search.git@master


Tests
=====

::

    $ python setup.py test


Example
=======

::

  >>> from ssearch import Search
  >>> results = Search.query(scene_id='LC81230172016109LGN00')
  >>> results.returned
  >>> results.returned
  1
  >>> results.query
  {'scene_id': 'LC81230172016109LGN00', 'limit': 100}
  >>> results.scenes
  [LC81230172016109LGN00]
  >>> results.scenes[0].cloud_coverage
  46.24

