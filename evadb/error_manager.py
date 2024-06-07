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
from enum import Enum


class ErrorCode:
    def __init__(self, code, message=""):
        self.code = code
        self.default_message = message

    def __str__(self):
        return f"[{self.code}] {self.default_message}"

class ErrorManager:
    # Generic Error
    ERROR_GENERIC = ErrorCode(0, "Error")

    # Expected-Type Errors
    EXPECTED_SELECTION_STATEMENT = ErrorCode(100, "Expected a select statement")
    EXPECTED_CREATE_TABLE_STATEMENT = ErrorCode(101, "Expected a create table statement")
    EXPECTED_SHOW_STATEMENT = ErrorCode(102, "Expected a show statement")
    EXPECTED_INSERT_STATEMENT = ErrorCode(103, "Expected an insert statement")
    EXPECTED_EXPLAIN_STATEMENT = ErrorCode(104, "Expected an explain statement")
    EXPECTED_LOAD_STATEMENT = ErrorCode(105, "Expected a load statement")
    EXPECTED_DROP_OBJECT_STATEMENT = ErrorCode(106, "Expected a drop object statement")
    EXPECTED_RENAME_STATEMENT = ErrorCode(107, "Expected a rename statement")
    EXPECTED_CREATE_FUNCTION_STATEMENT = ErrorCode(108, "Expected a create function statement")
    EXPECTED_COLUMNS_NUMBER_MISMATCH = ErrorCode(109, "Unexpected number of columns")
    QUERY_EXPECTS_ONE_CHILD = ErrorCode(110, "Query expects one child")
    EXPECTED_API_TOKEN_SET = ErrorCode(111, "API token expected to be se.")
    EXPECTED_PD_DF = ErrorCode(112, "Expected a Pandas DataFrame")

    # Index Errors
    CANNOT_CREATE_INDEX_ON_MULIPLE_COLUMN = ErrorCode(1100, "Index cannot be created on more than 1 column")
    CREATE_INDEX_ONLY_ON_EXISTING_TABLE = ErrorCode(1101, "Index can only be created on an existing table")
    CANNOT_CREATE_INDEX_ON_NONEXISTANT_COLUMN = ErrorCode(1102, "Index is created on non-existent column")
    INDEX_INPUT_TYPE_MISMATCH = ErrorCode(1103, "Index input type is mismatched")
    INDEX_INPUT_DIM_MISMATCH = ErrorCode(1104, "Index input dimensions are mismatched")
    CREATE_INDEX_FIRST = ErrorCode(1105, "Create an index first")

    # Type Errors
    UNSUPPORTED_TYPE = ErrorCode(2100, "Type not supported")
    UNSUPPORTED_OPERATION = ErrorCode(2101, "Operation not supported")
    UNSUPPORTED_CLAUSE = ErrorCode(2102, "Clause not supported")
    UNSUPPORTED_LIBRARY = ErrorCode(2103, "Library not supported")
    CONCURRENT_CALLS_NOT_SUPPORTED = ErrorCode(2104, "Concurrent queries not supported")

    # Not Found/Already Exists Errors
    TABLE_NOT_FOUND = ErrorCode(3100, "Table not found")
    TABLE_ALREADY_EXISTS = ErrorCode(3101, "Table already exists")
    DIRECTORY_NOT_FOUND = ErrorCode(3102, "Directory not found")
    DIRECTORY_ALREADY_EXISTS = ErrorCode(3103, "Directory already exists")
    FILE_NOT_FOUND = ErrorCode(3104, "File not found")
    FILE_ALREADY_EXISTS = ErrorCode(3105, "File already exists")
    KEY_NOT_FOUND = ErrorCode(3106, "Key not found")

    # Failed-to Errors
    DROP_TABLE_FAILED = ErrorCode(4100, "DROP table failed")
    VECTOR_STORE_HANDLER_INITALIZATION_FAILED = ErrorCode(4101, "Initialization of vector store failed")
    RELATION_EXECUTE_FAILED = ErrorCode(4102, "Relation execute failed")

    # Not implemented
    NOT_IMPLEMENTED = ErrorCode(9999, "Functionality not implemented for current use-case.")

    @staticmethod
    def get_error_message(error_code, additional_message=None):
        if additional_message:
            return f"{error_code} Details: {additional_message}"
        return str(error_code)