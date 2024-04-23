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
from typing import Union

SUBMISSION_COLUMNS = [
    ["author", str],
    ["author_flair_text", Union[str, None]],
    ["clicked", bool],
    ["created_utc", str],
    ["distinguished", bool],
    ["edited", bool],
    ["id", str],
    ["is_original_content", bool],
    ["is_self", bool],
    ["link_flair_text", Union[str, None]],
    ["locked", bool],
    ["name", str],
    ["num_comments", int],
    ["over_18", bool],
    ["permalink", str],
    ["saved", bool],
    ["score", float],
    ["selftext", str],
    ["spoiler", bool],
    ["stickied", bool],
    ["title", str],
    ["upvote_ratio", float],
    ["url", str],
]
