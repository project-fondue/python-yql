from unittest import TestCase

from yql.utils import get_http_method


class UtilitiesTest(TestCase):
    def test_finds_get_method_for_select_query(self):
        query = "SELECT foo"
        expected_verb = "GET"

        self.assertEqual(get_http_method(query), expected_verb)

    def test_finds_get_method_for_select_query_with_leading_space(self):
        query = " SELECT foo"
        expected_verb = "GET"

        self.assertEqual(get_http_method(query), expected_verb)

    def test_finds_get_method_for_lowercase_select_query(self):
        query = "select foo"
        expected_verb = "GET"

        self.assertEqual(get_http_method(query), expected_verb)

    def test_finds_post_method_for_insert_query(self):
        query = "INSERT into"
        expected_verb = "POST"

        self.assertEqual(get_http_method(query), expected_verb)

    def test_finds_post_method_for_multiline_insert_query(self):
        query = """
        INSERT INTO yql.queries.query (name, query)
        VALUES ("weather", "SELECT * FROM weather.forecast
            WHERE location=90210")
            """
        expected_verb = "POST"

        self.assertEqual(get_http_method(query), expected_verb)

    def test_finds_put_method_for_update_query(self):
        query = "update foo"
        expected_verb = "PUT"

        self.assertEqual(get_http_method(query), expected_verb)

    def test_finds_post_method_for_delete_query(self):
        query = "DELETE from"
        expected_verb = "POST"

        self.assertEqual(get_http_method(query), expected_verb)

    def test_finds_post_method_for_lowercase_delete_query(self):
        query = "delete from"
        expected_verb = "POST"

        self.assertEqual(get_http_method(query), expected_verb)

    def test_finds_get_method_for_show_query(self):
        query = "SHOW tables"
        expected_verb = "GET"

        self.assertEqual(get_http_method(query), expected_verb)

    def test_finds_get_method_for_describe_query(self):
        query = "DESC tablename"
        expected_verb = "GET"

        self.assertEqual(get_http_method(query), expected_verb)
