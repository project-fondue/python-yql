
from nose.tools import raises
from yql.utils import get_http_method

TEST_DATA = (
    (" SELECT foo", "GET"),
    ("SELECT foo", "GET"),
    ("select foo", "GET"),
    ("INSERT into", "POST"),
    ("INSERT into", "POST"),
    ("update foo", "PUT"),
    ("DELETE from", "DELETE"),
    ("delete from", "DELETE"),
)

def test_verb_from_query():
    for query, verb in TEST_DATA:
        yield find_verb_from_query, query, verb

def find_verb_from_query(query, verb):
    assert get_http_method(query) == verb

@raises(ValueError)
def test_raises_value_error():
    get_http_method("foo")
