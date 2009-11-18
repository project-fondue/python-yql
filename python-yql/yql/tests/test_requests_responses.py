
import os
import urlparse
import httplib2
from urllib import urlencode
from email import message_from_string, message_from_file
from nose import with_setup
from nose.tools import raises
from yql import *


HTTP_SRC_DIR = "http_src/"

class MyHttpReplacement:
    """Build a stand-in for httplib2.Http that takes its
    response headers and bodies from files on disk

    http://bitworking.org/news/172/Test-stubbing-httplib2
    
    """

    def __init__(self, cache=None, timeout=None):
        self.hit_counter = {}

    def request(self, uri, method="GET", body=None, headers=None, redirections=5):
        path = urlparse.urlparse(uri)[2]
        fname = os.path.join(HTTP_SRC_DIR, path[1:])

        if not os.path.exists(fname):
            index = self.hit_counter.get(fname, 1)

            if os.path.exists(fname + "." + str(index)):
                self.hit_counter[fname] = index + 1
                fname = fname + "." + str(index)

        if os.path.exists(fname):
            f = file(fname, "r")
            response = message_from_file(f)
            f.close()
            body = response.get_payload()
            headers = httplib2.Response(response)
            return (headers, body)
        else:
            return (httplib2.Response({"status": "404"}), "")

    def add_credentials(self, name, password):
        pass

class RequestDataHttpReplacement:
    """Create an httplib stub that returns request data"""

    def request(self, uri, *args, **kwargs):
        """return the request data"""
        return uri, args, kwargs

old_httplib2 = httplib2.Http

def set_up_http_from_file():
    httplib2.Http = MyHttpReplacement

def tear_down_http_from_file():
    httplib2.Http = old_httplib2

def set_up_http_request_data():
    httplib2.Http = RequestDataHttpReplacement

def tear_down_http_request_data():
    httplib2.Http = old_httplib2

class YQLTestRequest(YQL):
    """Subclass of YQL to allow returning of the request data"""    

    def execute(self, query, name_params=None, *args, **kwargs):
        query_params = self.get_query_params(query, name_params, *args, **kwargs) 
        query_string = urlencode(query_params)
    
        return  self.make_request(query_string, query_params)

class YQLTestRequestTwoLegged(YQLTwoLeggedAuth):
    """Subclass of YQLTwoLegged to allow returning of the request data"""    

    def execute(self, query, name_params=None, *args, **kwargs):
        query_params = self.get_query_params(query, name_params, *args, **kwargs) 
        query_string = urlencode(query_params)
    
        return  self.make_request(query_string, query_params)

class YQLTestRequestThreeLegged(YQLThreeLeggedAuth):
    """Subclass of YQLTwoLegged to allow returning of the request data"""    

    def execute(self, query, name_params=None, *args, **kwargs):
        query_params = self.get_query_params(query, name_params, *args, **kwargs) 
        query_string = urlencode(query_params)
    
        return  self.make_request(query_string, query_params)

@with_setup(set_up_http_request_data, tear_down_http_request_data)
def test_urlencoding_for_public_yql():
    query = 'SELECT * from foo'
    from httplib2 import Http
    y = YQLTestRequest(httplib2_inst=Http())
    uri, args, kwargs = y.execute(query)
    assert uri == "http://query.yahooapis.com/v1/public/yql?q=SELECT+%2A+from+foo&format=json"

@with_setup(set_up_http_request_data, tear_down_http_request_data)
def test_env_for_public_yql():
    query = 'SELECT * from foo'
    from httplib2 import Http
    y = YQLTestRequest(httplib2_inst=Http())
    uri, args, kwargs = y.execute(query, env="http://foo.com")
    assert uri.find(urlencode({"env":"http://foo.com"})) > -1

@with_setup(set_up_http_request_data, tear_down_http_request_data)
def test_name_param_inserted_for_public_yql():
    query = 'SELECT * from foo WHERE dog=@dog'
    from httplib2 import Http
    y = YQLTestRequest(httplib2_inst=Http())
    uri, args, kwargs = y.execute(query, {"dog": "fifi"})
    assert uri.find('dog=fifi') > -1

@raises(TypeError)
def test_yql_with_2leg_auth_raises_typerror():
    y = YQLTestRequestTwoLegged()

@raises(TypeError)
def test_yql_with_3leg_auth_raises_typerror():
    y = YQLTestRequestThreeLegged()

