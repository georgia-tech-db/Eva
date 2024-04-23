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

import pandas as pd
from praw import Reddit
from prawcore import ResponseException

from ..types import DBHandler, DBHandlerResponse, DBHandlerStatus
from .table_column_info import SUBMISSION_COLUMNS


class RedditHandler(DBHandler):
    def __init__(self, name: str, **kwargs):
        super().__init__(name)
        self.clientId = kwargs.get("client_id")
        self.clientSecret = kwargs.get("clientSecret")
        self.userAgent = kwargs.get("userAgent")
        self.subreddit = kwargs.get("subreddit")

    def connect(self):
        try:
            self.client = Reddit(
                client_id=self.clientId,
                client_secret=self.clientSecret,
                user_agent=self.userAgent,
            )
            return DBHandlerStatus(status=True)
        except Exception as e:
            return DBHandlerStatus(status=False, error=str(e))

    @property
    def supported_table(self):
        def _submission_generator():
            for submission in self.client.subreddit(self.subreddit).hot():
                yield {
                    property_name: getattr(submission, property_name)
                    for property_name, _ in SUBMISSION_COLUMNS
                }

        mapping = {
            "submissions": {
                "columns": SUBMISSION_COLUMNS,
                "generator": _submission_generator(),
            },
        }
        return mapping

    def disconnect(self):
        """
        No action required to disconnect from Reddit datasource
        TODO: Add support for destroying session token if used in other flows
        """
        return
        # raise NotImplementedError()

    def check_connection(self) -> DBHandlerStatus:
        try:
            self.client.user.me()
        except ResponseException as e:
            return DBHandlerStatus(
                status=False, error=f"Received ResponseException: {e.response}"
            )
        return DBHandlerStatus(status=True)

    def get_tables(self) -> DBHandlerResponse:
        connection_status = self.check_connection()
        if not connection_status.status:
            return DBHandlerResponse(data=None, error=str(connection_status))

        try:
            tables_df = pd.DataFrame(
                list(self.supported_table.keys()), columns=["table_name"]
            )
            return DBHandlerResponse(data=tables_df)
        except Exception as e:
            return DBHandlerResponse(data=None, error=str(e))

    def get_columns(self, table_name: str) -> DBHandlerResponse:
        columns = self.supported_table[table_name]["columns"]
        columns_df = pd.DataFrame(columns, columns=["name", "dtype"])
        return DBHandlerResponse(data=columns_df)

    def select(self, table_name: str) -> DBHandlerResponse:
        """
        Returns a generator that yields the data from the given table.
        Args:
            table_name (str): name of the table whose data is to be retrieved.
        Returns:
            DBHandlerResponse
        """
        if not self.client:
            return DBHandlerResponse(data=None, error="Not connected to the database.")
        try:
            if table_name not in self.supported_table:
                return DBHandlerResponse(
                    data=None,
                    error="{} is not supported or does not exist.".format(table_name),
                )
            # TODO: Projection column trimming optimization opportunity
            return DBHandlerResponse(
                data=None,
                data_generator=self.supported_table[table_name]["generator"],
            )
        except Exception as e:
            return DBHandlerResponse(data=None, error=str(e))

    # def post_message(self, message) -> DBHandlerResponse:
    #     try:
    #         response = self.client.chat_postMessage(channel=self.channel, text=message)
    #         return DBHandlerResponse(data=response["message"]["text"])
    #     except SlackApiError as e:
    #         assert e.response["ok"] is False
    #         assert e.response["error"]
    #         return DBHandlerResponse(data=None, error=e.response["error"])
    #
    # def _convert_json_response_to_DataFrame(self, json_response):
    #     messages = json_response["messages"]
    #     columns = ["text", "ts", "user"]
    #     data_df = pd.DataFrame(columns=columns)
    #     for message in messages:
    #         if message["text"] and message["ts"] and message["user"]:
    #             data_df.loc[len(data_df.index)] = [
    #                 message["text"],
    #                 message["ts"],
    #                 message["user"],
    #             ]
    #     return data_df
    #
    # def get_messages(self) -> DBHandlerResponse:
    #     try:
    #         channels = self.client.conversations_list(
    #             types="public_channel,private_channel"
    #         )["channels"]
    #         channel_ids = {c["name"]: c["id"] for c in channels}
    #         response = self.client.conversations_history(
    #             channel=channel_ids[self.channel_name]
    #         )
    #         data_df = self._convert_json_response_to_DataFrame(response)
    #         return data_df
    #
    #     except SlackApiError as e:
    #         assert e.response["ok"] is False
    #         assert e.response["error"]
    #         return DBHandlerResponse(data=None, error=e.response["error"])
    #
    # def del_message(self, timestamp) -> DBHandlerResponse:
    #     try:
    #         self.client.chat_delete(channel=self.channel, ts=timestamp)
    #     except SlackApiError as e:
    #         assert e.response["ok"] is False
    #         assert e.response["error"]
    #         return DBHandlerResponse(data=None, error=e.response["error"])

    # def execute_native_query(self, query_string: str) -> DBHandlerResponse:
    #     """
    #     TODO: integrate code for executing query on Reddit
    #     """
    #     raise NotImplementedError()
