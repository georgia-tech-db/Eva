# coding=utf-8
# Copyright 2018-2022 EVA
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
from inspect import isabstract
from test.util import get_all_subclasses

from eva.udfs.abstract.abstract_udf import AbstractUDF


class AbstractUDFTest(unittest.TestCase):
    def test_udf_abstract_functions(self):
        derived_udf_classes = list(get_all_subclasses(AbstractUDF))
        for derived_udf_class in derived_udf_classes:
            if isabstract(derived_udf_class) is False:
                obj = derived_udf_class()
                name = obj.name
                self.assertTrue(name is not None)
