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
from dataclasses import dataclass
from typing import Callable, List, Tuple

import numpy as np
import pandas as pd

from evadb.catalog.models.function_catalog import FunctionCatalogEntry
from evadb.catalog.models.function_io_catalog import FunctionIOCatalogEntry
from evadb.constants import NO_GPU
from evadb.executor.execution_context import Context
from evadb.expression.abstract_expression import AbstractExpression, ExpressionType
from evadb.functions.gpu_compatible import GPUCompatible
from evadb.models.storage.batch import Batch
from evadb.parser.alias import Alias
from evadb.utils.kv_cache import DiskKVCache
from evadb.utils.logging_manager import logger
from evadb.utils.stats import FunctionStats


class FunctionExpression(AbstractExpression):
    """
    Consider FunctionExpression: ObjDetector -> (labels, boxes)

    `output`: If the user wants only subset of outputs. Eg,
    ObjDetector.labels the parser with set output to 'labels'

    `output_objs`: It is populated by the binder. In case the
    output is None, the binder sets output_objs to list of all
    output columns of the FunctionExpression. Eg, ['labels',
    'boxes']. Otherwise, only the output columns.

    FunctionExpression also needs to prepend its alias to all the
    projected columns. This is important as other parts of the query
    might be assessing the results using alias. Eg,

    `Select Detector.labels
     FROM Video JOIN LATERAL ObjDetector AS Detector;`
    """

    def __init__(
        self,
        func: Callable,
        name: str,
        output: str = None,
        alias: Alias = None,
        **kwargs,
    ):
        super().__init__(ExpressionType.FUNCTION_EXPRESSION, **kwargs)
        self._context = Context()
        self._name = name
        self._function = func
        self._function_instance = None
        self._output = output
        self.alias = alias
        self.function_obj: FunctionCatalogEntry = None
        self.output_objs: List[FunctionIOCatalogEntry] = []
        self.projection_columns: List[str] = []
        self._cache: FunctionExpressionCache = None
        self._stats = FunctionStats()

    @property
    def name(self):
        return self._name

    @property
    def output(self):
        return self._output

    @property
    def col_alias(self):
        col_alias_list = []
        if self.alias is not None:
            for col in self.alias.col_names:
                col_alias_list.append("{}.{}".format(self.alias.alias_name, col))
        return col_alias_list

    @property
    def function(self):
        return self._function

    @function.setter
    def function(self, func: Callable):
        self._function = func

    def enable_cache(self, cache: "FunctionExpressionCache"):
        self._cache = cache
        return self

    def has_cache(self):
        return self._cache is not None

    def consolidate_stats(self):
        if self.function_obj is None:
            return

        # if the function expression support cache only approximate using cache_miss entries.
        if self.has_cache() and self._stats.cache_misses > 0:
            cost_per_func_call = (
                self._stats.timer.total_elapsed_time / self._stats.cache_misses
            )
        else:
            cost_per_func_call = self._stats.timer.total_elapsed_time / (
                self._stats.num_calls
            )

        if abs(self._stats.prev_cost - cost_per_func_call) > cost_per_func_call / 10:
            self._stats.prev_cost = cost_per_func_call

    def evaluate(self, batch: Batch, **kwargs) -> Batch:
        func = self._gpu_enabled_function()
        # record the time taken for the function execution
        # note the function might be using cache
        with self._stats.timer:
            # apply the function and project the required columns
            outcomes = self._apply_function_expression(func, batch, **kwargs)

            # process outcomes only if output is not empty
            if outcomes.frames.empty is False:
                outcomes = outcomes.project(self.projection_columns)
                outcomes.modify_column_alias(self.alias)

        # record the number of function calls
        self._stats.num_calls += len(batch)

        # try persisting the stats to catalog and do not crash if we fail in doing so
        try:
            self.consolidate_stats()
        except Exception as e:
            logger.warn(
                f"Persisting FunctionExpression {str(self)} stats failed with {str(e)}"
            )

        return outcomes

    def signature(self) -> str:
        """It constructs the signature of the function expression.
        It traverses the children (function arguments) and compute signature for each
        child. The output is in the form `function_name[row_id](arg1, arg2, ...)`.

        Returns:
            str: signature string
        """
        child_sigs = []
        for child in self.children:
            child_sigs.append(child.signature())

        func_sig = f"{self.name}[{self.function_obj.row_id}]({','.join(child_sigs)})"
        return func_sig

    def _gpu_enabled_function(self):
        if self._function_instance is None:
            self._function_instance = self.function()
            if isinstance(self._function_instance, GPUCompatible):
                device = self._context.gpu_device()
                if device != NO_GPU:
                    self._function_instance = self._function_instance.to_device(device)
        return self._function_instance

    def _apply_function_expression(self, func: Callable, batch: Batch, **kwargs):
        """
        If cache is not enabled, call the func on the batch and return.
        If cache is enabled:
        (1) iterate over the input batch rows and check if we have the value in the
        cache;
        (2) for all cache miss rows, call the func;
        (3) iterate over each cache miss row and store the results in the cache;
        (4) stitch back the partial cache results with the new func calls.
        """
        func_args = Batch.merge_column_wise(
            [child.evaluate(batch, **kwargs) for child in self.children]
        )

        # Rename the columns according to args from input signatures
        if self.function_obj is not None:
            col_renaming = {
                original_col: arg.name
                for original_col, arg in zip(func_args.columns, self.function_obj.args)
            }
            func_args.rename(col_renaming)

        if not self._cache:
            return func_args.apply_function_expression(func)

        output_cols = [obj.name for obj in self.function_obj.outputs]

        # 1. check cache
        # We are required to iterate over the batch row by row and check the cache.
        # This can hurt performance, as we have to stitch together columns to generate
        # row tuples. Is there an alternative approach we can take?

        results = np.full([len(batch), len(output_cols)], None)
        cache_keys = func_args
        # cache keys can be different from func_args
        # see optimize_cache_key
        if self._cache.key:
            cache_keys = Batch.merge_column_wise(
                [child.evaluate(batch, **kwargs) for child in self._cache.key]
            )
            assert len(cache_keys) == len(batch), "Not all rows have the cache key"

        cache_miss = np.full(len(batch), True)
        for idx, (_, key) in enumerate(cache_keys.iterrows()):
            val = self._cache.store.get(key.to_numpy())
            results[idx] = val
            cache_miss[idx] = val is None

        # log the cache misses
        self._stats.cache_misses += sum(cache_miss)

        # 2. call func for cache miss rows
        if cache_miss.any():
            func_args = func_args[list(cache_miss)]
            cache_miss_results = func_args.apply_function_expression(func)

            # 3. set the cache results
            missing_keys = cache_keys[list(cache_miss)]
            for key, value in zip(
                missing_keys.iterrows(), cache_miss_results.iterrows()
            ):
                self._cache.store.set(key[1].to_numpy(), value[1].to_numpy())

            # 4. merge the cache results
            results[cache_miss] = cache_miss_results.to_numpy()

        # 5. return the correct batch
        return Batch(pd.DataFrame(results, columns=output_cols))

    def __str__(self) -> str:
        args = [str(child) for child in self.children]
        expr_str = f"{self.name}({','.join(args)})"
        return expr_str

    def __eq__(self, other):
        is_subtree_equal = super().__eq__(other)
        if not isinstance(other, FunctionExpression):
            return False
        return (
            is_subtree_equal
            and self.name == other.name
            and self.output == other.output
            and self.alias == other.alias
            and self.function == other.function
            and self.output_objs == other.output_objs
            and self._cache == other._cache
        )

    def __hash__(self) -> int:
        return hash(
            (
                super().__hash__(),
                self.name,
                self.output,
                self.alias,
                self.function,
                tuple(self.output_objs),
                self._cache,
            )
        )


@dataclass(frozen=True)
class FunctionExpressionCache:
    """dataclass for cache-related attributes

    Args:
        key (`AbstractExpression`): the list of abstract expression to evaluate to get the key. If `None`, use the function arguments as the key. This is useful when the system wants to use logically equivalent columns as the key (e.g., frame number instead of frame data).
        store (`DiskKVCache`): the cache object to get/set key-value pairs
    """

    key: Tuple[AbstractExpression]
    store: DiskKVCache = None
