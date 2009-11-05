"""YQL Wrapper in Python

Stuart Colville
http://muffinresearch.co.uk/

BSD License

from yql import YQL

>>> yql = YQL(API_KEY, SECRET)
>>> query = 'select * from flickr.photos.search where text="panda" limit 3';
>>> yql.execute(query)

"""

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '../'))

from yql.oauth_client import YOAuthClient
from urllib import urlencode
from httplib2 import Http

try:
    import json
except ImportError:
    import simplejson as json

__author__ = 'Stuart Colville'
__version__ = '0.1'

__all__=['YQL']


PUBLIC_URI = "http://query.yahooapis.com/v1/public/yql"
PRIVATE_URI = "http://query.yahooapis.com/v1/yql"

class YQL(object):

    def __init__(self, api_key=None, shared_secret=None, *args, **kwargs):
        self.api_key = api_key
        shared_secret = shared_secret
    
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
            # invoke Oauth
            oa_client = YOAuthClient(self.api_key, 
                                        self.shared_secret, call_back_url=None)
        else:
            h = Http()
            query_string = urlencode(params)
            resp, content = h.request('%s?%s' % (PUBLIC_URI, query_string), "POST", query_string)

        if resp.get('status') == '200':
            return json.loads(content)
            

if __name__ == "__main__":

    yql = YQL()
    query = 'select * from flickr.photos.search where text="panda" limit 3';
    print yql.execute(query)
   

    
