==========
Python YQL
==========

Python YQL is a client library for making queries with Yahoo Query Language.

Installation
============

::

    sudo easy_install yql

Usage
=====

::

    >>> import yql
    >>> y = yql.Public()
    >>> query = 'select * from flickr.photos.search where text=@text and api_key="INSERT_API_KEY_HERE" limit 3';
    >>> y.execute(query, {"text": "panda"})


Source-code
===========

Branches exist at https://github.com/project-fondue/python-yql

Documentation
=============

Documentation can be found at http://python-yql.org/

Contributions
=============

Bug-fixes/Features/Patches always welcome - please add branches to the launchpad project.

