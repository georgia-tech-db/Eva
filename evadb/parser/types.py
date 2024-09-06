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

from evadb.utils.generic_utils import EvaDBEnum


class ColumnConstraintEnum(EvaDBEnum):
    NOTNULL  # noqa: F821
    DEFAULT  # noqa: F821
    PRIMARY  # noqa: F821
    UNIQUE  # noqa: F821


class StatementType(EvaDBEnum):
    """
    Manages EvaDBEnums for all the sql-like statements supported
    """

    SELECT  # noqa: F821
    CREATE  # noqa: F821
    RENAME  # noqa: F821
    DROP_OBJECT  # noqa: F821
    INSERT  # noqa: F821
    DELETE  # noqa: F821
    CREATE_FUNCTION  # noqa: F821
    LOAD_DATA  # noqa: F821
    SHOW  # noqa: F821
    EXPLAIN  # noqa: F821
    CREATE_INDEX  # noqa: F821
    CREATE_DATABASE  # noqa: F821
    USE  # noqa: F821
    SET  # noqa: F821
    CREATE_JOB  # noqa: F821
    START # noqa: F821
    STOP # noqa: F821
    # add other types


class ParserOrderBySortType(EvaDBEnum):
    """
    Manages EvaDBEnums for all order by sort types
    """

    ASC  # noqa: F821
    DESC  # noqa: F821


class JoinType(EvaDBEnum):
    LATERAL_JOIN  # noqa: F821
    INNER_JOIN  # noqa: F821


class FileFormatType(EvaDBEnum):
    VIDEO  # noqa: F821
    CSV  # noqa: F821
    IMAGE  # noqa: F821
    DOCUMENT  # noqa: F821
    PDF  # noqa: F821


class ShowType(EvaDBEnum):
    FUNCTIONS  # noqa: F821
    TABLES  # noqa: F821
    CONFIGS  # noqa: F821
    DATABASES  # noqa: F821


class FunctionType(EvaDBEnum):
    EXTRACT_OBJECT  # noqa: F821


class ObjectType(EvaDBEnum):
    TABLE  # noqa: F821
    FUNCTION  # noqa: F821
    INDEX  # noqa: F821
    DATABASE  # noqa: F821
    JOB  # noqa: F821
