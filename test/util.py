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
import gc
import multiprocessing as mp
import os
import shutil
import socket
import time
from contextlib import closing
from itertools import repeat
from multiprocessing import Pool
from pathlib import Path

import numpy as np
import pandas as pd
from mock import MagicMock

from evadb.binder.statement_binder import StatementBinder
from evadb.binder.statement_binder_context import StatementBinderContext
from evadb.catalog.catalog_type import NdArrayType
from evadb.configuration.constants import (
    S3_DOWNLOAD_DIR,
    TMP_DIR,
    EvaDB_DATABASE_DIR,
    EvaDB_INSTALLATION_DIR,
)
from evadb.database import init_evadb_instance
from evadb.expression.function_expression import FunctionExpression
from evadb.functions.abstract.abstract_function import (
    AbstractClassifierFunction,
    AbstractFunction,
)
from evadb.functions.decorators import decorators
from evadb.functions.decorators.io_descriptors.data_types import (
    NumpyArray,
    PandasDataframe,
)
from evadb.functions.function_bootstrap_queries import init_builtin_functions
from evadb.models.storage.batch import Batch
from evadb.optimizer.operators import LogicalFilter, Operator
from evadb.optimizer.plan_generator import PlanGenerator
from evadb.optimizer.statement_to_opr_converter import StatementToPlanConverter
from evadb.parser.parser import Parser
from evadb.plan_nodes.abstract_plan import AbstractPlan
from evadb.server.command_handler import execute_query_fetch_all
from evadb.utils.generic_utils import (
    is_ray_available,
    remove_directory_contents,
    try_to_import_cv2,
)

NUM_FRAMES = 10
FRAME_SIZE = (32, 32)


def suffix_pytest_xdist_worker_id_to_dir(path: str):
    try:
        worker_id = os.environ["PYTEST_XDIST_WORKER"]
        path = Path(str(worker_id) + "_" + path)
    except KeyError:
        pass
    return Path(path)


def get_evadb_for_testing(uri: str = None):
    db_dir = suffix_pytest_xdist_worker_id_to_dir(EvaDB_DATABASE_DIR)
    remove_directory_contents(db_dir)
    gc.collect()
    return init_evadb_instance(db_dir, custom_db_uri=uri)


def get_tmp_dir():
    db_dir = suffix_pytest_xdist_worker_id_to_dir(EvaDB_DATABASE_DIR)
    return db_dir / TMP_DIR


def s3_dir():
    db_dir = suffix_pytest_xdist_worker_id_to_dir(EvaDB_DATABASE_DIR)
    return db_dir / S3_DOWNLOAD_DIR


EvaDB_TEST_DATA_DIR = Path(EvaDB_INSTALLATION_DIR).parent


def is_ray_stage_running():
    import psutil

    return "ray::ray_stage" in (p.name() for p in psutil.process_iter())


def shutdown_ray():
    is_ray_enabled = is_ray_available()
    if is_ray_enabled:
        import ray

        ray.shutdown()


# Ref: https://stackoverflow.com/a/63851681
def get_all_subclasses(cls):
    subclass_list = []

    def recurse(klass):
        for subclass in klass.__subclasses__():
            subclass_list.append(subclass)
            recurse(subclass)

    recurse(cls)

    return set(subclass_list)


def get_mock_object(class_type, number_of_args):
    if number_of_args == 1:
        return class_type()
    elif number_of_args == 2:
        return class_type(MagicMock())
    elif number_of_args == 3:
        return class_type(MagicMock(), MagicMock())
    elif number_of_args == 4:
        return class_type(MagicMock(), MagicMock(), MagicMock())
    elif number_of_args == 5:
        return class_type(MagicMock(), MagicMock(), MagicMock(), MagicMock())
    elif number_of_args == 6:
        return class_type(
            MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock()
        )
    elif number_of_args == 7:
        return class_type(
            MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock(), MagicMock()
        )
    elif number_of_args == 8:
        return class_type(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
    elif number_of_args == 9:
        return class_type(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
    elif number_of_args == 10:
        return class_type(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
    elif number_of_args == 11:
        return class_type(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
    elif number_of_args == 12:
        return class_type(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
    elif number_of_args == 13:
        return class_type(
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
            MagicMock(),
        )
    else:
        raise Exception("Too many args")


def find_free_port():
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]


def get_logical_query_plan(db, query: str) -> Operator:
    stmt = Parser().parse(query)[0]
    StatementBinder(StatementBinderContext(db.catalog)).bind(stmt)
    l_plan = StatementToPlanConverter().visit(stmt)
    return l_plan


def get_physical_query_plan(
    db, query: str, rule_manager=None, cost_model=None
) -> AbstractPlan:
    l_plan = get_logical_query_plan(db, query)
    p_plan = PlanGenerator(db, rule_manager, cost_model).build(l_plan)
    return p_plan


def remove_function_cache(db, query):
    plan = next(get_logical_query_plan(db, query).find_all(LogicalFilter))
    func_exprs = plan.predicate.find_all(FunctionExpression)
    for expr in func_exprs:
        cache_name = expr.signature()
        function_cache = db.catalog.get_function_cache_catalog_entry_by_name(cache_name)
        if function_cache is not None:
            cache_dir = Path(function_cache.cache_path)
            if cache_dir.exists():
                shutil.rmtree(cache_dir)


def create_dataframe(num_frames=1) -> pd.DataFrame:
    frames = []
    for i in range(1, num_frames + 1):
        frames.append({"id": i, "data": (i * np.ones((1, 1)))})
    return pd.DataFrame(frames)


def create_dataframe_same(times=1):
    base_df = create_dataframe()
    for i in range(1, times):
        base_df = pd.concat([base_df, create_dataframe()], ignore_index=True)
    return base_df


def custom_list_of_dicts_equal(one, two):
    for v1, v2 in zip(one, two):
        if v1.keys() != v2.keys():
            return False
        for key in v1.keys():
            if isinstance(v1[key], np.ndarray):
                if not np.array_equal(v1[key], v2[key]):
                    return False

            else:
                if v1[key] != v2[key]:
                    return False

    return True


def convert_bbox(bbox):
    return np.array([np.float32(coord) for coord in bbox.split(",")])


def create_sample_csv(num_frames=NUM_FRAMES):
    try:
        os.remove(os.path.join(get_tmp_dir(), "dummy.csv"))
    except FileNotFoundError:
        pass

    sample_meta = {}

    index = 0
    sample_labels = ["car", "pedestrian", "bicycle"]
    num_videos = 2
    for video_id in range(num_videos):
        for frame_id in range(num_frames):
            random_coords = 200 + 300 * np.random.random(4)
            sample_meta[index] = {
                "id": index,
                "frame_id": frame_id,
                "video_id": video_id,
                "dataset_name": "test_dataset",
                "label": sample_labels[np.random.choice(len(sample_labels))],
                "bbox": ",".join([str(coord) for coord in random_coords]),
                "object_id": np.random.choice(3),
            }

            index += 1

    df_sample_meta = pd.DataFrame.from_dict(sample_meta, "index")
    df_sample_meta.to_csv(os.path.join(get_tmp_dir(), "dummy.csv"), index=False)
    return os.path.join(get_tmp_dir(), "dummy.csv")


def create_csv_with_comlumn_name_spaces(num_frames=NUM_FRAMES):
    try:
        os.remove(os.path.join(get_tmp_dir(), "dummy.csv"))
    except FileNotFoundError:
        pass

    sample_meta = {}

    index = 0
    sample_labels = ["car", "pedestrian", "bicycle"]
    num_videos = 2
    for video_id in range(num_videos):
        for frame_id in range(num_frames):
            random_coords = 200 + 300 * np.random.random(4)
            sample_meta[index] = {
                "id": index,
                "frame id": frame_id,
                "video id": video_id,
                "dataset name": "test_dataset",
                "label": sample_labels[np.random.choice(len(sample_labels))],
                "bbox": ",".join([str(coord) for coord in random_coords]),
                "object id": np.random.choice(3),
            }

            index += 1

    df_sample_meta = pd.DataFrame.from_dict(sample_meta, "index")
    df_sample_meta.to_csv(os.path.join(get_tmp_dir(), "dummy.csv"), index=False)
    return os.path.join(get_tmp_dir(), "dummy.csv")


def create_dummy_csv_batches(target_columns=None):
    if target_columns:
        df = pd.read_csv(
            os.path.join(get_tmp_dir(), "dummy.csv"),
            converters={"bbox": convert_bbox},
            usecols=target_columns,
        )
    else:
        df = pd.read_csv(
            os.path.join(get_tmp_dir(), "dummy.csv"),
            converters={"bbox": convert_bbox},
        )

    yield Batch(df)


def create_csv(num_rows, columns):
    csv_path = os.path.join(get_tmp_dir(), "dummy.csv")
    try:
        os.remove(csv_path)
    except FileNotFoundError:
        pass
    df = pd.DataFrame(columns=columns)
    for col in columns:
        df[col] = np.random.randint(1, 100, num_rows)
    df.to_csv(csv_path, index=False)
    return df, csv_path


def create_text_csv(num_rows=30):
    """
    Creates a csv with 2 columns: id and comment
    The comment column has 2 values: "I like this" and "I don't like this" that are alternated
    """
    csv_path = os.path.join(get_tmp_dir(), "dummy.csv")
    try:
        os.remove(csv_path)
    except FileNotFoundError:
        pass
    df = pd.DataFrame(columns=["id", "comment"])
    df["id"] = np.arange(num_rows)
    df["comment"] = np.where(df["id"] % 2 == 0, "I like this", "I don't like this")
    df.to_csv(csv_path, index=False)
    return csv_path


def create_table(db, table_name, num_rows, num_columns):
    # creates a table with num_rows tuples and columns = [a1, a2, a3, ...]
    columns = "".join("a{} INTEGER, ".format(i) for i in range(num_columns - 1))
    columns += "a{} INTEGER".format(num_columns - 1)
    create_table_query = "CREATE TABLE IF NOT EXISTS {} ( {} );".format(
        table_name, columns
    )
    execute_query_fetch_all(db, create_table_query)
    columns = ["a{}".format(i) for i in range(num_columns)]
    df, csv_file_path = create_csv(num_rows, columns)
    # load the CSV
    load_query = f"LOAD CSV '{csv_file_path}' INTO {table_name};"
    execute_query_fetch_all(db, load_query)
    df.columns = [f"{table_name}.{col}" for col in df.columns]
    return df


def create_sample_image():
    img_path = os.path.join(get_tmp_dir(), "dummy.jpg")
    try:
        os.remove(img_path)
    except FileNotFoundError:
        pass

    img = np.array(np.ones((3, 3, 3)), dtype=np.uint8)
    img[0] -= 1
    img[2] += 1
    try_to_import_cv2()
    import cv2

    cv2.imwrite(img_path, img)
    return img_path


def create_random_image(i, path):
    img = np.random.random_sample([400, 400, 3]).astype(np.uint8)
    try_to_import_cv2()
    import cv2

    cv2.imwrite(os.path.join(path, f"img{i}.jpg"), img)


def create_large_scale_image_dataset(num=1000000):
    img_dir = os.path.join(get_tmp_dir(), f"large_scale_image_dataset_{num}")
    Path(img_dir).mkdir(parents=True, exist_ok=True)

    # Generate images in parallel.
    image_idx_list = list(range(num))
    Pool(mp.cpu_count()).starmap(
        create_random_image, zip(image_idx_list, repeat(img_dir))
    )

    return img_dir


def create_sample_video(num_frames=NUM_FRAMES):
    file_name = os.path.join(get_tmp_dir(), "dummy.avi")
    try:
        os.remove(file_name)
    except FileNotFoundError:
        pass

    duration = 1
    fps = NUM_FRAMES
    try_to_import_cv2()
    import cv2

    out = cv2.VideoWriter(
        file_name, cv2.VideoWriter_fourcc("M", "J", "P", "G"), fps, (32, 32), False
    )
    for i in range(fps * duration):
        data = np.array(np.ones((FRAME_SIZE[1], FRAME_SIZE[0])) * i, dtype=np.uint8)
        out.write(data)
    out.release()

    return file_name


def file_remove(path, parent_dir=None):
    parent_dir = parent_dir or get_tmp_dir()
    try:
        os.remove(os.path.join(parent_dir, path))
    except FileNotFoundError:
        pass


def create_dummy_batches(
    num_frames=NUM_FRAMES,
    filters=[],
    batch_size=10,
    start_id=0,
    video_dir=None,
    is_from_storage=False,  # if cover test directly from storage, it needs to append a _row_number
):
    video_dir = video_dir or get_tmp_dir()

    if not filters:
        filters = range(num_frames)
    data = []
    for i in filters:
        data.append(
            {
                "myvideo._row_id": 1,
                "myvideo.name": os.path.join(video_dir, "dummy.avi"),
                "myvideo.id": i + start_id,
                "myvideo.data": np.array(
                    np.ones((FRAME_SIZE[1], FRAME_SIZE[0], 3)) * i, dtype=np.uint8
                ),
                "myvideo.seconds": np.float32(i / num_frames),
            }
        )

        if is_from_storage:
            data[-1]["myvideo._row_number"] = i + start_id

        if len(data) % batch_size == 0:
            yield Batch(pd.DataFrame(data))
            data = []
    if data:
        yield Batch(pd.DataFrame(data))


def create_dummy_4d_batches(
    num_frames=NUM_FRAMES, filters=[], batch_size=10, start_id=0
):
    if not filters:
        filters = range(num_frames)
    data = []
    for segment in filters:
        segment_data = []
        for i in segment:
            segment_data.append(np.ones((FRAME_SIZE[1], FRAME_SIZE[0], 3)) * i)
        segment_data = np.stack(np.array(segment_data, dtype=np.uint8))
        data.append(
            {
                "myvideo.name": "dummy.avi",
                "myvideo.id": segment[0] + start_id,
                "myvideo.data": segment_data,
                "myvideo.seconds": np.float32(i / num_frames),
            }
        )

        if len(data) % batch_size == 0:
            df = pd.DataFrame(data)
            df = df.astype({"myvideo.id": np.intp})
            yield Batch(df)
            data = []
    if data:
        df = pd.DataFrame(data)
        df = df.astype({"myvideo.id": np.intp})
        yield Batch(df)


def load_functions_for_testing(db, mode="debug"):
    # DEBUG MODE: ALL Functions
    init_builtin_functions(db, mode=mode)


class DummyObjectDetector(AbstractClassifierFunction):
    def setup(self, *args, **kwargs):
        pass

    @property
    def name(self) -> str:
        return "DummyObjectDetector"

    @property
    def labels(self):
        return ["__background__", "person", "bicycle"]

    def forward(self, df: pd.DataFrame) -> pd.DataFrame:
        ret = pd.DataFrame()
        ret["label"] = df.apply(self.classify_one, axis=1)
        return ret

    def classify_one(self, frames: np.ndarray):
        # odd are labeled bicycle and even person
        i = int(frames[0][0][0][0])
        label = self.labels[i % 2 + 1]
        return np.array([label])


class DummyMultiObjectDetector(AbstractClassifierFunction):
    """
    Returns multiple objects for each frame
    """

    def setup(self, *args, **kwargs):
        pass

    @property
    def name(self) -> str:
        return "DummyMultiObjectDetector"

    @property
    def labels(self):
        return ["__background__", "person", "bicycle", "car"]

    def forward(self, df: pd.DataFrame) -> pd.DataFrame:
        ret = pd.DataFrame()
        ret["labels"] = df.apply(self.classify_one, axis=1)
        return ret

    def classify_one(self, frames: np.ndarray):
        i = int(frames[0][0][0][0])
        label = self.labels[i % 3 + 1]
        return np.array([label, label])


class DummyFeatureExtractor(AbstractClassifierFunction):
    """
    Returns a feature for a frame.
    """

    def setup(self, *args, **kwargs):
        pass

    @property
    def name(self) -> str:
        return "DummyFeatureExtractor"

    @property
    def labels(self):
        return []

    def forward(self, df: pd.DataFrame) -> pd.DataFrame:
        # Return the original input as its feature.

        def _extract_feature(row: pd.Series):
            feat_input = row[0]
            feat_input = feat_input.reshape(1, -1)
            feat_input = feat_input.astype(np.float32)
            return feat_input

        ret = pd.DataFrame()
        ret["features"] = df.apply(_extract_feature, axis=1)
        return ret


class DummyObjectDetectorDecorators(AbstractClassifierFunction):
    @decorators.setup(cacheable=True, function_type="object_detection", batchable=True)
    def setup(self, *args, **kwargs):
        pass

    @property
    def name(self) -> str:
        return "DummyObjectDetectorDecorators"

    @property
    def labels(self):
        return ["__background__", "person", "bicycle"]

    @decorators.forward(
        input_signatures=[
            PandasDataframe(
                columns=["Frame_Array"],
                column_types=[NdArrayType.UINT8],
                column_shapes=[(3, 256, 256)],
            )
        ],
        output_signatures=[
            NumpyArray(
                name="label",
                type=NdArrayType.STR,
            )
        ],
    )
    def forward(self, df: pd.DataFrame) -> pd.DataFrame:
        ret = pd.DataFrame()
        ret["label"] = df.apply(self.classify_one, axis=1)
        return ret

    def classify_one(self, frames: np.ndarray):
        # odd are labeled bicycle and even person
        i = int(frames[0][0][0][0]) - 1
        label = self.labels[i % 2 + 1]
        return np.array([label])


class DummyNoInputFunction(AbstractFunction):
    @decorators.setup(cacheable=False, function_type="test", batchable=False)
    def setup(self, *args, **kwargs):
        pass

    @property
    def name(self) -> str:
        return "DummyNoInputFunction"

    @decorators.forward(
        input_signatures=[],
        output_signatures=[
            PandasDataframe(
                columns=["label"],
                column_types=[NdArrayType.STR],
                column_shapes=[(None,)],
            )
        ],
    )
    def forward(self, df: pd.DataFrame) -> pd.DataFrame:
        ret = pd.DataFrame([{"label": "DummyNoInputFunction"}])
        return ret


class DummyLLM(AbstractFunction):
    @property
    def name(self) -> str:
        return "DummyLLM"

    @decorators.setup(cacheable=True, function_type="chat-completion", batchable=True)
    def setup(self, *args, **kwargs):
        pass

    @decorators.forward(
        input_signatures=[
            PandasDataframe(
                columns=["query", "content", "prompt"],
                column_types=[
                    NdArrayType.STR,
                    NdArrayType.STR,
                    NdArrayType.STR,
                ],
                column_shapes=[(1,), (1,), (None,)],
            )
        ],
        output_signatures=[
            PandasDataframe(
                columns=["response"],
                column_types=[
                    NdArrayType.STR,
                ],
                column_shapes=[(1,)],
            )
        ],
    )
    def forward(self, text_df):
        queries = text_df[text_df.columns[0]]
        content = text_df[text_df.columns[0]]

        if len(text_df.columns) > 1:
            queries = text_df.iloc[:, 0]
            content = text_df.iloc[:, 1]

        prompt = None
        if len(text_df.columns) > 2:
            prompt = text_df.iloc[0, 2]

        results = []
        for query, content in zip(queries, content):
            results.append(("" if prompt is None else prompt) + query + " " + content)

        df = pd.DataFrame({"response": results})
        # Make it slower
        time.sleep(1)
        return df


class DummyAccessColumnByName(AbstractFunction):
    @decorators.setup(cacheable=False, function_type="test", batchable=False)
    def setup(self, *args, **kwargs):
        pass

    @property
    def name(self) -> str:
        return "DummyAccessColumnByName"

    @decorators.forward(
        input_signatures=[
            PandasDataframe(
                columns=["input1", "input2"],
                column_types=[NdArrayType.ANYTYPE, NdArrayType.ANYTYPE],
                column_shapes=[(None,), (None,)],
            )
        ],
        output_signatures=[
            PandasDataframe(
                columns=["output1", "output2"],
                column_types=[NdArrayType.ANYTYPE, NdArrayType.ANYTYPE],
                column_shapes=[(None,), (None,)],
            )
        ],
    )
    def forward(self, df: pd.DataFrame) -> pd.DataFrame:
        ret = pd.DataFrame(
            [{"output1": df["input1"] is not None, "output2": df["input2"] is not None}]
        )
        return ret
