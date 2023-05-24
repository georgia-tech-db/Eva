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
from test.util import (
    shutdown_ray,
)

import pytest

from eva.catalog.catalog_manager import CatalogManager
from eva.configuration.constants import EVA_ROOT_DIR
from eva.server.command_handler import execute_query_fetch_all
import fitz

@pytest.mark.notparallel
class LoadExecutorTest(unittest.TestCase):
    def setUp(self):
        # reset the catalog manager before running each test
        CatalogManager().reset()

    def tearDown(self):
        shutdown_ray()

        execute_query_fetch_all("DROP TABLE IF EXISTS pdfs;")

    def test_load_pdfs(self):
        pdf_path = f"{EVA_ROOT_DIR}/data/documents/pdf_sample1.pdf"
        
        doc = fitz.open(pdf_path)
        number_of_paragraphs=0
        for page in doc:
            blocks = page.get_text("dict")["blocks"]
            for b in blocks:  # iterate through the text blocks
                if b['type'] == 0:  # this block contains text
                    block_string = ""  # text found in block
                    for l in b["lines"]:  # iterate through the text lines
                        for s in l["spans"]:  # iterate through the text spans
                            if s['text'].strip():  # removing whitespaces:
                                    block_string += s['text']
                    number_of_paragraphs += 1

        execute_query_fetch_all(
            f"""LOAD PDF '{pdf_path}' INTO pdfs;"""
        )
        result = execute_query_fetch_all("SELECT * from pdfs;")
        self.assertEqual(len(result.columns), 5)
        self.assertEqual(len(result), number_of_paragraphs)


if __name__ == "__main__":
    unittest.main()
