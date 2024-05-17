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
import argparse
import asyncio
import unittest

from mock import patch

from evadb.evadb_cmd_client import evadb_client, main
from evadb.evadb_config import BASE_EVADB_CONFIG


# @pytest.mark.skip
class CMDClientTest(unittest.IsolatedAsyncioTestCase):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_mock_stdin_reader(self) -> asyncio.StreamReader:
        stdin_reader = asyncio.StreamReader()
        stdin_reader.feed_data(b"EXIT;\n")
        stdin_reader.feed_eof()
        return stdin_reader

    @patch("evadb.evadb_cmd_client.start_cmd_client")
    @patch("evadb.server.interpreter.create_stdin_reader")
    def test_evadb_client(self, mock_stdin_reader, mock_client):
        mock_stdin_reader.return_value = self.get_mock_stdin_reader()
        mock_client.side_effect = Exception("Test")

        async def test():
            with self.assertRaises(Exception):
                await evadb_client("0.0.0.0", 8803)

        asyncio.run(test())

        mock_client.reset_mock()
        mock_client.side_effect = KeyboardInterrupt

        async def test2():
            # Pass exception
            await evadb_client("0.0.0.0", 8803)

        asyncio.run(test2())

    @patch("argparse.ArgumentParser.parse_known_args")
    @patch("evadb.evadb_cmd_client.start_cmd_client")
    def test_evadb_client_with_cmd_arguments(
        self, mock_start_cmd_client, mock_parse_known_args
    ):
        # Set up the mock to simulate command-line arguments
        mock_parse_known_args.return_value = (
            argparse.Namespace(host="127.0.0.1", port="8800"),
            [],
        )

        # Call the function under test
        main()
        mock_start_cmd_client.assert_called_once_with("127.0.0.1", "8800")

    @patch("argparse.ArgumentParser.parse_known_args")
    @patch("evadb.evadb_cmd_client.start_cmd_client")
    def test_main_without_cmd_arguments(
        self, mock_start_cmd_client, mock_parse_known_args
    ):
        # Set up the mock to simulate missing command-line arguments
        mock_parse_known_args.return_value = (
            argparse.Namespace(host=None, port=None),
            [],
        )

        # Call the function under test
        main()

        # Assert that the mocked functions were called correctly
        mock_start_cmd_client.assert_called_once_with(
            BASE_EVADB_CONFIG["host"], BASE_EVADB_CONFIG["port"]
        )
