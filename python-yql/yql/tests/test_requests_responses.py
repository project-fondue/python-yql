import os
import urlparse
import httplib2
from urllib import urlencode
from email import message_from_string, message_from_file
from nose import with_setup
from nose.tools import raises
import oauth2 as oauth
import yql

try:
    from urlparse import parse_qs, parse_qsl
except ImportError:
    from cgi import parse_qs, parse_qsl

HTTP_SRC_DIR = os.path.join(os.path.dirname(__file__), "http_src/")

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

class TestPublic(yql.Public):
    """Subclass of YQL to allow returning of the request data"""    

    def execute(self, query, name_params=None, *args, **kwargs):
        query_params = self.get_query_params(query, name_params, *args, **kwargs) 
        query_string = urlencode(query_params)
    
        uri =  "%s?%s" % (self.uri, query_string)
        return uri, query_params

class TestTwoLegged(yql.TwoLegged):
    """Subclass of YQLTwoLegged to allow returning of the request data"""    

    def execute(self, query, params=None, *args, **kwargs):
        query_params = self.get_query_params(query, params, *args, **kwargs)
        url = '%s?%s' % (self.uri, urlencode(query_params))
        request = self._TwoLegged__two_legged_request(url, parameters=query_params)
        
        signed_url = "%s?%s" % (self.uri, request.to_postdata()) 
        return signed_url 

class TestThreeLegged(yql.ThreeLegged):
    """Subclass of YQLTwoLegged to allow returning of the request data"""    

    def execute(self, query, token=None, params=None, *args, **kwargs):

        query_params = self.get_query_params(query, params, *args, **kwargs)
        query_string = urlencode(query_params)

        if not token:
            raise ValueError, "Without a token three-legged-auth cannot be"\
                                                              " carried out"
         
        url = '%s?%s' % (self.uri, query_string)

        oauth_request = oauth.Request.from_consumer_and_token(
                                        self.consumer, http_url=url, 
                                        token=token, parameters=query_params)

        # Sign request 
        oauth_request.sign_request(
                            self.hmac_sha1_signature, self.consumer, token)

        uri = "%s?%s" % (self.uri,  oauth_request.to_postdata())

        return uri


@with_setup(set_up_http_request_data, tear_down_http_request_data)
def test_urlencoding_for_public_yql():
    query = 'SELECT * from foo'
    from httplib2 import Http
    y = TestPublic(httplib2_inst=Http())
    uri, query_params = y.execute(query)
    assert uri == "http://query.yahooapis.com/v1/public/yql?q=SELECT+%2A+from+foo&format=json"

@with_setup(set_up_http_request_data, tear_down_http_request_data)
def test_env_for_public_yql():
    query = 'SELECT * from foo'
    from httplib2 import Http
    y = TestPublic(httplib2_inst=Http())
    uri, query_params = y.execute(query, env="http://foo.com")
    assert uri.find(urlencode({"env":"http://foo.com"})) > -1

@with_setup(set_up_http_request_data, tear_down_http_request_data)
def test_name_param_inserted_for_public_yql():
    query = 'SELECT * from foo WHERE dog=@dog'
    from httplib2 import Http
    y = TestPublic(httplib2_inst=Http())
    uri, query_params = y.execute(query, {"dog": "fifi"})
    assert uri.find('dog=fifi') > -1

@raises(TypeError)
def test_yql_with_2leg_auth_raises_typerror():
    y = TestTwoLegged()

@raises(TypeError)
def test_yql_with_3leg_auth_raises_typerror():
    y = TestThreeLegged()

@with_setup(set_up_http_from_file, tear_down_http_from_file)
def test_json_response_from_file():
    query = 'SELECT * from foo WHERE dog=@dog'
    from httplib2 import Http
    y = yql.Public(httplib2_inst=Http())
    content = y.execute(query, {"dog": "fifi"})
    assert content is not None

def test_api_key_and_secret_attrs():
    from httplib2 import Http
    y = yql.TwoLegged('test-api-key', 'test-secret')
    assert y.api_key == 'test-api-key'
    assert y.secret == 'test-secret'

def test_api_key_and_secret_attrs2():
    from httplib2 import Http
    y = yql.ThreeLegged('test-api-key', 'test-secret')
    assert y.api_key == 'test-api-key'
    assert y.secret == 'test-secret'   

def test_get_base_params():
    from httplib2 import Http
    y = yql.ThreeLegged('test-api-key', 'test-secret')
    result = y.get_base_params()
    assert set(['oauth_nonce', 'oauth_version', 'oauth_timestamp']) \
                                                    == set(result.keys())

def test_get_two_legged_request_keys():
    from httplib2 import Http
    y = yql.TwoLegged('test-api-key', 'test-secret')
    # Accessed this was because it's private
    request =  y._TwoLegged__two_legged_request('http://google.com')
    assert set(['oauth_nonce', 'oauth_version', 'oauth_timestamp', 
        'oauth_consumer_key', 'oauth_signature_method',
        'oauth_version', 'oauth_signature']) == set(request.keys())

def test_get_two_legged_request_values():
    from httplib2 import Http
    y = yql.TwoLegged('test-api-key', 'test-secret')
    # Accessed this was because it's private
    request =  y._TwoLegged__two_legged_request('http://google.com')
    assert request['oauth_consumer_key'] == 'test-api-key'
    assert request['oauth_signature_method'] == 'HMAC-SHA1'
    assert request['oauth_version'] == '1.0'

def test_get_two_legged_request_param():
    from httplib2 import Http
    y = yql.TwoLegged('test-api-key', 'test-secret')
    # Accessed this way because it's private
    request =  y._TwoLegged__two_legged_request('http://google.com', 
                                                        {"test-param": "test"})
    assert request.get('test-param') == 'test'

@with_setup(set_up_http_from_file, tear_down_http_from_file)
def test_get_two_legged_from_file():
    query = 'SELECT * from foo'
    from httplib2 import Http
    y = yql.TwoLegged('test-api-key', 'test-secret', httplib2_inst=Http())
    # Accessed this was because it's private
    assert y.execute(query) is not None

@with_setup(set_up_http_request_data, tear_down_http_request_data)
def test_request_for_two_legged():
    query = 'SELECT * from foo'
    from httplib2 import Http
    y = TestTwoLegged('test-api-key', 'test-secret', httplib2_inst=Http())
    signed_url = y.execute(query)
    qs  = dict(parse_qsl(signed_url.split('?')[1]))
    assert qs['q'] == query
    assert qs['format'] == 'json'

@raises(ValueError)
def test_raises_for_three_legged_with_no_token():
    query = 'SELECT * from foo'
    from httplib2 import Http
    y = TestThreeLegged('test-api-key', 'test-secret', httplib2_inst=Http())
    request = y.execute(query)

@with_setup(set_up_http_request_data, tear_down_http_request_data)
def test_request_for_three_legged():
    query = 'SELECT * from foo'
    from httplib2 import Http
    y = TestThreeLegged('test-api-key', 'test-secret', httplib2_inst=Http())
    token = oauth.Token.from_string('oauth_token=foo&oauth_token_secret=bar')
    signed_url = y.execute(query, token)
    qs  = dict(parse_qsl(signed_url.split('?')[1]))
    assert qs['q'] == query
    assert qs['format'] == 'json'
