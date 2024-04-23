# coding=utf-8
# Copyright 2018-2023 EvaDB
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import unittest
from test.markers import reddit_skip_marker
from test.util import get_evadb_for_testing

import pytest

from evadb.server.command_handler import execute_query_fetch_all
from evadb.third_party.databases.reddit.table_column_info import SUBMISSION_COLUMNS


@pytest.mark.notparallel
class RedditDataSourceTest(unittest.TestCase):
    def setUp(self):
        self.evadb = get_evadb_for_testing()
        # reset the catalog manager before running each test
        self.evadb.catalog().reset()

    def tearDown(self):
        execute_query_fetch_all(self.evadb, "DROP DATABASE IF EXISTS reddit_data;")

    @reddit_skip_marker
    def test_should_run_select_query_on_reddit(self):
        # Create database.
        params = {
            "subreddit": "cricket",
            "client_id": "clientid..",
            "client_secret": "clientsecret..",
            "user_agent": "test script for dev eva",
        }
        query = f"""CREATE DATABASE reddit_data
                    WITH ENGINE = "reddit",
                    PARAMETERS = {params};"""
        execute_query_fetch_all(self.evadb, query)

        query = "SELECT * FROM reddit_data.submissions LIMIT 10;"
        batch = execute_query_fetch_all(self.evadb, query)
        self.assertEqual(len(batch), 10)
        expected_column = list(
            ["submissions.{}".format(col) for col, _ in SUBMISSION_COLUMNS]
        )
        self.assertEqual(batch.columns, expected_column)


if __name__ == "__main__":
    unittest.main()
