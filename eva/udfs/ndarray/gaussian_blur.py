# coding=utf-8
# Copyright 2018-2023 EVA
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
import cv2
import numpy as np
import pandas as pd

from eva.catalog.catalog_type import NdArrayType
from eva.udfs.abstract.abstract_udf import AbstractUDF
from eva.udfs.decorators.decorators import forward, setup
from eva.udfs.decorators.io_descriptors.data_types import PandasDataframe


class GaussianBlur(AbstractUDF):
    @setup(
        cacheable=False,
        udf_type="cv2-transformation",
        batchable=True,
        parallelizable=True,
    )
    def setup(self):
        pass

    @property
    def name(self):
        return "GaussianBlur"

    @forward(
        input_signatures=[
            PandasDataframe(
                columns=["data"],
                column_types=[NdArrayType.FLOAT32],
                column_shapes=[(None, None, 3)],
            )
        ],
        output_signatures=[
            PandasDataframe(
                columns=["blurred_frame_array"],
                column_types=[NdArrayType.FLOAT32],
                column_shapes=[(None, None, 3)],
            )
        ],
    )
    def forward(self, frame: pd.DataFrame) -> pd.DataFrame:
        """
        Apply Gaussian Blur to the frame

         Returns:
             ret (pd.DataFrame): The modified frame.
        """

        def gaussianBlur(row: pd.Series) -> np.ndarray:
            row = row.to_list()
            frame = row[0]

            frame = cv2.GaussianBlur(frame, (5, 5), cv2.BORDER_DEFAULT)
            # since cv2 by default reads an image in BGR
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            return frame

        ret = pd.DataFrame()
        ret["blurred_frame_array"] = frame.apply(gaussianBlur, axis=1)
        return ret
