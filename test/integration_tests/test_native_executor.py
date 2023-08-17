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
from test.util import (
    get_evadb_for_testing,
    shutdown_ray,
)

import pytest

from evadb.server.command_handler import execute_query_fetch_all
from evadb.utils.logging_manager import logger


@pytest.mark.notparallel
class NativeExecutorTest(unittest.TestCase):
    def setUp(self):
        self.evadb = get_evadb_for_testing()
        # reset the catalog manager before running each test
        self.evadb.catalog().reset()

    def tearDown(self):
        shutdown_ray()

    def test_should_run_simple_query_in_sqlalchemy(self):
        execute_query_fetch_all(
            self.evadb,
            "USE DemoDB (SELECT * FROM table);",
        )
