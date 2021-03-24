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

from mock import patch

from src.optimizer.operators import LogicalProject, LogicalGet, \
    LogicalFilter, LogicalInsert, LogicalCreateUDF, \
    LogicalLoadData, LogicalUnion, LogicalOrderBy, LogicalLimit
from src.optimizer.plan_generator import PlanGenerator


class PlanGeneratorTest(unittest.TestCase):
    @unittest.skip('No test is needed due to complete implementation rule')
    @patch("src.optimizer.plan_generator.ScanGenerator")
    def test_should_return_use_scan_generator_for_logical_project(self,
                                                                  mock_class):
        mock_instance = mock_class.return_value
        l_project = LogicalProject([])
        PlanGenerator().build(l_project)
        mock_instance.build.assert_called_with(l_project)

    @unittest.skip('No test is needed due to complete implementation rule')
    @patch("src.optimizer.plan_generator.ScanGenerator")
    def test_should_return_use_scan_generator_for_logical_get(self,
                                                              mock_class):
        mock_instance = mock_class.return_value
        l_get = LogicalGet(None, 1)
        PlanGenerator().build(l_get)
        mock_instance.build.assert_called_with(l_get)

    @unittest.skip('No test is needed due to complete implementation rule')
    @patch("src.optimizer.plan_generator.ScanGenerator")
    def test_should_return_use_scan_generator_for_logical_filter(self,
                                                                 mock_class):
        mock_instance = mock_class.return_value
        l_filter = LogicalFilter(None)
        PlanGenerator().build(l_filter)
        mock_instance.build.assert_called_with(l_filter)

    @unittest.skip('No test is needed due to complete implementation rule')
    @patch("src.optimizer.plan_generator.ScanGenerator")
    def test_should_return_use_scan_generator_for_logical_union(self,
                                                                mock_class):
        mock_instance = mock_class.return_value
        l_union = LogicalUnion(True, None)
        l_union.append_child(LogicalGet(None, 1))
        l_union.append_child(LogicalGet(None, 1))
        PlanGenerator().build(l_union)
        mock_instance.build.assert_called_with(l_union)

    @unittest.skip('No test is needed due to complete implementation rule')
    @patch("src.optimizer.plan_generator.ScanGenerator")
    def test_should_return_use_scan_generator_for_logical_orderby(self,
                                                                  mock_class):
        mock_instance = mock_class.return_value
        l_orderby = LogicalOrderBy(None)
        l_orderby.append_child(LogicalGet(None, 1))
        PlanGenerator().build(l_orderby)
        mock_instance.build.assert_called_with(l_orderby)

    @unittest.skip('No test is needed due to complete implementation rule')
    @patch("src.optimizer.plan_generator.ScanGenerator")
    def test_should_return_use_scan_generator_for_logical_limit(self,
                                                                mock_class):
        mock_instance = mock_class.return_value
        l_limit = LogicalLimit(None)
        l_limit.append_child(LogicalGet(None, 1))
        PlanGenerator().build(l_limit)
        mock_instance.build.assert_called_with(l_limit)

    @unittest.skip('No test is needed due to complete implementation rule')
    @patch("src.optimizer.plan_generator.ScanGenerator")
    def test_should_not_call_scan_generator_for_other_types(self,
                                                            mock_class):
        # PlanGenerator().build(Operator(None))
        PlanGenerator().build(LogicalInsert(None, 1, [], []))
        mock_class.assert_not_called()

    @unittest.skip('No test is needed due to complete implementation rule')
    @patch("src.optimizer.plan_generator.InsertGenerator")
    def test_should_return_use_insert_generator_for_logical_insert(
            self, mock_class):
        mock_instance = mock_class.return_value
        l_insert = LogicalInsert(None, 1, [], [])
        PlanGenerator().build(l_insert)
        mock_instance.build.assert_called_with(l_insert)

    @unittest.skip('No test is needed due to complete implementation rule')
    @patch("src.optimizer.plan_generator.InsertGenerator")
    def test_should_not_call_insert_generator_for_other_types(
            self, mock_class):
        # PlanGenerator().build(Operator(None))
        PlanGenerator().build(LogicalFilter(None))
        PlanGenerator().build(LogicalGet(None, 1))
        PlanGenerator().build(LogicalProject([]))
        mock_class.assert_not_called()

    @unittest.skip('No test is needed due to complete implementation rule')
    @patch('src.optimizer.plan_generator.CreateUDFGenerator')
    def test_should_call_create_udf_generator_for_logical_create_udf(
            self, mock):
        mock_instance = mock.return_value
        l_create_udf = LogicalCreateUDF('udf', True, [], [], 'tmp')
        PlanGenerator().build(l_create_udf)
        mock_instance.build.assert_called_with(l_create_udf)

    @unittest.skip('No test is needed due to complete implementation rule')
    @patch('src.optimizer.plan_generator.LoadDataGenerator')
    def test_should_call_load_data_generator(self, mock):
        mock_instance = mock.return_value
        l_load_Data = LogicalLoadData('meta_info', 'path')
        PlanGenerator().build(l_load_Data)
        mock_instance.build.assert_called_with(l_load_Data)
