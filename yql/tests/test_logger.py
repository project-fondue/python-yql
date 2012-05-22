import os
import shutil
from unittest import TestCase

import yql.logger


class LoggerTest(TestCase):
    def setUp(self):
        self._logging = os.environ.get('YQL_LOGGING', '')

    def tearDown(self):
        os.environ['YQL_LOGGING'] = self._logging

    def test_is_instantiated_even_if_log_dir_doesnt_exist(self):
        os.environ['YQL_LOGGING'] = '1'
        shutil.rmtree(yql.logger.LOG_DIRECTORY)
        logger = yql.logger.get_logger()

    def test_logs_message_to_file(self):
        os.environ['YQL_LOGGING'] = '1'
        logger = yql.logger.get_logger()