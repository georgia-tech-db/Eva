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

import numpy as np
import pytest
import torch

from eva.io_descriptors.eva_data_types import NumpyArray, PyTorchTensor
from eva.udfs.decorators.udf_decorators import forward
from eva.utils.errors import UDFInputOutputTypeException


@forward(input_signatures=[NumpyArray()], output_signature=NumpyArray())
def forward_fn_numpy_no_constraints(self_obj, np_array):
    ans = np.asarray(np.sum(np_array))
    return ans


@forward(
    input_signatures=[NumpyArray(dtype="int32", shape=(2, 1))],
    output_signature=NumpyArray(dtype="int32", shape=(1, 1)),
)
def forward_fn_numpy_input_output_constraint(self_obj, np_array):
    ans = np.sum(np_array, axis=0)
    ans = ans.astype(np.int32)
    return np.expand_dims(ans, 1)


@forward(
    input_signatures=[NumpyArray(dtype="int32", shape=(2, 1))],
    output_signature=NumpyArray(dtype="int32", shape=(3, 1)),
)
def forward_fn_numpy_output_mismatch(self_obj, np_array):
    ans = np.sum(np_array, axis=0)
    ans = ans.astype(np.int32)
    return np.expand_dims(ans, 1)


@forward(input_signatures=[PyTorchTensor()], output_signature=PyTorchTensor())
def forward_fn_pytorch_no_constraints(self_obj, torch_tensor):
    ans = torch.sum(torch_tensor)
    return ans


@forward(
    input_signatures=[PyTorchTensor(dtype="int32", shape=(2, 1))],
    output_signature=PyTorchTensor(dtype="int32", shape=(1, 1)),
)
def forward_fn_pytorch_input_output_constraint(self_obj, torch_tensor):
    ans = torch.sum(torch_tensor)
    ans = ans.to(torch.int32)
    ans = torch.unsqueeze(ans, 0)
    ans = torch.unsqueeze(ans, 0)
    return ans


class UdfDecoratorTest(unittest.TestCase):
    @pytest.mark.torchtest
    def test_forward_fn_numpy_no_constraints(self):
        np_arr = np.ones((10, 1))
        ans = forward_fn_numpy_no_constraints(None, np_arr)
        self.assertTrue(np.equal(ans, 10))

    @pytest.mark.torchtest
    def test_forward_fn_numpy_with_constraints(self):
        # all the constraints are satisfied
        np_arr = np.ones((2, 1), dtype=np.int32)
        ans = forward_fn_numpy_input_output_constraint(None, np_arr)
        self.assertTrue(np.equal(ans, 2))

        # input shape is mismatched
        np_arr = np.ones((1, 2), dtype=np.int32)
        with self.assertRaises(UDFInputOutputTypeException):
            ans = forward_fn_numpy_input_output_constraint(None, np_arr)

        # input data type is mismatched
        np_arr = np.ones((1, 2), dtype=np.float64)
        with self.assertRaises(UDFInputOutputTypeException):
            ans = forward_fn_numpy_input_output_constraint(None, np_arr)

    @pytest.mark.torchtest
    def test_forward_fn_numpy_output_mismatch(self):
        # the shape of output is different so raises an exception
        np_arr = np.ones((1, 2), dtype=np.float64)
        with self.assertRaises(UDFInputOutputTypeException):
            forward_fn_numpy_output_mismatch(None, np_arr)

    @pytest.mark.torchtest
    def test_forward_fn_numpy_raise_exception(self):
        # the numpy array cannot be reshaped to the required shape. hence it throws an exception
        np_arr = np.ones((3, 1), dtype=np.int32)
        with self.assertRaises(UDFInputOutputTypeException):
            forward_fn_numpy_input_output_constraint(None, np_arr)

    @pytest.mark.torchtest
    def test_forward_fn_pytorch_no_constraints(self):
        torch_tensor = torch.ones((2, 1))
        self.assertTrue(
            torch.eq(forward_fn_pytorch_no_constraints(None, torch_tensor), 2)
        )

    @pytest.mark.torchtest
    def test_forward_fn_pytorch_with_constraints(self):
        # all the constraints are satisfied
        torch_tensor = torch.ones((2, 1), dtype=torch.int32)
        self.assertTrue(
            torch.eq(forward_fn_pytorch_input_output_constraint(None, torch_tensor), 2)
        )

        # input shape is mismatched
        torch_tensor = torch.ones((1, 2))
        with self.assertRaises(UDFInputOutputTypeException):
            forward_fn_pytorch_input_output_constraint(None, torch_tensor)

        # input data type is mismatched
        torch_tensor = torch.ones((1, 2), dtype=torch.float64)
        with self.assertRaises(UDFInputOutputTypeException):
            forward_fn_pytorch_input_output_constraint(None, torch_tensor)

    @pytest.mark.torchtest
    def test_forward_fn_pytorch_raise_exception(self):
        # the tensor cannot be reshaped to the required shape
        torch_tensor = torch.ones((1, 3), dtype=torch.float64)
        with self.assertRaises(UDFInputOutputTypeException):
            forward_fn_pytorch_input_output_constraint(None, torch_tensor)
