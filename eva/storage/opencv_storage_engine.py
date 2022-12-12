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
import shutil
import zlib
from pathlib import Path
from typing import Iterator

import pandas as pd

from eva.catalog.catalog_manager import CatalogManager
from eva.catalog.models.df_metadata import DataFrameMetadata
from eva.expression.abstract_expression import AbstractExpression
from eva.models.storage.batch import Batch
from eva.parser.table_ref import TableInfo
from eva.readers.opencv_reader import OpenCVReader
from eva.storage.abstract_storage_engine import AbstractStorageEngine
from eva.storage.sqlite_storage_engine import SQLStorageEngine
from eva.utils.errors import CatalogError
from eva.utils.logging_manager import logger


class OpenCVStorageEngine(AbstractStorageEngine):
    def __init__(self):
        self._rdb_handler: SQLStorageEngine = SQLStorageEngine()

    def _get_metadata_table(self, table: DataFrameMetadata):
        return CatalogManager().get_video_metadata_table(table)

    def _create_metadata_table(self, table: DataFrameMetadata):
        return CatalogManager().create_video_metadata_table(table)

    def _xform_file_url_to_file_name(self, file_url: Path) -> str:
        # convert video_path to file name
        # This is done to support duplicate video_names with different complete paths. Without conversion, we cannot copy files with same name but different paths. Eg., a/b/my.mp4 and a/b/c/my.mp4
        # deterministic hashing
        xfromed_file_name = zlib.adler32(str(file_url).encode("utf-8")) & 0xFFFFFFFF
        return str(xfromed_file_name)

    def create(self, table: DataFrameMetadata, if_not_exists=True):
        """
        Create the directory to store the video.
        Create a sqlite table to persist the file urls
        """
        dir_path = Path(table.file_url)
        try:
            dir_path.mkdir(parents=True)
        except FileExistsError:
            if if_not_exists:
                return True
            error = "Failed to load the video as directory \
                        already exists: {}".format(
                dir_path
            )
            logger.error(error)
            raise FileExistsError(error)

        self._rdb_handler.create(self._create_metadata_table(table))
        return True

    def drop(self, table: DataFrameMetadata):
        dir_path = Path(table.file_url)
        try:
            shutil.rmtree(str(dir_path))
            metadata_table = self._get_metadata_table(table)
            self._rdb_handler.drop(metadata_table)
            # remove the metadata table from the catalog
            CatalogManager().drop_dataset_metadata(metadata_table)
        except Exception as e:
            logger.exception(f"Failed to drop the video table {e}")

    def delete(self, table: DataFrameMetadata, rows: Batch):
        try:
            video_metadata_table = self._get_metadata_table(table)
            for video_file_path in rows.file_paths():
                dst_file_name = self._xform_file_url_to_file_name(Path(video_file_path))
                video_file = Path(table.file_url) / dst_file_name
                self._rdb_handler.delete(
                    video_metadata_table,
                    where_clause={
                        video_metadata_table.identifier_column: str(video_file_path)
                    },
                )
                video_file.unlink()
        except Exception as e:
            error = f"Deleting file path {video_file_path} failed with exception {e}"
            logger.exception(error)
            raise RuntimeError(error)
        return True

    def write(self, table: DataFrameMetadata, rows: Batch):
        try:
            dir_path = Path(table.file_url)
            for video_file_path in rows.file_paths():
                video_file = Path(video_file_path)
                dst_file_name = self._xform_file_url_to_file_name(video_file)
                dst_path = dir_path / dst_file_name
                if dst_path.exists():
                    raise FileExistsError(
                        f"Duplicate File: {video_file} already exists in the table {table.name}"
                    )
                shutil.copy2(str(video_file), str(dst_path))
            self._rdb_handler.write(
                self._get_metadata_table(table),
                Batch(pd.DataFrame({"file_url": list(rows.file_paths())})),
            )

        except Exception as e:
            logger.exception(str(e))
            raise RuntimeError(str(e))
        else:
            return True

    def read(
        self,
        table: DataFrameMetadata,
        batch_mem_size: int,
        predicate: AbstractExpression = None,
        sampling_rate: int = None,
    ) -> Iterator[Batch]:

        for video_files in self._rdb_handler.read(self._get_metadata_table(table), 12):
            for video_file_name in video_files.frames["file_url"]:
                system_file_name = self._xform_file_url_to_file_name(video_file_name)
                video_file = Path(table.file_url) / system_file_name
                reader = OpenCVReader(
                    str(video_file),
                    batch_mem_size=batch_mem_size,
                    predicate=predicate,
                    sampling_rate=sampling_rate,
                )
                for batch in reader.read():
                    column_name = table.columns[1].name
                    batch.frames[column_name] = str(video_file_name)
                    yield batch

    def rename(self, old_table: DataFrameMetadata, new_name: TableInfo):
        try:
            CatalogManager().rename_table(old_table, new_name)
        except CatalogError as err:
            raise Exception(f"Failed to rename table {new_name} with exception {err}")
        except Exception as e:
            raise Exception(
                f"Unexpected exception {str(e)} occured during rename operation"
            )

    def _close(self, table):
        pass

    def _read_init(self, table):
        pass
