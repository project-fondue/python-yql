"""Set of tests for the placeholder checking"""

from yql import *
from nose import with_setup
from nose.tools import raises


@raises(ValueError)
def test_empty_args_raises_valueerror():
    y = YQL()
    query = "SELECT * from foo where dog=@dog"
    params = {}
    y.execute(query, params) 

@raises(ValueError)
def test_incorrect_args_raises_valueerror():
    y = YQL()
    query = "SELECT * from foo where dog=@dog"
    params = {'test': 'fail'}
    y.execute(query, params) 

@raises(ValueError)
def test_unecessary_args_raises_valueerror():
    y = YQL()
    query = "SELECT * from foo where dog='test'"
    params = {'test': 'fail'}
    y.execute(query, params) 

def test_placeholder_regex_one():
    y=YQL()
    query = "SELECT * from foo where email='foo@foo.com'"
    placeholders = y.get_placeholder_keys(query)
    assert placeholders == []

def test_placeholder_regex_two():
    y=YQL()
    query = "SELECT * from foo where email=@foo'"
    placeholders = y.get_placeholder_keys(query)
    assert placeholders == ['foo']

def test_placeholder_regex_three():
    y=YQL()
    query = "SELECT * from foo where email=@foo and test=@bar'"
    placeholders = y.get_placeholder_keys(query)
    assert placeholders == ['foo', 'bar']

def test_placeholder_regex_four():
    y=YQL()
    query = "SELECT * from foo where foo='bar' LIMIT @foo"
    placeholders = y.get_placeholder_keys(query)
    assert placeholders == ['foo']

