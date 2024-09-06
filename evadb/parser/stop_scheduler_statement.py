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
from __future__ import annotations

from typing import Any

from evadb.parser.statement import AbstractStatement
from evadb.parser.types import StatementType


class StopSchedulerStatement(AbstractStatement):
    def __init__(self):
        super().__init__(StatementType.STOP)

    def __str__(self):
        return "STOP JOB_SCHEDULER"

    def __eq__(self, other):
        if not isinstance(other, StopSchedulerStatement):
            return False
        return True
    
    def __hash__(self) -> int:
        return super().__hash__()
