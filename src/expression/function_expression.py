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
import pandas as pd
from enum import Enum, unique
from typing import Callable

from src.constants import NO_GPU
from src.executor.execution_context import Context
from src.expression.abstract_expression import AbstractExpression, \
    ExpressionType
from src.models.storage.batch import Batch
from src.udfs.gpu_compatible import GPUCompatible


@unique
class ExecutionMode(Enum):
    # EXEC means the executed function mutates the batch frame and returns
    # it back. The frame batch is mutated.
    EXEC = 1
    # EVAL function with return values
    EVAL = 2


class FunctionExpression(AbstractExpression):
    """
    Expression used for function evaluation
    Arguments:
        func (Callable): UDF or EVA built in function for performing
        operations on the

        mode (ExecutionMode): The mode in which execution needs to happen.
        Will just return the output in EVAL mode. EXEC mode updates the
        BatchFrame with output.

        is_temp (bool, default:False): In case of EXEC type, decides if the
        outcome needs to be stored in BatchFrame temporarily.

        output(str): The column to return after executing function

        output_obj(UdfIO): The catalog object corresponding to the func_output.
        To be populated by optimizer.

    """

    def __init__(self, func: Callable,
                 mode: ExecutionMode = ExecutionMode.EVAL, name=None,
                 is_temp: bool = False, output=None,
                 **kwargs):
        if mode == ExecutionMode.EXEC:
            assert name is not None

        super().__init__(ExpressionType.FUNCTION_EXPRESSION, **kwargs)
        self._context = Context()
        self._mode = mode
        self._name = name
        self._function = func
        self._is_temp = is_temp
        self._output = output
        self._output_obj = None

    def evaluate(self, batch: Batch):
        new_batch = Batch()
        for child in self.children:
            child_batch = child.evaluate(batch)
            new_batch = new_batch.merge_column_wise(child_batch)

        if new_batch.empty():
            new_batch = batch

        func = self._gpu_enabled_function()

        outcomes = func(new_batch.frames.to_numpy())
        outcomes = Batch(pd.DataFrame(outcomes))
        return outcomes.project([self._output])

    def _gpu_enabled_function(self):
        if isinstance(self._function, GPUCompatible):
            device = self._context.gpu_device()
            if device != NO_GPU:
                return self._function.to_device(device)
        return self._function
