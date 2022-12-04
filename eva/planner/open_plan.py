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
from pathlib import Path

from eva.planner.abstract_plan import AbstractPlan
from eva.planner.types import PlanOprType


class OpenPlan(AbstractPlan):
    def __init__(self, path: Path):
        super().__init__(PlanOprType.OPEN)
        self._path = path

    @property
    def path(self):
        return self._path

    def __str__(self):
        return "OpenPlan(path={})".format(
            self._path
        )

    def __hash__(self) -> int:
        return hash((super().__hash__(), self._path))
