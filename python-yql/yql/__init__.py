"""
Python YQL
==========

YQL client for Python

Author: Stuart Colville http://muffinresearch.co.uk/

.. sourcecode:: python
    
    from yql import YQL

    >>> yql = YQL(API_KEY, SECRET)
    >>> query = 'select * from flickr.photos.search where text="panda" limit 3';
    >>> yql.execute(query)

"""

import os
import re
import sys
import time
import urlparse, cgi

try:
    import json
except ImportError:
    import simplejson as json

from urllib import urlencode
from httplib2 import Http
import oauth2 as oauth

try:
    from urlparse import parse_qs, parse_qsl
except ImportError:
    from cgi import parse_qs, parse_qsl

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

__author__ = 'Stuart Colville'
__version__ = '0.2'
__all__ = ['Public', 'TwoLegged', 'ThreeLegged']

QUERY_PLACEHOLDER = re.compile(r"[ =]@(?P<param>[a-z].*?\b)", re.IGNORECASE)

REQUEST_TOKEN_URL = 'https://api.login.yahoo.com/oauth/v2/get_request_token'
ACCESS_TOKEN_URL = 'https://api.login.yahoo.com/oauth/v2/get_token'
AUTHORIZATION_URL = 'https://api.login.yahoo.com/oauth/v2/request_auth'

PUBLIC_URI = "http://query.yahooapis.com/v1/public/yql"
PRIVATE_URI = "http://query.yahooapis.com/v1/yql"


class YQLError(Exception):
    pass


class Public(object):
    """Class for making public YQL queries"""

    def __init__(self, api_key=None, shared_secret=None, httplib2_inst=None):
        """
        Init the base class.
        
        Optionally you can pass in an httplib2 instance which allows you 
        to set-up the instance in a different way for your own uses. 

        Also it's very helpful in a testing scenario.

        """
        self.api_key = api_key
        self.secret = shared_secret
        self.http = httplib2_inst or Http()
        self.uri = PUBLIC_URI
     

    def get_query_params(self, query, params, **kwargs):
        """Get the query params and validate placeholders"""

        query_params = {}
        keys_from_query = self.get_placeholder_keys(query)
        if keys_from_query and not params:
            raise ValueError, "If you are using placeholders a dictionary "\
                                                "of substitutions is required"
        elif not keys_from_query and params:
            raise ValueError, "You supplied a dictionary of substitutions "\
                                "but the query doesn't have any placeholders"

        elif keys_from_query and params:
            try:
                keys_from_params = params.keys()
            except AttributeError:
                raise ValueError, "Named parameters for substitution "\
                                                       "must be passed as a dict"

            if set(keys_from_query) != set(keys_from_params):
                raise ValueError, "Parameter keys don't match the query "\
                                                                "placeholders"
            else:
                query_params.update(params)


        query_params['q'] = query
        query_params['format'] = kwargs.get('format') or  'json'
        
        env = kwargs.get('env')
        if env:
            query_params['env'] = env

        return query_params     


    @staticmethod
    def get_placeholder_keys(query):
        """Gets the @var placeholders
        
        http://developer.yahoo.com/yql/guide/var_substitution.html

        """
        result = []
        for match in  QUERY_PLACEHOLDER.finditer(query):
            result.append(match.group('param'))

        return result


    def get_uri(self, query, params=None, **kwargs):
        """Get the the request url"""
        params = self.get_query_params(query, params, **kwargs)
        query_string = urlencode(params)
        return '%s?%s' % (self.uri, query_string)


    def execute(self, query, params=None, **kwargs):
        """Execute YQL query"""    
        url = self.get_uri(query, params, **kwargs)
        resp, content = self.http.request(url, "GET")
        if resp.get('status') == '200':
            return json.loads(content)
 

class TwoLegged(Public):
    """Two legged Auth is simple request which is signed prior to sending"""
    
    def __init__(self, api_key, shared_secret, httplib2_inst=None):
        """Override init to ensure required args"""
        super(TwoLegged, self).__init__(api_key, shared_secret, httplib2_inst)
        self.uri = PRIVATE_URI
        self.hmac_sha1_signature = oauth.SignatureMethod_HMAC_SHA1()
        self.plaintext_signature = oauth.SignatureMethod_PLAINTEXT()

    @staticmethod
    def get_base_params():
        """Set-up the basic parameters needed for a request"""
 
        params = {}
        params['oauth_version'] = "1.0"
        params['oauth_nonce'] = oauth.generate_nonce()
        params['oauth_timestamp'] = int(time.time())

        return params 
   
  
    def __two_legged_request(self, resource_url, parameters=None):
        """Sign a request for two-legged authentication"""
        
        params = self.get_base_params()
        if parameters:
            params.update(parameters)

        consumer = oauth.Consumer(self.api_key, self.secret)
        request = oauth.Request(method="GET", url=resource_url, parameters=params)
        request.sign_request(self.hmac_sha1_signature, consumer, None)
        
        return request
    
    
    def get_uri(self, query, params=None, **kwargs):
        """Get the the request url"""
        query_params = self.get_query_params(query, params, **kwargs)
        url = '%s?%s' % (self.uri, urlencode(query_params))
        request = self.__two_legged_request(url, parameters=query_params)
        
        return "%s?%s" % (self.uri, request.to_postdata()) 


    def execute(self, query, params=None, **kwargs):
        """Execute YQL query"""    
            
        signed_url = self.get_uri(query, params, **kwargs)
        resp, content = self.http.request(signed_url, "GET")

        if resp.get('status') == '200':
            return json.loads(content)
    

class ThreeLegged(TwoLegged):

    """
    Three-legged Auth is used when it involves private data such as a 
    user's contacts.

    Three-legged auth is most likely to be used in a web-site or 
    web-accessible application. Three-legged auth requires the user 
    to authenticate the request through the Yahoo login.

    Three-legged auth requires the implementation to:
        
    * Request a token
    * Get a authentication url
    * User uses the auth url to login which will redirect to a callback or shows a verfier string on screen
    * Verifier is read at the callback url or manually provided to get the access token
    * resources is access

    For an implementation this will require calling the following methods in order 
    the first time the user needs to authenticate

    * ``get_auth_url_and_token`` (returns a token and the auth url)
    * get verifier through callback or from screen
    * ``get_access_token``  (returns the access token)
    * ``execute`` - makes the request to the protected resource.

    Once the access token has been provided subsequent requests can re-use it. 
    
    Access tokens expire after 1 hour, however they can be refreshed with 
    the ``refresh_token`` method


    """

    def __init__(self, api_key, shared_secret, httplib2_inst=None):
        """Override init to add consumer"""
        super(ThreeLegged, self).__init__(
                                    api_key, shared_secret, httplib2_inst)

        self.consumer = oauth.Consumer(self.api_key, self.secret)


    def get_token_and_auth_url(self, callback_url=None):
        """First step is to get the token and then send the request that 
        provides the auth URL

        Returns a tuple of token and the authorisation URL.

        """

        client = oauth.Client(self.consumer) 

        params = {}
        params['oauth_callback'] = callback_url or 'oob'

        request = oauth.Request(parameters=params)
        url = REQUEST_TOKEN_URL
        resp, cont = client.request(url, "POST", request.to_postdata()) 
        
        if resp.get('status') == '200':
            token = oauth.Token.from_string(cont)
            data = dict(parse_qsl(cont))
            return token, data['xoauth_request_auth_url'] 
    

    def get_access_token(self, token, verifier):

        """Get the access token

        The verifier (required) should have been provided to the 
        user following login to at the url returned 
        by the ``get_token_and_auth_url`` method.
        
        If not you will need need to extract the auth_verifier 
        parameter from your callback url on the site where you 
        are implementing 3-legged auth in order to pass it to this
        function.

        The access token can be stored and re-used for subsequent 
        calls.

        The stored token will also need to be refreshed periodically 
        with ``refresh_token()``

        """

        client = oauth.Client(self.consumer) 

        params = {}
        params['oauth_verifier'] = verifier

        oauth_request = oauth.Request.from_consumer_and_token(
                               self.consumer, token=token, 
                               http_url=ACCESS_TOKEN_URL, parameters=params)

        oauth_request.sign_request(
                self.plaintext_signature, self.consumer, token)

        url = oauth_request.to_url()
        postdata = oauth_request.to_postdata()
        resp, cont = self.http.request(url, "POST", postdata) 

        if resp.get('status') == '200':
            access_token = oauth.Token.from_string(cont)

        return access_token

    
    @staticmethod
    def token_has_expired(token):
        """Check to see if a token has expired"""

        pass

    def refresh_token(self, token):
        """Access Tokens only last for one hour from the point of being issued. 

        When a token has expired it needs to be refreshed this method takes an 
        expired token and refreshes it.

        token parameter can be either a token object or a token string.
        
        """
        if not hasattr(token, "key"):
            token = YahooToken.from_string(token)

        params = self.get_base_params()
        params['oauth_token'] = token.key
        params['oauth_token_secret'] = token.secret
        params['oauth_session_handle'] = token.session_handle

        oauth_request = oauth.Request.from_consumer_and_token(
                               self.consumer, token=token,
                               http_url=ACCESS_TOKEN_URL, parameters=params)

        oauth_request.sign_request(
                self.plaintext_signature, self.consumer, token)

        url = oauth_request.to_url()
        postdata = oauth_request.to_postdata()
        resp, cont = self.http.request(url, "POST", postdata) 
        
        if resp.get('status') == '200':
            access_token = YahooToken.from_string(cont)

        return access_token


    def get_uri(self, query, params=None, token=None, **kwargs):
        """Get the the request url"""
        query_params = self.get_query_params(query, params, **kwargs)
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

        return "%s?%s" % (self.uri,  oauth_request.to_postdata())
            
            
    def execute(self, query, params=None, token=None, **kwargs):
        """Execute YQL Note in this case the token is required"""    
        
        uri = self.get_uri(query, params, token,  **kwargs)
        resp, content = self.http.request(uri, "GET")

        if resp.get('status') == '200':
            return json.loads(content)


class YahooToken(oauth.Token):
    """A subclass of oauth.Token with the addition of a place to 
    stash the session_handler which is required for token refreshing

    """

    @staticmethod
    def from_string(s):
        """Deserializes a token from a string like one returned by
        
        `to_string()`."""
 
        if not len(s):
            raise ValueError("Invalid parameter string.")
 
        params = urlparse.parse_qs(s, keep_blank_values=False)
        if not len(params):
            raise ValueError("Invalid parameter string.")
 
        try:
            key = params['oauth_token'][0]
        except Exception:
            raise ValueError("'oauth_token' not found in OAuth request.")
 
        try:
            secret = params['oauth_token_secret'][0]
        except Exception:
            raise ValueError("'oauth_token_secret' not found in "
                "OAuth request.")
 
        token = YahooToken(key, secret)

        session_handle = dict(parse_qsl(s)).get('oauth_session_handle')
        if session_handle:
            setattr(token, 'session_handle', session_handle)
        
        try:
            token.callback_confirmed = params['oauth_callback_confirmed'][0]
        except KeyError:
            pass # 1.0, no callback confirmed.

        return token


    def to_string(self):
        """Returns this token as a plain string, suitable for storage.
        The resulting string includes the token's secret, so you should never
        send or store this string where a third party can read it.
        
        """
 
        data = {
            'oauth_token': self.key,
            'oauth_token_secret': self.secret,
        }

        if hasattr(self, 'session_handle'):
            data['oauth_session_handle'] = self.session_handle
 
        if self.callback_confirmed is not None:
            data['oauth_callback_confirmed'] = self.callback_confirmed
        return urlencode(data)    



