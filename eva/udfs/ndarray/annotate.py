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
import cv2
import numpy as np
import pandas as pd

from eva.udfs.abstract.abstract_udf import AbstractUDF

color = (207, 248, 64)
thickness = 4


class Annotate(AbstractUDF):
    def setup(self):
        pass

    @property
    def name(self):
        return "Annotate"

    def forward(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Crop the frame given the bbox - Crop(frame, bbox)
        If one of the side of the crop box is 0, it automatically sets it to 1 pixel

        Returns:
            ret (pd.DataFrame): The cropped frame.
        """

        def annotate(row: pd.Series) -> np.ndarray:
            row = row.to_list()
            frame = row[0]
            labels = row[1]
            bboxes = row[2]

            for bbox in bboxes: 

                x1, y1, x2, y2 = np.asarray(bbox, dtype="int")

                # TODO: make sure the bbox is valid. Do we need to though?

                x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)

                frame = cv2.rectangle(frame, (x1, y1), (x2, y2), color, thickness)

                # cv2.putText(frame, label, (x1, y1-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, thickness)

            return frame

        ret = pd.DataFrame()
        ret["annotated_frame_array"] = df.apply(annotate, axis=1)
        return ret
