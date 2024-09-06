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

from evadb.configuration.constants import EvaDB_INSTALLATION_DIR
from evadb.database import EvaDBDatabase
from evadb.server.command_handler import execute_query_fetch_all

NDARRAY_DIR = "ndarray"
TUTORIALS_DIR = "tutorials"

DummyObjectDetector_function_query = """CREATE FUNCTION IF NOT EXISTS DummyObjectDetector
                  INPUT  (Frame_Array NDARRAY INT8(3, ANYDIM, ANYDIM))
                  OUTPUT (label NDARRAY STR(1))
                  TYPE  Classification
                  IMPL  '{}/../test/util.py';
        """.format(
    EvaDB_INSTALLATION_DIR
)

DummyMultiObjectDetector_function_query = """CREATE FUNCTION
                  IF NOT EXISTS  DummyMultiObjectDetector
                  INPUT  (Frame_Array NDARRAY INT8(3, ANYDIM, ANYDIM))
                  OUTPUT (labels NDARRAY STR(2))
                  TYPE  Classification
                  IMPL  '{}/../test/util.py';
        """.format(
    EvaDB_INSTALLATION_DIR
)

DummyFeatureExtractor_function_query = """CREATE FUNCTION
                  IF NOT EXISTS DummyFeatureExtractor
                  INPUT (Frame_Array NDARRAY UINT8(3, ANYDIM, ANYDIM))
                  OUTPUT (features NDARRAY FLOAT32(1, ANYDIM))
                  TYPE Classification
                  IMPL '{}/../test/util.py';
        """.format(
    EvaDB_INSTALLATION_DIR
)

DummyNoInputFunction_function_query = """CREATE FUNCTION
                  IF NOT EXISTS DummyNoInputFunction
                  IMPL '{}/../test/util.py';
        """.format(
    EvaDB_INSTALLATION_DIR
)

DummyLLM_function_query = """CREATE FUNCTION
                  IF NOT EXISTS DummyLLM
                  IMPL '{}/../test/util.py';
        """.format(
    EvaDB_INSTALLATION_DIR
)

DummyAccessColumnByName_function_query = """CREATE FUNCTION
                  IF NOT EXISTS DummyAccessColumnByName
                  IMPL '{}/../test/util.py';
        """.format(
    EvaDB_INSTALLATION_DIR
)

fuzzy_function_query = """CREATE FUNCTION IF NOT EXISTS FuzzDistance
                    INPUT (Input_Array1 NDARRAY ANYTYPE, Input_Array2 NDARRAY ANYTYPE)
                    OUTPUT (distance FLOAT(32, 7))
                    TYPE NdarrayFunction
                    IMPL "{}/functions/{}/fuzzy_join.py";
        """.format(
    EvaDB_INSTALLATION_DIR, NDARRAY_DIR
)

ArrayCount_function_query = """CREATE FUNCTION
            IF NOT EXISTS  ArrayCount
            INPUT (Input_Array NDARRAY ANYTYPE, Search_Key ANYTYPE)
            OUTPUT (key_count INTEGER)
            TYPE NdarrayFunction
            IMPL "{}/functions/{}/array_count.py";
        """.format(
    EvaDB_INSTALLATION_DIR, NDARRAY_DIR
)

Crop_function_query = """CREATE FUNCTION IF NOT EXISTS Crop
                INPUT  (Frame_Array NDARRAY UINT8(3, ANYDIM, ANYDIM),
                        bboxes NDARRAY FLOAT32(ANYDIM, 4))
                OUTPUT (Cropped_Frame_Array NDARRAY UINT8(3, ANYDIM, ANYDIM))
                TYPE  NdarrayFunction
                IMPL  "{}/functions/{}/crop.py";
        """.format(
    EvaDB_INSTALLATION_DIR, NDARRAY_DIR
)

Open_function_query = """CREATE FUNCTION IF NOT EXISTS Open
                INPUT (img_path TEXT(1000))
                OUTPUT (data NDARRAY UINT8(3, ANYDIM, ANYDIM))
                TYPE NdarrayFunction
                IMPL "{}/functions/{}/open.py";
        """.format(
    EvaDB_INSTALLATION_DIR, NDARRAY_DIR
)

Similarity_function_query = """CREATE FUNCTION IF NOT EXISTS Similarity
                    INPUT (Frame_Array_Open NDARRAY UINT8(3, ANYDIM, ANYDIM),
                           Frame_Array_Base NDARRAY UINT8(3, ANYDIM, ANYDIM),
                           Feature_Extractor_Name TEXT(100))
                    OUTPUT (distance FLOAT(32, 7))
                    TYPE NdarrayFunction
                    IMPL "{}/functions/{}/similarity.py";
        """.format(
    EvaDB_INSTALLATION_DIR, NDARRAY_DIR
)

Unnest_function_query = """CREATE FUNCTION IF NOT EXISTS Unnest
                INPUT  (inp NDARRAY ANYTYPE)
                OUTPUT (out ANYTYPE)
                TYPE  NdarrayFunction
                IMPL  "{}/functions/{}/unnest.py";
        """.format(
    EvaDB_INSTALLATION_DIR, NDARRAY_DIR
)

Fastrcnn_function_query = """CREATE FUNCTION IF NOT EXISTS FastRCNNObjectDetector
      INPUT  (Frame_Array NDARRAY UINT8(3, ANYDIM, ANYDIM))
      OUTPUT (labels NDARRAY STR(ANYDIM), bboxes NDARRAY FLOAT32(ANYDIM, 4),
                scores NDARRAY FLOAT32(ANYDIM))
      TYPE  Classification
      IMPL  '{}/functions/fastrcnn_object_detector.py';
      """.format(
    EvaDB_INSTALLATION_DIR
)

Yolo_function_query = """CREATE FUNCTION IF NOT EXISTS Yolo
      TYPE  ultralytics
      MODEL 'yolov8m.pt';
      """

face_detection_function_query = """CREATE FUNCTION IF NOT EXISTS FaceDetector
                  INPUT  (frame NDARRAY UINT8(3, ANYDIM, ANYDIM))
                  OUTPUT (bboxes NDARRAY FLOAT32(ANYDIM, 4),
                          scores NDARRAY FLOAT32(ANYDIM))
                  TYPE  FaceDetection
                  IMPL  '{}/functions/face_detector.py';
        """.format(
    EvaDB_INSTALLATION_DIR
)

Mvit_function_query = """CREATE FUNCTION IF NOT EXISTS MVITActionRecognition
        INPUT  (Frame_Array NDARRAY UINT8(3, 16, 224, 224))
        OUTPUT (labels NDARRAY STR(ANYDIM))
        TYPE  Classification
        IMPL  '{}/functions/mvit_action_recognition.py';
        """.format(
    EvaDB_INSTALLATION_DIR
)

Asl_function_query = """CREATE FUNCTION IF NOT EXISTS ASLActionRecognition
        INPUT  (Frame_Array NDARRAY UINT8(3, 16, 224, 224))
        OUTPUT (labels NDARRAY STR(ANYDIM))
        TYPE  Classification
        IMPL  '{}/functions/asl_action_recognition.py';
        """.format(
    EvaDB_INSTALLATION_DIR
)

norfair_obj_tracker_query = """CREATE FUNCTION IF NOT EXISTS NorFairTracker
                  IMPL  '{}/functions/trackers/nor_fair.py';
        """.format(
    EvaDB_INSTALLATION_DIR
)

Sift_function_query = """CREATE FUNCTION IF NOT EXISTS SiftFeatureExtractor
        IMPL  '{}/functions/sift_feature_extractor.py';
        """.format(
    EvaDB_INSTALLATION_DIR
)

Text_feat_function_query = """CREATE FUNCTION IF NOT EXISTS SentenceFeatureExtractor
        IMPL  '{}/functions/sentence_feature_extractor.py';
        """.format(
    EvaDB_INSTALLATION_DIR
)

mnistcnn_function_query = """CREATE FUNCTION IF NOT EXISTS MnistImageClassifier
        INPUT  (data NDARRAY (3, 28, 28))
        OUTPUT (label TEXT(2))
        TYPE  Classification
        IMPL  '{}/functions/mnist_image_classifier.py';
        """.format(
    EvaDB_INSTALLATION_DIR
)

chatgpt_function_query = """CREATE FUNCTION IF NOT EXISTS ChatGPT
        IMPL '{}/functions/chatgpt.py';
        """.format(
    EvaDB_INSTALLATION_DIR
)

yolo8n_query = """CREATE FUNCTION IF NOT EXISTS Yolo
            TYPE  ultralytics
            MODEL 'yolov8n.pt';
        """

stablediffusion_function_query = """CREATE FUNCTION IF NOT EXISTS StableDiffusion
        IMPL '{}/functions/stable_diffusion.py';
        """.format(
    EvaDB_INSTALLATION_DIR
)

dalle_function_query = """CREATE FUNCTION IF NOT EXISTS DallE
        IMPL '{}/functions/dalle.py';
        """.format(
    EvaDB_INSTALLATION_DIR
)

Upper_function_query = """CREATE FUNCTION IF NOT EXISTS UPPER
        INPUT  (input ANYTYPE)
        OUTPUT (output NDARRAY STR(ANYDIM))
        TYPE HelperFunction
        IMPL '{}/functions/helpers/upper.py';
        """.format(
    EvaDB_INSTALLATION_DIR
)

Lower_function_query = """CREATE FUNCTION IF NOT EXISTS LOWER
        INPUT  (input ANYTYPE)
        OUTPUT (output NDARRAY STR(ANYDIM))
        TYPE HelperFunction
        IMPL '{}/functions/helpers/lower.py';
        """.format(
    EvaDB_INSTALLATION_DIR
)

Concat_function_query = """CREATE FUNCTION IF NOT EXISTS CONCAT
        INPUT  (input ANYTYPE)
        OUTPUT (output NDARRAY STR(ANYDIM))
        TYPE HelperFunction
        IMPL '{}/functions/helpers/concat.py';
        """.format(
    EvaDB_INSTALLATION_DIR
)


def init_builtin_functions(db: EvaDBDatabase, mode: str = "debug") -> None:
    """Load the built-in functions into the system during system bootstrapping.

    The function loads a set of pre-defined function queries based on the `mode` argument.
    In 'debug' mode, the function loads debug functions along with release functions.
    In 'release' mode, only release functions are loaded. In addition, in 'debug' mode,
    the function loads a smaller model to accelerate the test suite time.

    Args:G
        mode (str, optional): The mode for loading functions, either 'debug' or 'release'.
        Defaults to 'debug'.

    """

    # Attempting to import torch module
    # It is necessary to import torch before to avoid encountering a
    # "RuntimeError: random_device could not be read"
    # The suspicion is that importing torch prior to decord resolves this issue
    try:
        import torch  # noqa: F401
    except ImportError:
        pass

    # Enable environment variables
    # Relevant for transformer-based models
    import os

    os.environ["PROTOCOL_BUFFERS_PYTHON_IMPLEMENTATION"] = "python"
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    # list of function queries to load
    queries = [
        mnistcnn_function_query,
        Fastrcnn_function_query,
        ArrayCount_function_query,
        Crop_function_query,
        Open_function_query,
        Similarity_function_query,
        norfair_obj_tracker_query,
        chatgpt_function_query,
        face_detection_function_query,
        # Mvit_function_query,
        Sift_function_query,
        Yolo_function_query,
        stablediffusion_function_query,
        dalle_function_query,
        Upper_function_query,
        Lower_function_query,
        Concat_function_query,
    ]

    # if mode is 'debug', add debug functions
    if mode == "debug":
        queries.extend(
            [
                DummyObjectDetector_function_query,
                DummyMultiObjectDetector_function_query,
                DummyFeatureExtractor_function_query,
                DummyNoInputFunction_function_query,
                DummyLLM_function_query,
                DummyAccessColumnByName_function_query,
            ]
        )

    # execute each query in the list of function queries
    # ignore exceptions during the bootstrapping phase due to missing packages
    for query in queries:
        try:
            execute_query_fetch_all(
                db, query, do_not_print_exceptions=False, do_not_raise_exceptions=True
            )
        except Exception:
            pass
