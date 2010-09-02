import yql
from nose.tools import raises

try:
    from urlparse import parse_qs, parse_qsl
except ImportError:
    from cgi import parse_qs, parse_qsl


def test_create_yahoo_token():
    token = yql.YahooToken('test-key', 'test-secret')
    assert token.key == 'test-key'
    assert token.secret == 'test-secret'

def test_y_token_to_string():
    token = yql.YahooToken('test-key', 'test-secret')
    token_to_string = token.to_string()
    string_data = dict(parse_qsl(token_to_string))
    assert string_data.get('oauth_token') == 'test-key'
    assert string_data.get('oauth_token_secret') == 'test-secret'

def test_y_token_to_string2():
    token = yql.YahooToken('test-key', 'test-secret')

    token.timestamp = '1111'
    token.session_handle = 'poop'
    token.callback_confirmed = 'basilfawlty'

    token_to_string = token.to_string()
    string_data = dict(parse_qsl(token_to_string))
    assert string_data.get('oauth_token') == 'test-key'
    assert string_data.get('oauth_token_secret') == 'test-secret'
    assert string_data.get('token_creation_timestamp') == '1111'
    assert string_data.get('oauth_callback_confirmed') == 'basilfawlty'
    assert string_data.get('oauth_session_handle') == 'poop'

def test_y_token_from_string():
    token_string = "oauth_token=foo&oauth_token_secret=bar&oauth_session_handle=baz&token_creation_timestamp=1111"
    token_from_string = yql.YahooToken.from_string(token_string)
    assert token_from_string.key == 'foo'
    assert token_from_string.secret == 'bar'
    assert token_from_string.session_handle == 'baz'
    assert token_from_string.timestamp == '1111'

@raises(ValueError)
def test_y_token_raises_value_error():
    yql.YahooToken.from_string('')

@raises(ValueError)
def test_y_token_raises_value_error2():
    yql.YahooToken.from_string('foo')

@raises(ValueError)
def test_y_token_raises_value_error3():
    yql.YahooToken.from_string('oauth_token=bar')

@raises(ValueError)
def test_y_token_raises_value_error4():
    yql.YahooToken.from_string('oauth_token_secret=bar')

@raises(AttributeError)
def test_y_token_without_timestamp_raises():
    token = yql.YahooToken('test', 'test2')
    y = yql.ThreeLegged('test', 'test2')
    y.check_token(token)

def test_y_token_without_timestamp_raises2():

    def refresh_token_replacement(token):
        return 'replaced'

    y = yql.ThreeLegged('test', 'test2')
    y.refresh_token = refresh_token_replacement

    token = yql.YahooToken('test', 'test2')
    token.timestamp = 11111
    assert y.check_token(token) == 'replaced'


