"""Tests against live services.

*** SKIPPED BY DEFAULT ***

These tests won't normally be run, as part of the main test suite but are run by 
our hudson instance to tell us should Yahoo's API change in some way that will 
break python-yql.

Note to end-users: These tests are dependent on defining a secrets file with API 
keys and other secrets which are required to carry out these tests.

If the secrets file isn't present the tests are skipped

"""
import os

import yql
from yql.storage import FileTokenStore
from nose.plugins.skip import SkipTest


from unittest import TestCase

try:
    from yql.secrets import *
except ImportError:
    raise SkipTest


class LiveTestCase(TestCase):
    """A test case containing live tests"""
        
    def test_write_bitly_url(self):
        """Test writing bit.ly url"""

        query = """USE 'http://yqlblog.net/samples/bitly.shorten.xml'; 
                   insert into bitly.shorten(login,apiKey,longUrl) 
                   values('%s','%s','http://yahoo.com')""" % (
                                            BITLY_USER, BITLY_API_KEY)
        y = yql.Public()
        res = y.execute(query)
        assert res.rows["results"]["nodeKeyVal"]["shortUrl"] == "http://yhoo.it/9PPTOr"

    def test_update_social_status(self):
        """Updates status"""
        y = yql.ThreeLegged(YQL_API_KEY, YQL_SHARED_SECRET)
        query = """UPDATE social.profile.status SET status='Using YQL. Update' WHERE guid=me""" 

        path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../cache'))
        token_store = FileTokenStore(path, secret='gsfdsfdsfdsfs')

        stored_token = token_store.get('foo')

        if not stored_token:
            # Do the dance
            request_token, auth_url = y.get_token_and_auth_url()
            print "Visit url %s and get a verifier string" % auth_url
            verifier = raw_input("Enter the code: ")
            token = y.get_access_token(request_token, verifier)
            token_store.set('foo', token)
        else:
            # Check access_token is within 1hour-old and if not refresh it
            # and stash it
            token = y.check_token(stored_token)
            if token != stored_token:
                token_store.set('foo', token)

        res = y.execute(query, token=token)
        assert res.rows == "ok"
        new_query = """select message from social.profile.status where guid=me""" 
        res = y.execute(new_query, token=token)
        assert res.rows.get("message") == "Using YQL. Update"

    def test_check_env_var(self):
        """Testing env variable"""
        y = yql.Public()
        env = "http://datatables.org/alltables.env"
        query = "SHOW tables;"
        res = y.execute(query, env=env)
        assert res.count >= 800

    def test_xpath_works(self):
        y = yql.Public()
        query = """SELECT * FROM html 
                   WHERE url='http://google.co.uk' 
                   AND xpath="//input[contains(@name, 'q')]" 
                   LIMIT 10"""
        res = y.execute(query)
        assert res.rows.get("title") == "Google Search"


