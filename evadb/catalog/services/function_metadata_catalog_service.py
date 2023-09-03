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
from typing import List

from sqlalchemy.orm import Session
from sqlalchemy.sql.expression import select

from evadb.catalog.models.function_metadata_catalog import (
    FunctionMetadataCatalog,
    FunctionMetadataCatalogEntry,
)
from evadb.catalog.services.base_service import BaseService
from evadb.utils.errors import CatalogError
from evadb.utils.logging_manager import logger


class FunctionMetadataCatalogService(BaseService):
    def __init__(self, db_session: Session):
        super().__init__(FunctionMetadataCatalog, db_session)

    def insert_entries(self, entries: List[FunctionMetadataCatalogEntry]):
        try:
            for entry in entries:
                metadata_obj = FunctionMetadataCatalog(
                    key=entry.key, value=entry.value, function_id=entry.function_id
                )
                metadata_obj.save(self.session)
        except Exception as e:
            logger.exception(
                f"Failed to insert entry {entry} into function metadata catalog with exception {str(e)}"
            )
            raise CatalogError(e)

    def get_entries_by_function_id(
        self, function_id: int
    ) -> List[FunctionMetadataCatalogEntry]:
        try:
            result = (
                self.session.execute(
                    select(self.model).filter(
                        self.model._function_id == function_id,
                    )
                )
                .scalars()
                .all()
            )
            return [obj.as_dataclass() for obj in result]
        except Exception as e:
            error = f"Getting metadata entries for Function id {function_id} raised {e}"
            logger.error(error)
            raise CatalogError(error)
