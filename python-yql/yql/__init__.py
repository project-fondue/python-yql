"""python-yql

YQL client for Python

Stuart Colville
http://muffinresearch.co.uk/

from yql import YQL

>>> yql = YQL(API_KEY, SECRET)
>>> query = 'select * from flickr.photos.search where text="panda" limit 3';
>>> yql.execute(query)

TODO: Ensure Two and three legged OAuth works
TODO: Add support for parameterized Queries http://developer.yahoo.com/yql/guide/var_substitution.html

"""

import os
import sys
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
__all__=['YQL']

PUBLIC_URI = "http://query.yahooapis.com/v1/public/yql"
PRIVATE_URI = "http://query.yahooapis.com/v1/yql"




class YQL(object):

    def __init__(self, api_key=None, shared_secret=None, *args, **kwargs):
        self.api_key = api_key
        self.secret = shared_secret


    def two_legged(self, resource_url, parameters=None):
        client = YOAuthClient(self.api_key, self.secret, resource_url)
        consumer = oauth.OAuthConsumer(self.api_key, self.secret)
        request = oauth.OAuthRequest.from_consumer_and_token(
            consumer, 
            token=None, 
            http_method='GET', 
            http_url=resource_url, 
            parameters=parameters
        )
        signature_method = oauth.OAuthSignatureMethod_HMAC_SHA1()
        request.sign_request(signature_method, consumer, None)
        return client.access_resource(request)


    def three_legged(self, resource_url, parameters=None, callback_url=None):
        
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
      
        verifier = None 
        
        # Three-legged Auth only
        #this will actually occur only on some callback
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
        params = client.access_resource(oauth_request)
        return params

    
    def execute(self, query, *args, **kwargs):
        """Run the YQL query"""
       
        # Work out if we are using the public or private endpoints
        endpoint = kwargs.get('endpoint') or 'public'
        uris = {
            'public': PUBLIC_URI,
            'private': PRIVATE_URI, 
        }
        uri = uris.get(endpoint)
        if not uri:
            raise ValueError, 'endpoint should be either "public" or "private"'

        params = {}
        params['q'] = query
        params['format'] = kwargs.get('format') or  'json'
        
        query_string = urlencode(params)
        print "uri", uri

        # Need to carry out if we are using the private endpoint
        if endpoint == 'private':
            content = self.two_legged('%s?%s' % (uri, query_string), parameters=params)
            return content
        else:
            h = Http()
            resp, content = h.request('%s?%s' % (uri, query_string), "POST", query_string)

            if resp.get('status') == '200':
                return json.loads(content)
            

if __name__ == "__main__":

    # yql = YQL()
    # print "Making Public Query"
    # query = 'select * from flickr.photos.search where text="panda" limit 3';
    # print yql.execute(query)
   
    try:
        print "Making Private Call"
        from yql.keys import SECRET, API_KEY
        yql = YQL(API_KEY, SECRET)
        query = "SELECT * from geo.places WHERE text='SFO'"
        print yql.execute(query, endpoint='private')
    except ImportError:
        print "You need a file containing your Secret and API key"
 
   
    
