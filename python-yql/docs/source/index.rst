.. Python YQL documentation master file, created by
   sphinx-quickstart on Mon Nov 16 08:38:41 2009.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Python YQL's documentation!
======================================

Contents:

.. toctree::
    :maxdepth: 2
    
    usage
    contribution
    code

Introduction
============

Python YQL is a client library for making queries with `Yahoo Query Language <http://developer.yahoo.com/yql/>`_.


    The Yahoo! Query Language is an expressive SQL-like language that lets you query, filter, and join data across Web services. With YQL, apps run faster with fewer lines of code and a smaller network footprint.

    -- `YDN <http://developer.yahoo.com/yql/>`_


QuickStart
----------

.. sourcecode:: sh

    sudo easy_install yql

The following example shows a simple query using the public endpoint.

.. sourcecode:: python

    >>> from yql import YQL
    >>> y = YQL()
    >>> query = 'select * from flickr.photos.search where text=panda limit 3';
    >>> y.execute(query)



Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

