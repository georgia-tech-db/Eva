# coding=utf-8
# Copyright 2018-2023 EVA
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
from abc import ABC, abstractmethod
from collections import deque
from typing import Any, Generator, Iterable, List, TypeVar

from eva.catalog.catalog_manager import CatalogManager
from eva.configuration.configuration_manager import ConfigurationManager
from eva.database import EVADB
from eva.models.storage.batch import Batch
from eva.plan_nodes.abstract_plan import AbstractPlan

AbstractExecutor = TypeVar("AbstractExecutor")


class AbstractExecutor(ABC):
    """
    An abstract class for the executor engine
    Arguments:
        node (AbstractPlan): Plan node corresponding to this executor
    """

    def __init__(self, db: EVADB, node: AbstractPlan):
        self._db = db
        self._node = node
        self._catalog: CatalogManager = db.catalog if db else None
        self._config: ConfigurationManager = db.config if db else None
        self._children = []

    def append_child(self, child: AbstractExecutor):
        """
        appends a child executor node

        Arguments:
            child {AbstractExecutor} -- child node
        """
        self._children.append(child)

    @property
    def children(self) -> List[AbstractExecutor]:
        """
        Returns the list of child executor
        Returns:
            [] -- list of children
        """
        return self._children

    @children.setter
    def children(self, children):
        self._children = children

    @property
    def node(self) -> AbstractPlan:
        return self._node

    @property
    def db(self) -> EVADB:
        return self._db

    @property
    def config(self) -> ConfigurationManager:
        return self._config

    @property
    def catalog(self) -> CatalogManager:
        return self._catalog

    @abstractmethod
    def exec(self, *args, **kwargs) -> Iterable[Batch]:
        """
        This method is implemented by every executor.
        Contains logic for that executor;
        For retrieval based executor : It fetches frame batches from
        child nodes and emits it to parent node.
        """

    def __call__(self, *args, **kwargs) -> Generator[Batch, None, None]:
        yield from self.exec(*args, **kwargs)

    def bfs(self):
        """Returns a generator which visits all nodes in execution tree in
        breadth-first search (BFS) traversal order.

        Returns:
            the generator object.
        """
        queue = deque([self])
        while queue:
            node = queue.popleft()
            yield node
            for child in node.children:
                queue.append(child)

    def find_all(self, exceution_type: Any):
        """Returns a generator which visits all the nodes in execution tree and yields one that matches the passed `exceution_type`.

        Args:
            exceution_type (Any): execution type to match with

        Returns:
            the generator object.
        """

        for node in self.bfs():
            if isinstance(node, exceution_type):
                yield node
