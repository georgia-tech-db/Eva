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
from evadb.parser.create_function_statement import CreateFunctionStatement
from evadb.parser.create_statement import (
    CreateDatabaseStatement,
    CreateJobStatement,
    CreateTableStatement,
)
from evadb.parser.drop_object_statement import DropObjectStatement
from evadb.parser.explain_statement import ExplainStatement
from evadb.parser.insert_statement import InsertTableStatement
from evadb.parser.load_statement import LoadDataStatement
from evadb.parser.parser import Parser
from evadb.parser.rename_statement import RenameTableStatement
from evadb.parser.select_statement import SelectStatement
from evadb.parser.set_statement import SetStatement
from evadb.parser.show_statement import ShowStatement
from evadb.parser.start_scheduler_statement import StartSchedulerStatement
from evadb.parser.stop_scheduler_statement import StopSchedulerStatement
from evadb.parser.types import ObjectType
from evadb.parser.use_statement import UseStatement

# List of statements for which we omit binder and optimizer and pass the statement
# directly to the executor.
SKIP_BINDER_AND_OPTIMIZER_STATEMENTS = (
    CreateDatabaseStatement,
    CreateJobStatement,
    UseStatement,
    SetStatement,
    StartSchedulerStatement,
    StopSchedulerStatement,
)


def parse_expression(expr: str):
    mock_query = f"SELECT {expr} FROM DUMMY;"
    stmt = Parser().parse(mock_query)[0]
    assert isinstance(stmt, SelectStatement), "Expected a select statement"
    return stmt.target_list


def parse_predicate_expression(expr: str):
    mock_query = f"SELECT * FROM DUMMY WHERE {expr};"
    stmt = Parser().parse(mock_query)[0]
    assert isinstance(stmt, SelectStatement), "Expected a select statement"
    return stmt.where_clause


def parse_table_clause(expr: str, chunk_size: int = None, chunk_overlap: int = None):
    mock_query_parts = [f"SELECT * FROM {expr}"]
    if chunk_size is not None:
        mock_query_parts.append(f"CHUNK_SIZE {chunk_size}")
    if chunk_overlap is not None:
        mock_query_parts.append(f"CHUNK_OVERLAP {chunk_overlap}")
    mock_query_parts.append(";")
    mock_query = " ".join(mock_query_parts)
    stmt = Parser().parse(mock_query)[0]
    assert isinstance(stmt, SelectStatement), "Expected a select statement"
    assert stmt.from_table.is_table_atom
    return stmt.from_table


def parse_create_function(
    function_name: str,
    if_not_exists: bool,
    function_file_path: str,
    type: str,
    **kwargs,
):
    mock_query = (
        f"CREATE FUNCTION IF NOT EXISTS {function_name}"
        if if_not_exists
        else f"CREATE FUNCTION {function_name}"
    )
    if type is not None:
        mock_query += f" TYPE {type}"
        task, model = kwargs["task"], kwargs["model"]
        if task is not None and model is not None:
            mock_query += f" TASK '{task}' MODEL '{model}'"
    else:
        mock_query += f" IMPL '{function_file_path}'"
    mock_query += ";"

    stmt = Parser().parse(mock_query)[0]
    assert isinstance(
        stmt, CreateFunctionStatement
    ), "Expected a create function statement"
    return stmt


def parse_create_table(table_name: str, if_not_exists: bool, columns: str, **kwargs):
    mock_query = (
        f"CREATE TABLE IF NOT EXISTS {table_name} ({columns});"
        if if_not_exists
        else f"CREATE TABLE {table_name} ({columns});"
    )
    stmt = Parser().parse(mock_query)[0]
    assert isinstance(stmt, CreateTableStatement), "Expected a create table statement"
    return stmt


def parse_show(show_type: str, **kwargs):
    mock_query = f"SHOW {show_type};"
    stmt = Parser().parse(mock_query)[0]
    assert isinstance(stmt, ShowStatement), "Expected a show statement"
    return stmt


def parse_explain(query: str, **kwargs):
    mock_query = f"EXPLAIN {query};"
    stmt = Parser().parse(mock_query)[0]
    assert isinstance(stmt, ExplainStatement), "Expected a explain statement"
    return stmt


def parse_insert(table_name: str, columns: str, values: str, **kwargs):
    mock_query = f"INSERT INTO {table_name} {columns} VALUES {values};"
    stmt = Parser().parse(mock_query)[0]
    assert isinstance(stmt, InsertTableStatement), "Expected a insert statement"
    return stmt


def parse_load(table_name: str, file_regex: str, format: str, **kwargs):
    mock_query = f"LOAD {format.upper()} '{file_regex}' INTO {table_name};"
    stmt = Parser().parse(mock_query)[0]
    assert isinstance(stmt, LoadDataStatement), "Expected a load statement"
    return stmt


def parse_drop(object_type: ObjectType, name: str, if_exists: bool):
    mock_query = f"DROP {object_type}"
    mock_query = (
        f" {mock_query} IF EXISTS {name} " if if_exists else f"{mock_query} {name}"
    )
    mock_query += ";"

    stmt = Parser().parse(mock_query)[0]
    assert isinstance(stmt, DropObjectStatement), "Expected a drop object statement"
    return stmt


def parse_drop_table(table_name: str, if_exists: bool):
    return parse_drop(ObjectType.TABLE, table_name, if_exists)


def parse_drop_function(function_name: str, if_exists: bool):
    return parse_drop(ObjectType.FUNCTION, function_name, if_exists)


def parse_drop_index(index_name: str, if_exists: bool):
    return parse_drop(ObjectType.INDEX, index_name, if_exists)


def parse_drop_database(database_name: str, if_exists: bool):
    return parse_drop(ObjectType.DATABASE, database_name, if_exists)


def parse_query(query):
    stmt = Parser().parse(query)
    assert len(stmt) == 1
    return stmt[0]


def parse_lateral_join(expr: str, alias: str):
    mock_query = f"SELECT * FROM DUMMY JOIN LATERAL {expr} AS {alias};"
    stmt = Parser().parse(mock_query)[0]
    assert isinstance(stmt, SelectStatement), "Expected a select statement"
    assert stmt.from_table.is_join()
    return stmt.from_table.join_node.right


def parse_create_vector_index(index_name: str, table_name: str, expr: str, using: str):
    mock_query = f"CREATE INDEX {index_name} ON {table_name} ({expr}) USING {using};"
    stmt = Parser().parse(mock_query)[0]
    return stmt


def parse_sql_orderby_expr(expr: str):
    mock_query = f"SELECT * FROM DUMMY ORDER BY {expr};"
    stmt = Parser().parse(mock_query)[0]
    assert isinstance(stmt, SelectStatement), "Expected a select statement"
    return stmt.orderby_list


def parse_rename(old_name: str, new_name: str):
    mock_query = f"RENAME TABLE {old_name} TO {new_name};"
    stmt = Parser().parse(mock_query)[0]
    assert isinstance(stmt, RenameTableStatement), "Expected a rename statement"
    return stmt
