import os
import urlparse
from urllib import urlencode
from email import message_from_file

from nose.tools import raises
from nose import with_setup
import oauth2 as oauth
import httplib2
import yql

try:
    from urlparse import parse_qsl
except ImportError:
    from cgi import parse_qsl

HTTP_SRC_DIR = os.path.join(os.path.dirname(__file__), "http_src/")

class MyHttpReplacement(object):
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
            response_headers = httplib2.Response(response)
            return (response_headers, body)
        else:
            return (httplib2.Response({"status": "404"}), "")

    def add_credentials(self, name, password):
        pass

class RequestDataHttpReplacement:
    """Create an httplib stub that returns request data"""

    def __init__(self):
        pass
    
    def request(self, uri, *args, **kwargs):
        """return the request data"""
        return uri, args, kwargs

def set_up_http_from_file():
    httplib2.Http = MyHttpReplacement
    httplib2._Http = httplib2.Http

def tear_down_http_from_file():
    httplib2.Http = httplib2._Http
    delattr(httplib2, '_Http')

def set_up_http_request_data():
    httplib2.Http = RequestDataHttpReplacement
    httplib2._Http = httplib2.Http

def tear_down_http_request_data():
    httplib2.Http = httplib2._Http
    delattr(httplib2, '_Http')

def execute_return_uri(self, query, params=None, **kwargs):
    """A surrogate execute method that returns the uri"""
    return self.get_uri(query, params, **kwargs)

class TestPublic(yql.Public):
    """Subclass of YQL to allow returning of the request data"""    
    pass

class TestTwoLegged(yql.TwoLegged):
    """Subclass of YQLTwoLegged to allow returning of the request data"""    
    pass

class TestThreeLegged(yql.ThreeLegged):
    """Subclass of YQLTwoLegged to allow returning of the request data"""    
    pass

setattr(TestPublic, 'execute', execute_return_uri)
setattr(TestTwoLegged, 'execute', execute_return_uri)
setattr(TestThreeLegged, 'execute', execute_return_uri)

@with_setup(set_up_http_request_data, tear_down_http_request_data)
def test_urlencoding_for_public_yql():
    query = 'SELECT * from foo'
    y = TestPublic(httplib2_inst=httplib2.Http())
    uri = y.execute(query)
    assert uri == "http://query.yahooapis.com/v1/public/yql?q=SELECT+%2A+from+foo&format=json"

@with_setup(set_up_http_request_data, tear_down_http_request_data)
def test_env_for_public_yql():
    query = 'SELECT * from foo'
    y = TestPublic(httplib2_inst=httplib2.Http())
    uri = y.execute(query, env="http://foo.com")
    assert uri.find(urlencode({"env":"http://foo.com"})) > -1

@with_setup(set_up_http_request_data, tear_down_http_request_data)
def test_name_param_inserted_for_public_yql():
    query = 'SELECT * from foo WHERE dog=@dog'
    y = TestPublic(httplib2_inst=httplib2.Http())
    uri = y.execute(query, {"dog": "fifi"})
    assert uri.find('dog=fifi') > -1

@raises(TypeError)
def test_yql_with_2leg_auth_raises_typerror():
    TestTwoLegged()

@raises(TypeError)
def test_yql_with_3leg_auth_raises_typerror():
    TestThreeLegged()

@with_setup(set_up_http_from_file, tear_down_http_from_file)
def test_json_response_from_file():
    query = 'SELECT * from foo WHERE dog=@dog'
    y = yql.Public(httplib2_inst=httplib2.Http())
    content = y.execute(query, {"dog": "fifi"})
    assert content.count == 3

def test_api_key_and_secret_attrs():
    y = yql.TwoLegged('test-api-key', 'test-secret')
    assert y.api_key == 'test-api-key'
    assert y.secret == 'test-secret'

def test_api_key_and_secret_attrs2():
    y = yql.ThreeLegged('test-api-key', 'test-secret')
    assert y.api_key == 'test-api-key'
    assert y.secret == 'test-secret'   

def test_get_base_params():
    y = yql.ThreeLegged('test-api-key', 'test-secret')
    result = y.get_base_params()
    assert set(['oauth_nonce', 'oauth_version', 'oauth_timestamp']) \
                                                    == set(result.keys())

def test_get_two_legged_request_keys():
    y = yql.TwoLegged('test-api-key', 'test-secret')
    # Accessed this was because it's private
    request =  y._TwoLegged__two_legged_request('http://google.com')
    assert set(['oauth_nonce', 'oauth_version', 'oauth_timestamp', 
        'oauth_consumer_key', 'oauth_signature_method',
        'oauth_version', 'oauth_signature']) == set(request.keys())

def test_get_two_legged_request_values():
    y = yql.TwoLegged('test-api-key', 'test-secret')
    # Accessed this was because it's private
    request =  y._TwoLegged__two_legged_request('http://google.com')
    assert request['oauth_consumer_key'] == 'test-api-key'
    assert request['oauth_signature_method'] == 'HMAC-SHA1'
    assert request['oauth_version'] == '1.0'

def test_get_two_legged_request_param():
    y = yql.TwoLegged('test-api-key', 'test-secret')
    # Accessed this way because it's private
    request =  y._TwoLegged__two_legged_request('http://google.com', 
                                                        {"test-param": "test"})
    assert request.get('test-param') == 'test'

@with_setup(set_up_http_from_file, tear_down_http_from_file)
def test_get_two_legged_from_file():
    query = 'SELECT * from foo'
    y = yql.TwoLegged('test-api-key', 'test-secret', httplib2_inst=httplib2.Http())
    # Accessed this was because it's private
    assert y.execute(query) is not None

@with_setup(set_up_http_request_data, tear_down_http_request_data)
def test_request_for_two_legged():
    query = 'SELECT * from foo'
    y = TestTwoLegged('test-api-key', 'test-secret', httplib2_inst=httplib2.Http())
    signed_url = y.execute(query)
    qs  = dict(parse_qsl(signed_url.split('?')[1]))
    assert qs['q'] == query
    assert qs['format'] == 'json'

@raises(ValueError)
def test_raises_for_three_legged_with_no_token():
    query = 'SELECT * from foo'
    y = TestThreeLegged('test-api-key', 'test-secret', httplib2_inst=httplib2.Http())
    y.execute(query)

@with_setup(set_up_http_request_data, tear_down_http_request_data)
def test_request_for_three_legged():
    query = 'SELECT * from foo'
    y = TestThreeLegged('test-api-key', 'test-secret', 
                                        httplib2_inst=httplib2.Http())
    token = oauth.Token.from_string(
                        'oauth_token=foo&oauth_token_secret=bar')
    signed_url = y.execute(query, token=token)
    qs  = dict(parse_qsl(signed_url.split('?')[1]))
    assert qs['q'] == query
    assert qs['format'] == 'json'

@with_setup(set_up_http_from_file, tear_down_http_from_file)
def test_three_legged_execution():
    query = 'SELECT * from foo WHERE dog=@dog'
    y = yql.ThreeLegged('test','test2', httplib2_inst=httplib2.Http())
    token = yql.YahooToken('test', 'test2')
    content = y.execute(query, {"dog": "fifi"}, token=token)
    assert content.count == 3

@raises(ValueError)
@with_setup(set_up_http_from_file, tear_down_http_from_file)
def test_three_legged_execution_raises_value_error_with_invalid_uri():
    y = yql.ThreeLegged('test','test2', httplib2_inst=httplib2.Http())
    y.uri = "fail"
    token = yql.YahooToken('tes1t', 'test2')
    y.execute("SELECT foo meh meh ", token=token)
 
@with_setup(set_up_http_from_file, tear_down_http_from_file)
def test_get_access_token_request3():
    y = yql.ThreeLegged('test', 'test-does-not-exist', 
                                httplib2_inst=httplib2.Http())
    new_token = yql.YahooToken('test', 'test2')
    new_token.session_handle = 'sess_handle_test'
    token = y.refresh_token(token=new_token)
    assert hasattr(token, 'key')
    assert hasattr(token, 'secret')

