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
import torch

from eva.udfs.contrib.decorators.ish.io_descriptors.eva_arguments import EvaArgument


class PyTorchTensor(EvaArgument):
    """EVA data type for PyTorch Tensor"""
    def __init__(self, shape=None, dtype=None) -> None:
        super().__init__()
        self.shape = shape
        self.dtype = dtype

    def check_type(self, input_object) -> bool:
        if self.dtype:
            if self.dtype == "int32":
                return isinstance(input_object, torch.Tensor) and (
                    input_object.dtype == torch.int32
                )
            elif self.dtype == "float16":
                return isinstance(input_object, torch.Tensor) and (
                    input_object.dtype == torch.float16
                )
            elif self.dtype == "float32":
                return isinstance(input_object, torch.Tensor) and (
                    input_object.dtype == torch.float32
                )

        else:
            return isinstance(input_object, torch.Tensor)

    def check_shape(self, input_object) -> bool:
        if self.shape:
            if input_object.shape != self.shape:
                return False

        return True

    def name(self):
        return "PyTorch Tensor"
