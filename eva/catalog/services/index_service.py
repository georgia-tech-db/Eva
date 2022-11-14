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
import os

from sqlalchemy.orm.exc import NoResultFound

from eva.catalog.models.index import IndexMetadata
from eva.catalog.services.base_service import BaseService
from eva.utils.logging_manager import logger


class IndexService(BaseService):
    def __init__(self):
        super().__init__(IndexMetadata)

    def create_index(self, name: str, save_file_path: str, type: str) -> IndexMetadata:
        metadata = self.model(name, save_file_path, type)
        metadata = metadata.save()
        return metadata

    def index_by_name(self, name: str):
        try:
            return self.model.query.filter(self.model._name == name).one()
        except NoResultFound:
            return None

    def index_by_id(self, id: int):
        try:
            return self.model.query.filter(self.model._id == id).one()
        except NoResultFound:
            return None

    def drop_index_by_name(self, name: str):
        try:
            index_record = self.index_by_name(name)
            # clean up the on disk data
            if os.path.exists(index_record.save_file_path):
                os.remove(index_record.save_file_path)
            index_record.delete()
        except Exception:
            logger.exception("Delete index failed for name {}".format(name))
            return False
        return True

    def get_all_indices(self):
        try:
            return self.model.query.all()
        except NoResultFound:
            return []
