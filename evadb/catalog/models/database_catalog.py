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

from sqlalchemy import Column, String

from evadb.catalog.models.base_model import BaseModel
from evadb.catalog.models.utils import DatabaseCatalogEntry, TextPickleType


class DatabaseCatalog(BaseModel):
    """The `DatabaseCatalog` catalog stores information about all databases.
    `_row_id:` an autogenerated unique identifier.
    `_name:` the database name.
    `_app_type`: type of database being integrated
    `_engine:` database engine
    `_param:` parameters specific to the database engine
    """

    __tablename__ = "database_catalog"

    _name = Column("name", String(100), unique=True)
    _engine = Column("engine", String(100))
    _app_type = Column("app_type", String(100))
    _params = Column("params", TextPickleType())

    def __init__(self, name: str, engine: str, params: dict, app_type: str):
        self._name = name
        self._engine = engine
        self._app_type = app_type
        self._params = params

    def as_dataclass(self) -> "DatabaseCatalogEntry":
        return DatabaseCatalogEntry(
            row_id=self._row_id,
            name=self._name,
            engine=self._engine,
            app_type=self._app_type,
            params=self._params,
        )
