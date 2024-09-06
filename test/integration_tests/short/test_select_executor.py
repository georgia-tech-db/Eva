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
from test.util import (  # file_remove,
    create_dummy_4d_batches,
    create_dummy_batches,
    create_sample_video,
    create_table,
    file_remove,
    get_evadb_for_testing,
    get_logical_query_plan,
    load_functions_for_testing,
    shutdown_ray,
)

import numpy as np
import pandas as pd
import pytest

from evadb.binder.binder_utils import BinderError
from evadb.models.storage.batch import Batch
from evadb.optimizer.operators import LogicalFilter
from evadb.server.command_handler import execute_query_fetch_all

NUM_FRAMES = 10


@pytest.mark.notparallel
class SelectExecutorTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.evadb = get_evadb_for_testing()
        cls.evadb.catalog().reset()

        video_file_path = create_sample_video(NUM_FRAMES)
        load_query = f"LOAD VIDEO '{video_file_path}' INTO MyVideo;"
        execute_query_fetch_all(cls.evadb, load_query)

        load_functions_for_testing(cls.evadb)

        cls.table1 = create_table(cls.evadb, "table1", 100, 3)
        cls.table2 = create_table(cls.evadb, "table2", 500, 3)
        cls.table3 = create_table(cls.evadb, "table3", 1000, 3)

    @classmethod
    def tearDownClass(cls):
        shutdown_ray()

        file_remove("dummy.avi")
        execute_query_fetch_all(cls.evadb, """DROP TABLE IF EXISTS table1;""")
        execute_query_fetch_all(cls.evadb, """DROP TABLE IF EXISTS table2;""")
        execute_query_fetch_all(cls.evadb, """DROP TABLE IF EXISTS table3;""")
        execute_query_fetch_all(cls.evadb, "DROP TABLE IF EXISTS MyVideo;")

    def test_should_load_and_sort_in_table(self):
        select_query = "SELECT data, id FROM MyVideo ORDER BY id;"
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        expected_rows = [
            {
                "myvideo.id": i,
                "myvideo.data": np.array(np.ones((32, 32, 3)) * i, dtype=np.uint8),
            }
            for i in range(NUM_FRAMES)
        ]
        expected_batch = Batch(frames=pd.DataFrame(expected_rows))
        self.assertEqual(actual_batch, expected_batch)

        select_query = "SELECT data, id FROM MyVideo ORDER BY id DESC;"
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        expected_batch.reverse()
        self.assertEqual(actual_batch, expected_batch)

    def test_should_load_and_select_in_table(self):
        select_query = "SELECT id FROM MyVideo;"
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        actual_batch.sort()
        expected_rows = [{"myvideo.id": i} for i in range(NUM_FRAMES)]
        expected_batch = Batch(frames=pd.DataFrame(expected_rows))
        self.assertEqual(actual_batch, expected_batch)

        select_query = "SELECT * FROM MyVideo;"
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        actual_batch.sort()
        expected_batch = list(create_dummy_batches())
        self.assertEqual([actual_batch], expected_batch)

    def test_should_raise_binder_error_on_native_datasource(self):
        select_query = "SELECT * FROM test.MyVideo"
        self.assertRaises(
            BinderError, execute_query_fetch_all, self.evadb, select_query
        )

    def test_should_raise_binder_error_on_non_existent_column(self):
        select_query = "SELECT b1 FROM table1;"

        with self.assertRaises(BinderError) as ctx:
            execute_query_fetch_all(self.evadb, select_query)
        self.assertEqual(
            "Cannot find column b1. Did you mean a1? The feasible columns are ['_row_id', 'a0', 'a1', 'a2'].",
            str(ctx.exception),
        )

    def test_should_select_star_in_nested_query(self):
        select_query = """SELECT * FROM (SELECT * FROM MyVideo) AS T;"""
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        actual_batch.sort()
        expected_batch = list(create_dummy_batches())[0]
        expected_batch.modify_column_alias("T")
        self.assertEqual(actual_batch, expected_batch)

        select_query = """SELECT * FROM (SELECT id FROM MyVideo) AS T;"""
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        actual_batch.sort()
        expected_rows = [{"T.id": i} for i in range(NUM_FRAMES)]
        expected_batch = Batch(frames=pd.DataFrame(expected_rows))
        self.assertEqual(actual_batch, expected_batch)

    @unittest.skip("Not supported in current version")
    def test_select_star_in_lateral_join(self):
        select_query = """SELECT * FROM MyVideo JOIN LATERAL
                          Yolo(data);"""
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        self.assertEqual(actual_batch.frames.columns, ["myvideo.id"])

    def test_should_throw_error_when_both_audio_and_video_selected(self):
        query = """LOAD VIDEO 'data/sample_videos/touchdown.mp4'
                   INTO TOUCHDOWN1;"""
        execute_query_fetch_all(self.evadb, query)

        select_query = "SELECT id, audio, data FROM TOUCHDOWN1;"
        try:
            execute_query_fetch_all(self.evadb, select_query)
            self.fail("Didn't raise AssertionError")
        except AssertionError as e:
            self.assertEquals(
                "Cannot query over both audio and video streams", e.args[0]
            )

    def test_select_and_limit(self):
        select_query = "SELECT * FROM MyVideo ORDER BY id LIMIT 5;"
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        actual_batch.sort()
        expected_batch = list(create_dummy_batches(num_frames=10, batch_size=5))

        self.assertEqual(len(actual_batch), len(expected_batch[0]))
        self.assertEqual(actual_batch, expected_batch[0])

    def test_select_and_aggregate(self):
        simple_aggregate_query = "SELECT COUNT(*), AVG(id) FROM MyVideo;"
        actual_batch = execute_query_fetch_all(self.evadb, simple_aggregate_query)

        self.assertEqual(actual_batch.frames.iat[0, 0], 10)
        self.assertEqual(actual_batch.frames.iat[0, 1], 4.5)

    def test_select_and_iframe_sample(self):
        select_query = "SELECT id FROM MyVideo SAMPLE IFRAMES 7 ORDER BY id;"
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        actual_batch.sort()

        expected_batch = list(create_dummy_batches(filters=range(0, NUM_FRAMES, 7)))
        expected_batch[0] = expected_batch[0].project(["myvideo.id"])

        self.assertEqual(len(actual_batch), len(expected_batch[0]))
        self.assertEqual(actual_batch, expected_batch[0])

    def test_select_and_iframe_sample_without_sampling_rate(self):
        select_query = "SELECT id FROM MyVideo SAMPLE IFRAMES ORDER BY id;"
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        actual_batch.sort()

        expected_batch = list(create_dummy_batches(filters=range(0, NUM_FRAMES, 1)))
        expected_batch[0] = expected_batch[0].project(["myvideo.id"])

        self.assertEqual(len(actual_batch), len(expected_batch[0]))
        self.assertEqual(actual_batch, expected_batch[0])

    def test_select_and_groupby_first(self):
        # groupby and orderby together not tested because groupby
        # only applies to video data which is already sorted
        segment_size = 3
        select_query = (
            "SELECT FIRST(id), SEGMENT(data) FROM MyVideo GROUP BY '{} frames';".format(
                segment_size
            )
        )
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        actual_batch.sort()
        ids = np.arange(NUM_FRAMES)
        segments = [ids[i : i + segment_size] for i in range(0, len(ids), segment_size)]
        segments = [i for i in segments if len(i) == segment_size]
        expected_batch = list(create_dummy_4d_batches(filters=segments))[0]
        self.assertEqual(len(actual_batch), len(expected_batch))

        expected_batch.rename(
            columns={"myvideo.id": "FIRST.id", "myvideo.data": "SEGMENT.data"}
        )
        self.assertEqual(
            actual_batch,
            expected_batch.project(["FIRST.id", "SEGMENT.data"]),
        )

    def test_select_and_groupby_with_last(self):
        # groupby and orderby together not tested because groupby
        # only applies to video data which is already sorted
        segment_size = 3
        select_query = (
            "SELECT LAST(id), SEGMENT(data) FROM MyVideo GROUP BY '{}frames';".format(
                segment_size
            )
        )
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        actual_batch.sort()
        ids = np.arange(NUM_FRAMES)
        segments = [ids[i : i + segment_size] for i in range(0, len(ids), segment_size)]
        segments = [i for i in segments if len(i) == segment_size]
        expected_batch = list(
            create_dummy_4d_batches(filters=segments, start_id=segment_size - 1)
        )[0]
        self.assertEqual(len(actual_batch), len(expected_batch))

        expected_batch.rename(
            columns={"myvideo.id": "LAST.id", "myvideo.data": "SEGMENT.data"}
        )
        self.assertEqual(
            actual_batch,
            expected_batch.project(["LAST.id", "SEGMENT.data"]),
        )

    def test_select_and_groupby_should_fail_with_incorrect_pattern(self):
        segment_size = "4a"
        select_query = (
            "SELECT FIRST(id), SEGMENT(data) FROM MyVideo GROUP BY '{} frames';".format(
                segment_size
            )
        )
        self.assertRaises(
            BinderError, execute_query_fetch_all, self.evadb, select_query
        )

    def test_select_and_groupby_should_fail_with_seconds(self):
        segment_size = 4
        select_query = "SELECT FIRST(id), SEGMENT(data) FROM MyVideo GROUP BY '{} seconds';".format(
            segment_size
        )
        self.assertRaises(
            BinderError, execute_query_fetch_all, self.evadb, select_query
        )

    def test_select_and_groupby_should_fail_with_non_video_table(self):
        segment_size = 4
        select_query = "SELECT FIRST(a1) FROM table1 GROUP BY '{} frames';".format(
            segment_size
        )
        self.assertRaises(
            BinderError, execute_query_fetch_all, self.evadb, select_query
        )

    def test_select_and_groupby_with_sample(self):
        # TODO ACTION: groupby and orderby together not tested because groupby
        # only applies to video data which is already sorted
        segment_size = 2
        sampling_rate = 2
        select_query = "SELECT FIRST(id), SEGMENT(data) FROM MyVideo SAMPLE {} GROUP BY '{} frames';".format(
            sampling_rate, segment_size
        )
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        actual_batch.sort()
        ids = np.arange(0, NUM_FRAMES, sampling_rate)

        segments = [ids[i : i + segment_size] for i in range(0, len(ids), segment_size)]
        segments = [i for i in segments if len(i) == segment_size]
        expected_batch = list(create_dummy_4d_batches(filters=segments))[0]
        self.assertEqual(len(actual_batch), len(expected_batch))

        expected_batch.rename(
            columns={"myvideo.id": "FIRST.id", "myvideo.data": "SEGMENT.data"}
        )

        self.assertEqual(
            actual_batch,
            expected_batch.project(["FIRST.id", "SEGMENT.data"]),
        )

    def test_select_and_groupby_and_aggregate_with_pdf(self):
        GROUPBY_SIZE = 8
        execute_query_fetch_all(self.evadb, "DROP TABLE IF EXISTS MyPDFs;")
        # load from directory
        pdf_path = (
            "test/data/uadetrac/small-data/pdf_data/fall_2023_orientation_document.pdf"
        )
        load_query = f"LOAD PDF '{pdf_path}' INTO MyPDFs;"
        execute_query_fetch_all(self.evadb, load_query)
        select_all_query = "SELECT * FROM MyPDFs;"
        all_pdf_batch = execute_query_fetch_all(self.evadb, select_all_query)

        select_query = (
            f"SELECT COUNT(*) FROM MyPDFs GROUP BY '{GROUPBY_SIZE} paragraphs';"
        )
        actual_batch = execute_query_fetch_all(self.evadb, select_query)

        self.assertAlmostEqual(
            len(all_pdf_batch),
            len(actual_batch) * actual_batch.frames.iloc[0, 0],
            None,
            None,
            GROUPBY_SIZE,
        )
        self.assertEqual(len(actual_batch), 99)
        n = len(actual_batch)
        for i in range(n):
            self.assertEqual(actual_batch.frames.iloc[i, 0], GROUPBY_SIZE)

        # tear down
        execute_query_fetch_all(self.evadb, "DROP TABLE IF EXISTS MyPDFs;")

    def test_lateral_join_with_unnest_and_sample(self):
        query = """SELECT id, label
                  FROM MyVideo SAMPLE 2 JOIN LATERAL
                    UNNEST(DummyMultiObjectDetector(data).labels) AS T(label)
                  WHERE id < 10 ORDER BY id;"""
        unnest_batch = execute_query_fetch_all(self.evadb, query)
        expected = Batch(
            pd.DataFrame(
                {
                    "myvideo.id": np.array(
                        [0, 0, 2, 2, 4, 4, 6, 6, 8, 8], dtype=np.intp
                    ),
                    "T.label": np.array(
                        [
                            "person",
                            "person",
                            "car",
                            "car",
                            "bicycle",
                            "bicycle",
                            "person",
                            "person",
                            "car",
                            "car",
                        ]
                    ),
                }
            )
        )
        self.assertEqual(len(unnest_batch), 10)
        self.assertEqual(unnest_batch, expected)

    def test_select_without_from(self):
        # Check test/integration_tests/long/test_model_forecasting.py for `SELECT FUNC(1)` test cases.
        query = """SELECT 1;"""
        batch = execute_query_fetch_all(self.evadb, query)
        expected = Batch(pd.DataFrame([{0: 1}]))
        self.assertEqual(batch, expected)

        query = """SELECT 1>2;"""
        batch = execute_query_fetch_all(self.evadb, query)
        expected = Batch(pd.DataFrame([{0: False}]))
        self.assertEqual(batch, expected)

    def test_should_raise_error_with_missing_alias_in_lateral_join(self):
        function_name = "DummyMultiObjectDetector"
        query = """SELECT id, labels
                  FROM MyVideo JOIN LATERAL DummyMultiObjectDetector(data).labels;"""
        with self.assertRaises(SyntaxError) as cm:
            execute_query_fetch_all(self.evadb, query, do_not_print_exceptions=True)
        self.assertEqual(
            str(cm.exception),
            f"TableValuedFunction {function_name} should have alias.",
        )

        query = """SELECT id, labels
                  FROM MyVideo JOIN LATERAL
                    UNNEST(DummyMultiObjectDetector(data).labels);"""
        with self.assertRaises(SyntaxError) as cm:
            execute_query_fetch_all(self.evadb, query)
        self.assertEqual(
            str(cm.exception),
            f"TableValuedFunction {function_name} should have alias.",
        )

        query = """SELECT id, labels
                  FROM MyVideo JOIN LATERAL DummyMultiObjectDetector(data);"""
        with self.assertRaises(SyntaxError) as cm:
            execute_query_fetch_all(self.evadb, query)
        self.assertEqual(
            str(cm.exception),
            f"TableValuedFunction {function_name} should have alias.",
        )

    def test_should_raise_error_with_invalid_number_of_aliases(self):
        function_name = "DummyMultiObjectDetector"
        query = """SELECT id, labels
                  FROM MyVideo JOIN LATERAL
                    DummyMultiObjectDetector(data).bboxes AS T;"""
        with self.assertRaises(BinderError) as cm:
            execute_query_fetch_all(self.evadb, query)
        self.assertEqual(
            str(cm.exception),
            f"Output bboxes does not exist for {function_name}.",
        )

    def test_should_raise_error_with_invalid_output_lateral_join(self):
        query = """SELECT id, a
                  FROM MyVideo JOIN LATERAL
                    DummyMultiObjectDetector(data) AS T(a, b);
                """
        with self.assertRaises(AssertionError) as cm:
            execute_query_fetch_all(self.evadb, query)
        self.assertEqual(str(cm.exception), "Expected 1 output columns for T, got 2.")

    def test_hash_join_with_one_on(self):
        select_query = """SELECT * FROM table1 JOIN
                        table2 ON table1.a1 = table2.a1;"""
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        expected = pd.merge(
            self.table1,
            self.table2,
            left_on=["table1.a1"],
            right_on=["table2.a1"],
            how="inner",
        )
        if len(expected):
            expected_batch = Batch(expected)
            self.assertEqual(
                expected_batch.sort_orderby(["table1.a2"]),
                actual_batch.sort_orderby(["table1.a2"]),
            )

    def test_hash_join_with_multiple_on(self):
        select_query = """SELECT * FROM table1 JOIN
                        table1 AS table2 ON table1.a1 = table2.a1 AND
                        table1.a0 = table2.a0;"""
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        expected = pd.merge(
            self.table1,
            self.table1,
            left_on=["table1.a1", "table1.a0"],
            right_on=["table1.a1", "table1.a0"],
            how="inner",
        )
        if len(expected):
            expected_batch = Batch(expected)
            self.assertEqual(
                expected_batch.sort_orderby(["table1.a1"]),
                actual_batch.sort_orderby(["table1.a1"]),
            )

    def test_expression_tree_signature(self):
        plan = get_logical_query_plan(
            self.evadb,
            "SELECT id FROM MyVideo WHERE DummyMultiObjectDetector(data).labels @> ['person'];",
        )
        signature = next(plan.find_all(LogicalFilter)).predicate.children[0].signature()
        function_id = (
            self.evadb.catalog()
            .get_function_catalog_entry_by_name("DummyMultiObjectDetector")
            .row_id
        )
        table_entry = self.evadb.catalog().get_table_catalog_entry("MyVideo")
        col_id = (
            self.evadb.catalog().get_column_catalog_entry(table_entry, "data").row_id
        )
        self.assertEqual(
            signature,
            f"DummyMultiObjectDetector[{function_id}](MyVideo.data[{col_id}])",
        )

    def test_function_with_no_input_arguments(self):
        select_query = "SELECT DummyNoInputFunction();"
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        expected = Batch(
            pd.DataFrame([{"dummynoinputfunction.label": "DummyNoInputFunction"}])
        )
        self.assertEqual(actual_batch, expected)

    def test_nested_function_calls(self):
        select_query = "SELECT DummyAccessColumnByName(DummyAccessColumnByName(id, data)) from MyVideo;"
        actual_batch = execute_query_fetch_all(self.evadb, select_query)
        expected = Batch(
            pd.DataFrame(
                [
                    {
                        "dummyaccesscolumnbyname.output1": True,
                        "dummyaccesscolumnbyname.output2": True,
                    }
                ]
            )
        )
        self.assertEqual(actual_batch, expected)
