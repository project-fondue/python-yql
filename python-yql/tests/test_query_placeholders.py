"""Set of tests for the placeholder checking"""

import yql
from nose.tools import raises

@raises(ValueError)
def test_empty_args_raises_valueerror():
    y = yql.Public()
    query = "SELECT * from foo where dog=@dog"
    params = {}
    y.execute(query, params) 

@raises(ValueError)
def test_incorrect_args_raises_valueerror():
    y = yql.Public()
    query = "SELECT * from foo where dog=@dog"
    params = {'test': 'fail'}
    y.execute(query, params) 

@raises(ValueError)
def test_params_raises_when_not_dict():
    y = yql.Public()
    query = "SELECT * from foo where dog=@dog"
    params = ['test']
    y.execute(query, params) 

@raises(ValueError)
def test_unecessary_args_raises_valueerror():
    y = yql.Public()
    query = "SELECT * from foo where dog='test'"
    params = {'test': 'fail'}
    y.execute(query, params) 

@raises(ValueError)
def test_incorrect_type_raises_valueerror():
    y = yql.Public()
    query = "SELECT * from foo where dog=@test"
    params = ('fail')
    y.execute(query, params) 

def test_placeholder_regex_one():
    y = yql.Public()
    query = "SELECT * from foo where email='foo@foo.com'"
    placeholders = y.get_placeholder_keys(query)
    assert placeholders == []

def test_placeholder_regex_two():
    y = yql.Public()
    query = "SELECT * from foo where email=@foo'"
    placeholders = y.get_placeholder_keys(query)
    assert placeholders == ['foo']

def test_placeholder_regex_three():
    y = yql.Public()
    query = "SELECT * from foo where email=@foo and test=@bar'"
    placeholders = y.get_placeholder_keys(query)
    assert placeholders == ['foo', 'bar']

def test_placeholder_regex_four():
    y = yql.Public()
    query = "SELECT * from foo where foo='bar' LIMIT @foo"
    placeholders = y.get_placeholder_keys(query)
    assert placeholders == ['foo']

def test_placeholder_regex_five():
    y = yql.Public()
    query = """SELECT * from foo 
                where foo='bar' LIMIT 
                @foo"""
    placeholders = y.get_placeholder_keys(query)
    assert placeholders == ['foo']

