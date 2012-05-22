import json
import os
from unittest import TestCase

from yql import NotOneError, YQLError


class YQLErrorTest(TestCase):
    def test_is_represented_by_content_as_json_if_provided_as_string(self):
        error = YQLError(resp='some response', content='some content')

        self.assertEqual("'some content'", str(error))

    def test_is_represented_by_error_description_as_json_if_provided_as_json(self):
        content = {
            'error': {
                'description': 'some description',
            }
        }
        error = YQLError(resp='some response', content=json.dumps(content))

        #TODO: verify if this is really the intended representation
        self.assertEqual("u'some description'", str(error))


class NotOneErrorTest(TestCase):
    def test_is_represented_by_message_as_json(self):
        error = NotOneError('some message')

        self.assertEqual("'some message'", str(error))