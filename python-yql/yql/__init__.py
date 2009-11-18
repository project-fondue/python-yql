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
import sys
import re
import urlparse, cgi

try:
    import json
except ImportError:
    import simplejson as json


from urllib import urlencode
from httplib2 import Http
from oauth import oauth

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))
from yql.oauth_client import YOAuthClient

__author__ = 'Stuart Colville'
__version__ = '0.1'
__all__ = ['YQL', 'YQLTwoLeggedAuth', 'YQLThreeLeggedAuth']


QUERY_PLACEHOLDER = re.compile(r"[ =]@(?P<param>[a-z].*?\b)", re.IGNORECASE)

class YQL(object):
    """Class for making public YQL queries"""

    uri = "http://query.yahooapis.com/v1/public/yql"


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


    def execute(self, query, name_params=None, *args, **kwargs):
        """Execute YQL query"""    
    
        query_params = self.get_query_params(
                                        query, name_params, *args, **kwargs)
        query_string = urlencode(query_params)
        
        resp, content = self.make_request(query_string, query_params)
        
        if resp.get('status') == '200':
            return json.loads(content)


    def make_request(self, query_string, query_params):
        """Run the YQL query"""

        return self.http.request('%s?%s' % (self.uri, query_string), 
                                                    "POST", query_string)
       
    def get_query_params(self, query, name_params, **kwargs):
        """Get the query params and validate placeholders"""

        query_params = {}
        keys_from_query = self.get_placeholder_keys(query)
        if keys_from_query and not name_params:
            raise ValueError, "If you are using placeholders a dictionary "\
                                                "of substitutions is required"
        elif not keys_from_query and name_params:
            raise ValueError, "You supplied a dictionary of substitutions "\
                                "but the query doesn't have any placeholders"

        elif keys_from_query and name_params:
            try:
                keys_from_params = name_params.keys()
            except AttributeError:
                raise ValueError, "Named parameters for substitution "\
                                                    "must be passed as a dict"

            if set(keys_from_query) != set(keys_from_params):
                raise ValueError, "Parameter keys don't match the query "\
                                                                "placeholders"
            else:
                query_params.update(name_params)


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



class YQLTwoLeggedAuth(YQL):
    """Two legged Auth is simple request which is signed prior to sending"""
    
    uri = "http://query.yahooapis.com/v1/yql"

    def __init__(self, api_key, shared_secret, httplib2_inst=None):
        """Override init to ensure required args"""
        super(YQLTwoLeggedAuth, self).__init__(
                                    api_key, shared_secret, httplib2_inst)

        self.hmac_sha1_signature = oauth.OAuthSignatureMethod_HMAC_SHA1()
    
    def two_legged_request(self, resource_url, parameters=None):
        """Sign a request for two-legged authentication"""
        
        consumer = oauth.OAuthConsumer(self.api_key, self.secret)
        request = oauth.OAuthRequest.from_consumer_and_token(consumer, 
                               http_url=resource_url, parameters=parameters)

        request.sign_request(self.hmac_sha1_signature, consumer, None)
        return request

    def make_request(self, query_string, query_params):
        """Sets up and makes the request"""
        url = '%s?%s' % (self.uri, query_string)
        request = self.two_legged_request(url, parameters=query_params)
        return self.http.request("%s?%s" % (self.uri, 
                                            request.to_postdata()), "GET")


class YQLThreeLeggedAuth(YQL):
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

    * ``get_auth_url_and_token`` (returns a token and the auth url)
    * get verifier through callback or from screen
    * ``get_access_token``  (returns the access token)
    * ``execute`` - makes the request to the protected resource.

    """

    uri = "http://query.yahooapis.com/v1/yql"

    def __init__(self, api_key, shared_secret, httplib2_inst=None):
        """Override init to ensure required args"""
        super(YQLThreeLeggedAuth, self).__init__(
                                    api_key, shared_secret, httplib2_inst)

        self.plaintext_signature = oauth.OAuthSignatureMethod_PLAINTEXT()
        self.hmac_sha1_signature = oauth.OAuthSignatureMethod_HMAC_SHA1()
        
        self.client = YOAuthClient(self.api_key, self.secret)
        self.consumer = oauth.OAuthConsumer(self.api_key, self.secret)


    def get_auth_url_and_token(self, callback_url=None):
        """First step is to get the token and then send the request that 
        provides the auth URL

        Returns a tuple of token and the authorisation URL.

        """

        if not callback_url:
            callback_url = 'oob'
    
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(
                                     self.consumer, callback=callback_url, 
                                     http_url=self.client.request_token_url)
        
        oauth_request.sign_request(
                              self.plaintext_signature, self.consumer, None)
        token = self.client.fetch_request_token(oauth_request)
        
        # Authorize token to get Auth URL
        oauth_request = oauth.OAuthRequest.from_token_and_callback(
                                     token=token, 
                                     http_url=self.client.authorization_url)
        
        return token, oauth_request.to_url()
    

    def get_access_token(self, request_token, verifier):

        """Helper function for getting access token

        If callback is 'oob' this will be provided following login
        
        If not you will need need to extract the auth_verifier 
        parameter from your callback url on the site where you 
        are implementing 3-legged auth

        The token can be stored and re-used for subsequent calls.

        """
        # If you pass verifier into the from_consumer_and_token 
        # the resulting oauth_request has a token but no verifier 
        # Setting verifier as an attr of token fixes that. But seems 
        # a bit weird imho
        setattr(request_token, 'verifier', verifier)

        # get access token
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(
                      self.consumer, token=request_token,
                      http_url=self.client.access_token_url)

        oauth_request.sign_request(self.plaintext_signature,
                                               self.consumer, request_token)
        token = self.client.fetch_access_token(oauth_request)
        return token
 
            
    def execute(self, query, name_params=None, token=None, *args, **kwargs):
        """Execute YQL Note in this case the token is required"""    
    
        query_params = self.get_query_params(
                                        query, name_params, *args, **kwargs)
        query_string = urlencode(query_params)

        if not token:
            raise ValueError, "Without a token three-legged-auth cannot be"\
                                                              " carried out"
       
        url = '%s?%s' % (self.uri, query_string)
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(
                                  self.consumer, token=token, 
                                  http_url=url, parameters=query_params)
        # Sign request 
        oauth_request.sign_request(self.hmac_sha1_signature, 
                                                       self.consumer, token)

        resp, content = self.http.request("%s?%s" % (self.uri, 
                                            oauth_request.to_postdata()), "GET")

        if resp.get('status') == '200':
            return json.loads(content)


if __name__ == "__main__":

    y = YQL()
    print "Making Public Query"
    query = 'select * from flickr.photos.search where text="panda" limit 3'
    print y.execute(query)
    print  
 
    try:
        from yql.keys import SECRET, API_KEY
        print "Making Private Call"
        y2 = YQLTwoLeggedAuth(API_KEY, SECRET)
        query = "SELECT * from geo.places WHERE text='SFO'"
        print y2.execute(query)
        print
        
        print "Make private query requiring user auth"
        y3 = YQLThreeLeggedAuth(API_KEY, SECRET)
        query = 'select * from social.connections where owner_guid=me'
        request_token, auth_url = y3.get_auth_url_and_token()

        print "Visit url %s and get a verifier string" % auth_url
        verifier = raw_input("Enter the code: ")

        access_token = y3.get_access_token(request_token, verifier)
        print y3.execute(query, token=access_token) 

    except ImportError:
        print "You need a file containing your Secret and API key"
 
   

