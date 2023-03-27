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
from ast import literal_eval
from dataclasses import dataclass, field
from typing import Tuple

from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from eva.catalog.models.association_models import (
    association_table_udf_column_and_udf_cache
)
from eva.catalog.models.base_model import BaseModel


class UdfCacheCatalog(BaseModel):
    """The `UdfCacheCatalog` catalog stores information about the udf cache.

    It maintains the following information for each cache entry:
    `_row_id:` An autogenerated identifier for the cache entry.
    `_name:` The name of the cache, also referred to as the unique UDF signature.
    `_udf_id:` `_row_id` of the UDF in the `UdfCatalog` for which the cache is built.
    `_args:` A serialized list of `ColumnCatalog` `_row_id`s for each argument of the
    UDF. If the argument is a function expression, it stores the string representation
    of the expression tree.
    `_udf_depends:` A list of `UdfCatalog`s of the UDFs that the cache depends on,
    including both the UDF being cached and the UDFs in the arguments.
    `_col_depends:` A list of `ColumnCatalog`s of the columns that the cache depends on.
    """

    __tablename__ = "udf_cache"

    _name = Column("name", String(128))
    _udf_id = Column("udf_id", Integer, ForeignKey("udf_catalog._row_id"))
    _cache_path = Column("cache_path", String(256))
    _args = Column("args", String(1024))

    _col_depends = relationship(
        "ColumnCatalog",
        secondary=association_table_udf_column_and_udf_cache,
        back_populates="_dep_caches",
        # cascade="all, delete-orphan",
    )

    _udf_depends = relationship(
        "UdfCatalog",
        secondary=association_table_udf_column_and_udf_cache,
        back_populates="_dep_caches",
        
        # cascade="all, delete-orphan",
    )

    def __init__(self, name: str, udf_id: int, cache_path: str, args: Tuple[str]):
        self._name = name
        self._udf_id = udf_id
        self._cache_path = cache_path
        self._args = str(args)

    def as_dataclass(self) -> "UdfCacheCatalogEntry":
        udf_depends = [obj._row_id for obj in self._udf_depends]
        col_depends = [obj._row_id for obj in self._col_depends]
        return UdfCacheCatalogEntry(
            row_id=self._row_id,
            name=self._name,
            udf_id=self._udf_id,
            cache_path=self._cache_path,
            args=literal_eval(self._args),
            udf_depends=udf_depends,
            col_depends=col_depends,
        )


@dataclass(unsafe_hash=True)
class UdfCacheCatalogEntry:
    """Dataclass representing an entry in the `UdfCatalog`.
    This is done to ensure we don't expose the sqlalchemy dependencies beyond catalog service. Further, sqlalchemy does not allow sharing of objects across threads.
    """

    name: str
    udf_id: int
    cache_path: str
    args: Tuple[str]
    # row_ids of the dependent udfs and columns
    udf_depends: Tuple[int] = field(compare=False, default_factory=tuple)
    col_depends: Tuple[int] = field(compare=False, default_factory=tuple)
    row_id: int = None
