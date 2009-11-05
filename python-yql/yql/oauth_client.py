from oauth.oauth import OAuthClient

class YOAuthClient(OAuthClient):
        
    request_token_uri = 'https://api.login.yahoo.com/oauth/v2/get_request_token'
    access_token_uri = 'https://api.login.yahoo.com/oauth/v2/get_token'
    auth_uri = 'https://api.login.yahoo.com/oauth/v2/request_auth'

    def fetch_request_token(self, oauth_request):
        """Get the request token."""
        raise NotImplementedError

    def fetch_access_token(self, oauth_request):
        """Get the access token"""
        raise NotImplementedError

    def access_resource(self, oauth_request):
        """Some protected resource."""
        raise NotImplementedError
