#!/usr/bin/env python
# coding=utf-8

# Copyright [2017] [B2W Digital]
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import pytest

from marvin_python_toolbox.engine_base import EngineBaseTraining


@pytest.fixture
def engine_action():
    class EngineAction(EngineBaseTraining):
        def execute(self, **kwargs):
            return 1

    return EngineAction(default_root_path="/tmp/.marvin")


class TestEngineBaseTraining:
    def test_instantiation_error(self):
        try:
            EngineBaseTraining()
            assert False

        except TypeError:
            assert True

    def test_instantiation_ok(self):
        class EngineAction(EngineBaseTraining):
            def execute(self, **kwargs):
                return 1

        try:
            EngineAction()
            assert True

        except TypeError:
            assert False

        assert 1 == EngineAction().execute()

    def test_dataset(self, engine_action):
        engine_action.dataset = [1]
        assert engine_action.dataset == engine_action._dataset == [1]

    def test_model(self, engine_action):
        engine_action.model = [2]
        assert engine_action.model == engine_action._model == [2]

    def test_metrics(self, engine_action):
        engine_action.metrics = [3]
        assert engine_action.metrics == engine_action._metrics == [3]
