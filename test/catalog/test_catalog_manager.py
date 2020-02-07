# coding=utf-8
# Copyright 2018-2020 EVA
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

import mock

from src.catalog.catalog_manager import CatalogManager


class CatalogManagerTests(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @mock.patch('src.catalog.catalog_manager.init_db')
    def test_catalog_manager_singleton_pattern(self, mocked_db):
        x = CatalogManager()
        y = CatalogManager()
        self.assertEqual(x, y)

        # x.create_dataset("foo")
        # x.create_dataset("bar")
        # x.create_dataset("baz")


if __name__ == '__main__':

    unittest.main()
