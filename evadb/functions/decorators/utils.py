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
from typing import List, Type

from evadb.catalog.models.function_io_catalog import FunctionIOCatalogEntry
from evadb.functions.abstract.abstract_function import AbstractFunction
from evadb.utils.errors import FunctionIODefinitionError

HELP_LINK = 'https://evadb.readthedocs.io/en/stable/source/reference/ai/custom-ai-function.html#yolo-object-detection'
HELP_DESCRIPTOR = 'Refer to the documentation for more information: ' + HELP_LINK

def load_io_from_function_decorators(
    function: Type[AbstractFunction], is_input=False
) -> List[Type[FunctionIOCatalogEntry]]:
    """Load the inputs/outputs from the function decorators and return a list of FunctionIOCatalogEntry objects

    Args:
        function (Object): Function object
        is_input (bool, optional): True if inputs are to be loaded. Defaults to False.

    Returns:
        Type[FunctionIOCatalogEntry]: FunctionIOCatalogEntry object created from the input decorator in setup
    """
    tag_key = "input" if is_input else "output"
    io_signature = None
    if hasattr(function.forward, "tags") and tag_key in function.forward.tags:
        io_signature = function.forward.tags[tag_key]
    else:
        # Attempt to populate from the parent class and stop at the first parent class
        # where the required tags are found.
        for base_class in function.__bases__:
            if hasattr(base_class, "forward") and hasattr(base_class.forward, "tags"):
                if tag_key in base_class.forward.tags:
                    io_signature = base_class.forward.tags[tag_key]
                    break

    if io_signature is None:
        if not hasattr(function.forward, "tags"):
            raise FunctionIODefinitionError("No tags found in the forward function. Please make sure to use the @forward decorator with both input and output signatures.\n"+HELP_DESCRIPTOR)

        if hasattr(function.forward, "tags") and tag_key not in function.forward.tags:
            raise FunctionIODefinitionError(f"Could not detect {tag_key} signature for {function}. Please check the @forward decorator for {function}.\n"+HELP_DESCRIPTOR)

    if (type(io_signature) is list) and (len(io_signature) == 0):
        raise FunctionIODefinitionError(f"Could not detect {tag_key} signature for {function}. Please check the @forward decorator for {function}.\n"+HELP_DESCRIPTOR)

    # assert (
    #     io_signature is not None
    # ), f"Cannot infer io signature from the decorator for {function}. Please check the {tag_key} of the forward function."

    result_list = []
    for io in io_signature:
        result_list.extend(io.generate_catalog_entries(is_input))
    return result_list
