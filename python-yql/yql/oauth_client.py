"""

Yahoo Specific client for handling two and three legged OAuth
=============================================================

Dependencies
------------

* python-oauth by leah Culver

Stuart Colville
http://muffinresearch.co.uk/

"""

import httplib
from oauth import oauth

class YOAuthError(Exception):
    pass

class YOAuthClient(oauth.OAuthClient):
        
    request_token_url = 'https://api.login.yahoo.com/oauth/v2/get_request_token'
    access_token_url = 'https://api.login.yahoo.com/oauth/v2/get_token'
    authorization_url = 'https://api.login.yahoo.com/oauth/v2/request_auth'
    
    def __init__(self, key, secret, resource_url):
        self.key = key
        self.secret = secret
        self.resource_url = resource_url
        self.connection = httplib.HTTPSConnection('api.login.yahoo.com')

    def fetch_request_token(self, oauth_request):
        # via headers
        # -> OAuthToken
        self.connection.request(oauth_request.http_method, self.request_token_url, headers=oauth_request.to_header('yahooapis.com')) 
        response = self.connection.getresponse()
        content = response.read()
        try:
            return oauth.OAuthToken.from_string(content)
        except KeyError:
            raise YOAuthError, content

    def fetch_access_token(self, oauth_request):
        # via headers
        # -> OAuthToken
        self.connection.request(oauth_request.http_method, self.access_token_url, headers=oauth_request.to_header('yahooapis.com')) 
        response = self.connection.getresponse()
        content = response.read()
        try:
            return oauth.OAuthToken.from_string(content)
        except KeyError:
            raise YOAuthError, content

    def authorize_token(self, oauth_request):
        # via url
        # -> typically just some okay response
        self.connection.request(oauth_request.http_method, oauth_request.to_url()) 
        response = self.connection.getresponse()
        return response.read()

    def access_resource(self, oauth_request):
        # via post body
        # -> some protected resources
        headers = {'Content-Type' :'application/x-www-form-urlencoded'}
        self.connection.request('POST', self.resource_url, body=oauth_request.to_postdata(), headers=headers)
        print self.resource_url        
        response = self.connection.getresponse()
        print response.status
        return response.read() 





