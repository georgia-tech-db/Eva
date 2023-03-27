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
from __future__ import annotations

import typing
from ast import literal_eval
from dataclasses import dataclass, field
from typing import List, Tuple

if typing.TYPE_CHECKING:
    from eva.catalog.models.udf_cache_catalog import UdfCacheCatalogEntry

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from sqlalchemy.types import Enum

from eva.catalog.catalog_type import ColumnType, Dimension, NdArrayType
from eva.catalog.models.association_models import association_table_udf_column_and_udf_cache
from eva.catalog.models.base_model import BaseModel


class ColumnCatalog(BaseModel):
    """The `ColumnCatalog` catalog stores information about the columns of the table.
    It maintinas the following information for each column
    `_row_id:` an autogenerated identifier
    `_name: ` name of the column
    `_type:` the type of the column, refer `ColumnType`
    `_is_nullable:` which indicates whether the column is nullable
    `_array_type:` the type of array, as specified in `NdArrayType` (or `None` if the column is a primitive type)
    `_array_dimensions:` the dimensions of the array (if `_array_type` is not `None`)
    `_table_id:` the `_row_id` of the `TableCatalog` entry to which the column belongs
    `_dep_caches`: list of udf caches associated with the column
    """

    __tablename__ = "column_catalog"

    _name = Column("name", String(100))
    _type = Column("type", Enum(ColumnType), default=Enum)
    _is_nullable = Column("is_nullable", Boolean, default=False)
    _array_type = Column("array_type", Enum(NdArrayType), nullable=True)
    _array_dimensions = Column("array_dimensions", String(100))
    _table_id = Column("table_id", Integer, ForeignKey("table_catalog._row_id"))

    __table_args__ = (UniqueConstraint("name", "table_id"), {})

    # Foreign key dependency with the table catalog
    _table_catalog = relationship("TableCatalog", back_populates="_columns")

    # list of associated UdfCacheCatalog entries
    _dep_caches = relationship(
        "UdfCacheCatalog",
        secondary=association_table_udf_column_and_udf_cache,
        back_populates="_col_depends",
        cascade="all, delete",
    )

    def __init__(
        self,
        name: str,
        type: ColumnType,
        is_nullable: bool = False,
        array_type: NdArrayType = None,
        array_dimensions: Tuple[int] = (),
        table_id: int = None,
    ):
        self._name = name
        self._type = type
        self._is_nullable = is_nullable
        self._array_type = array_type
        self.array_dimensions = array_dimensions
        self._table_id = table_id

    @property
    def array_dimensions(self):
        return literal_eval(self._array_dimensions)

    @array_dimensions.setter
    def array_dimensions(self, value: Tuple[int]):
        # This tranformation converts the ANYDIM enum to
        # None which is expected by petastorm.
        # Before adding data, petastorm verifies _is_compliant_shape
        # and any unknown dimension is expected to be None
        # https://petastorm.readthedocs.io/en/latest/_modules/petastorm/codecs.html#DataframeColumnCodec.encode
        dimensions = []
        for dim in value:
            if dim == Dimension.ANYDIM:
                dimensions.append(None)
            else:
                dimensions.append(dim)
        self._array_dimensions = str(tuple(dimensions))

    def as_dataclass(self) -> "ColumnCatalogEntry":
        return ColumnCatalogEntry(
            row_id=self._row_id,
            name=self._name,
            type=self._type,
            is_nullable=self._is_nullable,
            array_type=self._array_type,
            array_dimensions=self.array_dimensions,
            table_id=self._table_id,
            table_name=self._table_catalog._name,
            dep_caches=[cache.as_dataclass() for cache in self._dep_caches],
        )


@dataclass(unsafe_hash=True)
class ColumnCatalogEntry:
    """Class decouples the ColumnCatalog from the sqlalchemy.
    This is done to ensure we don't expose the sqlalchemy dependencies beyond catalog service. Further, sqlalchemy does not allow sharing of objects across threads.
    """

    name: str
    type: ColumnType
    is_nullable: bool = False
    array_type: NdArrayType = None
    array_dimensions: Tuple[int] = field(default_factory=tuple)
    table_id: int = None
    table_name: str = None
    row_id: int = None
    dep_caches: List[UdfCacheCatalogEntry] = field(compare=False, default_factory=list)
