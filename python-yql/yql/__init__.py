"""python-yql

YQL client for Python

Stuart Colville
http://muffinresearch.co.uk/

from yql import YQL

>>> yql = YQL(API_KEY, SECRET)
>>> query = 'select * from flickr.photos.search where text="panda" limit 3';
>>> yql.execute(query)

TODO: Ensure Two legged OAuth works
TODO: Ensure Three legged OAuth works

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
__all__=['YQL', 'YQLTwoLeggedAuth', 'YQLThreeLeggedAuth']


QUERY_PLACEHOLDER = re.compile(r"= ?@(?P<param>[a-z].*?\b)", re.IGNORECASE)

class YQL(object):

    uri = "http://query.yahooapis.com/v1/public/yql"


    def __init__(self, api_key=None, shared_secret=None):
        """Initialise the base class"""
        self.api_key = api_key
        self.secret = shared_secret
        self.http = Http()


    def execute(self, query, name_params=None, *args, **kwargs):
        """Execute YQL query"""    
    
        query_params = {}
       
        if name_params:
            keys_from_query = get_placeholder_keys(query)
            if not keys_from_query:
                raise ValueError, 'If you are using placeholders a dictionary of substitutions is required'
            try:
                keys_from_params = name_params.keys()
            except AttributeError:
                raise ValueError, 'Named parameters for substitution must be passed as a dict'

            if set(keys_from_query) != set(keys_from_params):
                raise ValueError, "Parameter keys don't match the query placeholders"
            else:
                query_params.update(name_params)


        query_params['q'] = query
        query_params['format'] = kwargs.get('format') or  'json'
        
        env = kwargs.get('env')
        if env:
            query_params['env'] = env

        query_string = urlencode(query_params)
        
        resp, content = self.make_request(query, query_string, query_params)
        
        if resp.get('status') == '200':
            return json.loads(content)


    def make_request(self, query, query_string, query_params):
        """Run the YQL query"""

        return self.http.request('%s?%s' % (self.uri, query_string), "POST", query_string)
            

    def get_placeholder_keys(self, query):
        """Gets the @var placeholders
        
        http://developer.yahoo.com/yql/guide/var_substitution.html

        """
        result = []
        for match in  QUERY_PLACEHOLDER.finditer(query):
            result.append(match.group('param'))

        return result



class YQLTwoLeggedAuth(YQL):

    uri = "http://query.yahooapis.com/v1/yql"
    
    def two_legged_request(self, resource_url, parameters=None):
        """Sign a request for two-legged authentication"""
        
        client = YOAuthClient(self.api_key, self.secret)
        consumer = oauth.OAuthConsumer(self.api_key, self.secret)
        request = oauth.OAuthRequest.from_consumer_and_token(consumer, 
                                http_url=resource_url, parameters=parameters)

        signature_method = oauth.OAuthSignatureMethod_HMAC_SHA1()
        request.sign_request(signature_method, consumer, None)
        return request

    def make_request(self, query, query_string, query_params):
        """Sets up and makes the request"""
        url = '%s?%s' % (self.uri, query_string)
        request = self.two_legged_request(url, parameters=query_params)
        return self.http.request("%s?%s" % (self.uri, 
                                            request.to_postdata()), "GET")


class YQLThreeLeggedAuth(YQL):

    uri = "http://query.yahooapis.com/v1/yql"
    
    def three_legged_request(self, resource_url, parameters=None, callback_url=None):
        """Setup three-legged request"""

        if callback_url is None:
            callback_url = 'oob'

        client = YOAuthClient(self.api_key, self.secret, resource_url)
        consumer = oauth.OAuthConsumer(self.api_key, self.secret)
        
        signature_method_plaintext = oauth.OAuthSignatureMethod_PLAINTEXT()
        signature_method_hmac_sha1 = oauth.OAuthSignatureMethod_HMAC_SHA1()

        # get request token
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(
             consumer, callback=callback_url, http_url=client.request_token_url)

        oauth_request.sign_request(signature_method_plaintext, consumer, None)
        token = client.fetch_request_token(oauth_request)

        oauth_request = oauth.OAuthRequest.from_token_and_callback(
                                 token=token, http_url=client.authorization_url)
        
        response = client.authorize_token(oauth_request)
            
        # sad way to get the verifier
        query = urlparse.urlparse(response)[4]
        params = cgi.parse_qs(query, keep_blank_values=False)
            
        verifier = params['oauth_verifier'][0]

        # get access token
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer,
                   token=token, verifier=verifier, http_url=client.access_token_url)

        oauth_request.sign_request(signature_method_plaintext, consumer, token)
        token = client.fetch_access_token(oauth_request)
        print token
        
        # access some protected resources
        #parameters = {'file': 'vacation.jpg', 'size': 'original'} # resource specific params
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer, 
                                token=token, http_method='POST', 
                                http_url=resource_url, parameters=parameters)
        
        oauth_request.sign_request(signature_method_hmac_sha1, consumer, token)
       
        return params

    def make_request(self, query, query_string, query_params):
        pass


if __name__ == "__main__":

    y = YQL()
    print "Making Public Query"
    query = 'select * from flickr.photos.search where text="panda" limit 3';
    print y.execute(query)
   
    try:
        print "Making Private Call"
        from yql.keys import SECRET, API_KEY
        y2 = YQLTwoLeggedAuth(API_KEY, SECRET)
        query = "SELECT * from geo.places WHERE text='SFO'"
        print y2.execute(query)
        
        print "Make private query requiring user auth"
        y3 = YQLThreeLeggedAuth(API_KEY, SECRET)
        query = 'select * from social.connections where owner_guid=me'
        print y3.execute(query) 

    except ImportError:
        print "You need a file containing your Secret and API key"
 
   

