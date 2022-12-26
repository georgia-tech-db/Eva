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
import unittest

import mock
from mock import ANY, MagicMock

from eva.catalog.catalog_manager import CatalogManager
from eva.catalog.catalog_type import ColumnType, NdArrayType, TableType
from eva.catalog.models.column_catalog import ColumnCatalog
from eva.catalog.models.udf_catalog import UdfCatalog


class CatalogManagerTests(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def test_catalog_manager_singleton_pattern(self):
        x = CatalogManager()
        y = CatalogManager()
        self.assertEqual(x, y)

    @mock.patch("eva.catalog.catalog_manager.init_db")
    def test_catalog_bootstrap(self, mocked_db):
        x = CatalogManager()
        x._bootstrap_catalog()
        mocked_db.assert_called()

    @mock.patch("eva.catalog.catalog_manager.drop_db")
    def test_catalog_shutdown(self, mocked_db):
        x = CatalogManager()
        x._shutdown_catalog()
        mocked_db.assert_called_once()

    @mock.patch("eva.catalog.catalog_manager.CatalogManager._shutdown_catalog")
    @mock.patch("eva.catalog.catalog_manager.CatalogManager._bootstrap_catalog")  # noqa
    def test_catalog_manager_reset(self, mock_bootstrap, mock_shutdown):
        x = CatalogManager()
        mock_init = MagicMock()
        with mock.patch.object(CatalogManager, "__init__", mock_init):
            x.reset()
            mock_init.assert_called_once_with()
            mock_bootstrap.assert_called_once_with()
            mock_shutdown.assert_called_once_with()

    @mock.patch("eva.catalog.catalog_manager.CatalogManager.insert_table_catalog_entry")
    @mock.patch("eva.catalog.catalog_manager.generate_file_path")
    def test_create_video_table(self, m_gfp, m_cm):
        x = CatalogManager()
        name = "eva"
        uri = "tmp"
        m_gfp.return_value = uri

        x._create_video_table(name)

        col_metadata_list = [
            ColumnCatalog("name", ColumnType.TEXT, False, None, []),
            ColumnCatalog("id", ColumnType.INTEGER, False, None, []),
            ColumnCatalog(
                "data", ColumnType.NDARRAY, False, NdArrayType.UINT8, [None, None, None]
            ),
        ]

        m_cm.assert_called_once_with(
            name,
            uri,
            col_metadata_list,
            identifier_column="id",
            table_type=TableType.VIDEO_DATA,
        )

    @mock.patch("eva.catalog.catalog_manager.init_db")
    @mock.patch("eva.catalog.catalog_manager.TableCatalogService")
    @mock.patch("eva.catalog.catalog_manager.ColumnCatalogService")
    def test_create_metadata_should_create_dataset_and_columns(
        self, dcs_mock, ds_mock, initdb_mock
    ):
        catalog = CatalogManager()
        file_url = "file1"
        dataset_name = "name"

        columns = [(ColumnCatalog("c1", ColumnType.INTEGER))]
        actual = catalog.insert_table_catalog_entry(dataset_name, file_url, columns)
        ds_mock.return_value.insert_entry.assert_called_with(
            dataset_name, file_url, identifier_id="id", table_type=TableType.VIDEO_DATA
        )
        for column in columns:
            column.table_id = ds_mock.return_value.insert_entry.return_value.id

        dcs_mock.return_value.insert_entries.assert_called_with([ANY] + columns)

        expected = ds_mock.return_value.insert_entry.return_value
        expected.schema = dcs_mock.return_value.insert_entries.return_value

        self.assertEqual(actual, expected)

    @mock.patch("eva.catalog.catalog_manager.init_db")
    @mock.patch("eva.catalog.catalog_manager.TableCatalogService")
    @mock.patch("eva.catalog.catalog_manager.ColumnCatalogService")
    def test_get_table_catalog_entry_when_table_exists(
        self, dcs_mock, ds_mock, initdb_mock
    ):
        catalog = CatalogManager()
        dataset_name = "name"

        database_name = "database"
        schema = [1, 2, 3]
        id = 1
        metadata_obj = MagicMock(id=id, schema=None)
        ds_mock.return_value.get_entry_by_name.return_value = metadata_obj
        dcs_mock.return_value.filter_entries_by_table_id.return_value = schema

        actual = catalog.get_table_catalog_entry(database_name, dataset_name)
        ds_mock.return_value.get_entry_by_name.assert_called_with(
            database_name, dataset_name
        )
        dcs_mock.return_value.filter_entries_by_table_id.assert_called_with(id)
        self.assertEqual(actual.id, id)
        self.assertEqual(actual.schema, schema)

    @mock.patch("eva.catalog.catalog_manager.init_db")
    @mock.patch("eva.catalog.catalog_manager.TableCatalogService")
    @mock.patch("eva.catalog.catalog_manager.ColumnCatalogService")
    def test_get_table_catalog_entry_when_table_doesnot_exists(
        self, dcs_mock, ds_mock, initdb_mock
    ):
        catalog = CatalogManager()
        dataset_name = "name"

        database_name = "database"
        metadata_obj = None

        ds_mock.return_value.get_entry_by_name.return_value = metadata_obj

        actual = catalog.get_table_catalog_entry(database_name, dataset_name)
        ds_mock.return_value.get_entry_by_name.assert_called_with(
            database_name, dataset_name
        )
        dcs_mock.return_value.filter_entries_by_table_id.assert_not_called()
        self.assertEqual(actual, metadata_obj)

    @mock.patch("eva.catalog.catalog_manager.UdfIOCatalog")
    def test_create_udf_io_object(self, udfio_mock):
        catalog = CatalogManager()
        actual = catalog.udf_io(
            "name", ColumnType.NDARRAY, NdArrayType.UINT8, [2, 3, 4], True
        )
        udfio_mock.assert_called_with(
            "name",
            ColumnType.NDARRAY,
            array_type=NdArrayType.UINT8,
            array_dimensions=[2, 3, 4],
            is_input=True,
        )
        self.assertEqual(actual, udfio_mock.return_value)

    @mock.patch("eva.catalog.catalog_manager.UdfCatalogService")
    @mock.patch("eva.catalog.catalog_manager.UdfIOCatalogService")
    def test_insert_udf(self, udfio_mock, udf_mock):
        catalog = CatalogManager()
        udf_io_list = [MagicMock()]
        actual = catalog.insert_udf_catalog_entry(
            "udf", "sample.py", "classification", udf_io_list
        )
        udfio_mock.return_value.insert_entries.assert_called_with(udf_io_list)
        udf_mock.return_value.insert_entry.assert_called_with(
            "udf", "sample.py", "classification"
        )
        self.assertEqual(actual, udf_mock.return_value.insert_entry.return_value)

    @mock.patch("eva.catalog.catalog_manager.UdfCatalogService")
    def test_get_udf_catalog_entry_by_name(self, udf_mock):
        catalog = CatalogManager()
        actual = catalog.get_udf_catalog_entry_by_name("name")
        udf_mock.return_value.get_entry_by_name.assert_called_with("name")
        self.assertEqual(actual, udf_mock.return_value.get_entry_by_name.return_value)

    @mock.patch("eva.catalog.catalog_manager.UdfCatalogService")
    def test_delete_udf(self, udf_mock):
        CatalogManager().delete_udf_catalog_entry_by_name("name")
        udf_mock.return_value.delete_entry_by_name.assert_called_with("name")

    @mock.patch("eva.catalog.catalog_manager.UdfIOCatalogService")
    def test_get_udf_outputs(self, udf_mock):
        mock_func = udf_mock.return_value.get_output_entries_by_udf_id
        udf_obj = MagicMock(spec=UdfCatalog)
        CatalogManager().get_udf_io_catalog_output_entries(udf_obj)
        mock_func.assert_called_once_with(udf_obj.id)

        # should raise error
        with self.assertRaises(ValueError):
            CatalogManager().get_udf_io_catalog_output_entries(MagicMock())

    @mock.patch("eva.catalog.catalog_manager.UdfIOCatalogService")
    def test_get_udf_inputs(self, udf_mock):
        mock_func = udf_mock.return_value.get_input_entries_by_udf_id
        udf_obj = MagicMock(spec=UdfCatalog)
        CatalogManager().get_udf_io_catalog_input_entries(udf_obj)
        mock_func.assert_called_once_with(udf_obj.id)

        # should raise error
        with self.assertRaises(ValueError):
            CatalogManager().get_udf_io_catalog_input_entries(MagicMock())
