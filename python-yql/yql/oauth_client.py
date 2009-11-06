"""

Yahoo Specific client for handling two and three legged OAuth
=============================================================

Dependencies
------------

* python-oauth by leah Culver
* httplib2 by Joe Gregorio

Stuart Colville
http://muffinresearch.co.uk/

"""

import httplib
from oauth.oauth import OAuthClient

class YOAuthClient(OAuthClient):
        
    request_token_uri = 'https://api.login.yahoo.com/oauth/v2/get_request_token'
    access_token_uri = 'https://api.login.yahoo.com/oauth/v2/get_token'
    auth_uri = 'https://api.login.yahoo.com/oauth/v2/request_auth'

    def __init__(self, key, secret, url):
        self.key = key
        self.secret = secret
        self.url = url
        self.http = httplib.Http()
    
    def fetch_request_token(self, oauth_request):
        """Get the request token."""
        resp, content = self.http.request(self.request_token_url, 
                                        headers=oauth_request.to_header()) 
        return oauth.OAuthToken.from_string(content)

    def fetch_access_token(self, oauth_request):
        """Get the access token"""
        resp, content = self.http.request(self.access_token_url, 
                                        headers=oauth_request.to_header()) 
        return oauth.OAuthToken.from_string(content)

    def authorize_token(self, oauth_request):
        """Authorize the token"""
        resp,content = self.http.request(oauth_request.to_url()) 
        return content 

    def access_resource(self, oauth_request):
        """Access the protected resource."""
        headers = {'Content-Type' :'application/x-www-form-urlencoded'}
        resp, cont = self.http.request(self.url, 'POST', 
                               oauth_request.to_postdata(), headers=headers)
        return content



