"""Tests against live services."""

import yql
from yql.secrets import *
from nose.tools import raises


def test_write_bitly_url():
    """Test writing bit.ly url"""
    query = """USE 'http://yqlblog.net/samples/bitly.shorten.xml'; insert into bitly.shorten(login,apiKey,longUrl) values('%s','%s','http://yahoo.com')""" % (BITLY_USER, BITLY_API_KEY)

    y = yql.Public()
    res = y.execute(query)
    assert res.rows["results"]["nodeKeyVal"]["shortUrl"] == "http://yhoo.it/9PPTOr"


