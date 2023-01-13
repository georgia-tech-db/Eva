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
from time import sleep

import pytest
from pytest_benchmark import session


@pytest.mark.torchtest
@pytest.mark.benchmark(
    warmup=False, warmup_iterations=1, min_rounds=1, min_time=0.1, max_time=0.5
)
def test_should_run_pytorch_and_resnet50(benchmark, setup_pytorch_tests):

    try:
        benchmark(sleep, 4)
    except session.PerformanceRegression as e:
        print(e)
        exit(-1)
