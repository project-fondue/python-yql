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


    def access_protected(self, url):
    
        client = YOAuthClient(self.api_key, self.secret, url)
        consumer = oauth.OAuthConsumer(CONSUMER_KEY, CONSUMER_SECRET)
        signature_method_plaintext = oauth.OAuthSignatureMethod_PLAINTEXT()
        signature_method_hmac_sha1 = oauth.OAuthSignatureMethod_HMAC_SHA1()
        pause()

        # get request token
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(
             consumer, callback=CALLBACK_URL, http_url=client.request_token_url)

        oauth_request.sign_request(signature_method_plaintext, consumer, None)
        token = client.fetch_request_token(oauth_request)

        oauth_request = oauth.OAuthRequest.from_token_and_callback(
                                 token=token, http_url=client.authorization_url)
        
        # this will actually occur only on some callback
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

        # access some protected resources
        parameters = {'file': 'vacation.jpg', 'size': 'original'} # resource specific params
        oauth_request = oauth.OAuthRequest.from_consumer_and_token(consumer, 
                                token=token, http_method='POST', 
                                http_url=RESOURCE_URL, parameters=parameters)
        
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
       
        # Need to carry out if we are using the private endpoint
        if uri == 'private':
            resp = self.access_protected('%s?%s' % (uri, query_string))
        else:
            h = Http()
            query_string = urlencode(params)
            resp, content = h.request('%s?%s' % (uri, query_string), "POST", query_string)

        if resp.get('status') == '200':
            return json.loads(content)
            

if __name__ == "__main__":

    yql = YQL()
    print "Making Public Query"
    query = 'select * from flickr.photos.search where text="panda" limit 3';
    print yql.execute(query)
   
    try:
        print "Making Private Call"
        from yql.keys import SECRET, API_KEY
        yql = YQL(API_KEY, SECRET)
        query = "SELECT * from geo.places WHERE text='SFO'"
        print yql.execute(query, endpoint='private')
    except ImportError:
        print "You need a file containing your Secret and API key"
 
   
    
