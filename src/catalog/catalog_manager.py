# coding=utf-8
# Copyright 2018-2020 EVA
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

from src.utils.logging_manager import LoggingManager
from src.utils.logging_manager import LoggingLevel

from src.configuration.configuration_manager import ConfigurationManager
from src.configuration.dictionary import CATALOG_DIR
from src.configuration.dictionary import DATASET_FILE

from urllib.parse import urlparse

from src.catalog.dataset_df import *


class CatalogManager(object):

    _instance = None
    _catalog = None
    _catalog_dictionary = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(CatalogManager, cls).__new__(cls)

            cls._instance.bootstrap_catalog()

        return cls._instance

    def bootstrap_catalog(self):

        eva_dir = ConfigurationManager().get_value("core", "location")
        output_url = os.path.join(eva_dir, CATALOG_DIR)
        LoggingManager().log("Bootstrapping catalog" + str(output_url),
                             LoggingLevel.INFO)

        # Construct output location
        eva_dir = ConfigurationManager().get_value("core", "location")
        catalog_dir_url = os.path.join(eva_dir, "catalog")

        # Get filesystem path
        catalog_os_path = urlparse(catalog_dir_url).path

        # Check if catalog exists
        if os.path.exists(catalog_os_path):

            dataset_file_url = os.path.join(catalog_dir_url, DATASET_FILE)
            dataset_df = load_dataset_df(dataset_file_url)
            dataset_df.show(1)

            append_row(dataset_file_url, 'foo')

        # Create catalog if it does not exist
        else:

            print("Catalog not found")

            dataset_file_url = os.path.join(catalog_dir_url, DATASET_FILE)
            create_datset_df(dataset_file_url)
