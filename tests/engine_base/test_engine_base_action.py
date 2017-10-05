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

import cPickle as serializer
import pytest
import os
import shutil
import copy

from marvin_python_toolbox.engine_base import EngineBaseAction
from marvin_python_toolbox.engine_base.stubs.actions_pb2 import HealthCheckResponse, HealthCheckRequest


@pytest.fixture
def engine_action():
    class EngineAction(EngineBaseAction):
        def execute(self, **kwargs):
            return 1

    return EngineAction(default_root_path="/tmp/.marvin")


class TestEngineBaseAction:
    def setup(self):
        shutil.rmtree("/tmp/.marvin", ignore_errors=True)

    def test_retrieve_obj(self):
        path = '/tmp/test-obj'
        obj = [1, 2]
        serializer.dump(obj, open(path, 'wb'))
        assert obj == EngineBaseAction.retrieve_obj(path)

    def test_params(self, engine_action):
        engine_action._params = {'x': '1'}
        assert engine_action.params == {'x': '1'}

    def test_constructor(self):
        class EngineAction(EngineBaseAction):
            def execute(self, **kwargs):
                return 1

        engine = EngineAction(params={"x", 1}, persistence_mode='x')

        assert engine.params == {"x", 1}
        assert engine._persistence_mode == 'x'

    def test_get_object_file_path(self, engine_action):
        assert engine_action._get_object_file_path(object_reference="xpath") == "/tmp/.marvin/test_base_action/xpath"

    def test_save_obj_memory_persistence(self, engine_action):
        obj = [6, 5, 4]
        object_reference = '_params'
        engine_action._save_obj(object_reference, obj)

        assert obj == engine_action.params
        assert not os.path.exists("/tmp/.marvin/test_base_action/params")

    def test_save_obj_local_persistence(self, engine_action):
        obj = [6, 5, 4]
        object_reference = '_params'
        engine_action._persistence_mode = 'local'
        engine_action._save_obj(object_reference, obj)

        assert obj == engine_action.params
        assert os.path.exists("/tmp/.marvin/test_base_action/params")

    def test_save_two_times(self, engine_action):
        obj = [6, 5, 4]
        object_reference = '_params'
        engine_action._persistence_mode = 'local'

        engine_action._save_obj(object_reference, obj)
        try:
            engine_action._save_obj(object_reference, obj)
            assert False

        except Exception as e:
            assert str(e) == "('MultipleAssignException', '_params')"

    def test_load_obj_local_persistence(self, engine_action):
        engine_action2 = copy.copy(engine_action)

        obj = [6, 5, 4]
        object_reference = '_params'
        engine_action._persistence_mode = 'local'
        engine_action._save_obj(object_reference, obj)

        engine_action2._persistence_mode = 'local'
        engine_action2._load_obj(object_reference)

        assert obj == engine_action2.params

        engine_action2._persistence_mode = 'memory'
        engine_action2._params = [1]
        engine_action2._load_obj(object_reference)

        assert [1] == engine_action2.params

    def test_health_check_ok(self, engine_action):
        obj1_key = "obj1"
        engine_action._save_obj(obj1_key, "check")
        request = HealthCheckRequest(artifacts=obj1_key)
        expected_response = HealthCheckResponse(status=HealthCheckResponse.OK)
        response = engine_action._health_check(request=request, context=None)

        assert expected_response.status == response.status

    def test_health_check_ok_multiple(self, engine_action):
        obj1_key = "obj1"
        engine_action._save_obj(obj1_key, "check")
        obj2_key = "obj2"
        engine_action._save_obj(obj2_key, "check")

        request = HealthCheckRequest(artifacts=obj1_key + "," + obj2_key)
        expected_response = HealthCheckResponse(status=HealthCheckResponse.OK)
        response = engine_action._health_check(request=request, context=None)

        assert expected_response.status == response.status

    def test_health_check_nok(self, engine_action):
        obj1_key = "obj1"
        request = HealthCheckRequest(artifacts=obj1_key)
        expected_response = HealthCheckResponse(status=HealthCheckResponse.NOK)
        response = engine_action._health_check(request=request, context=None)

        assert expected_response.status == response.status

        engine_action._save_obj(obj1_key, "check")
        request = HealthCheckRequest(artifacts=obj1_key + ", obj2")
        response = engine_action._health_check(request=request, context=None)

        assert expected_response.status == response.status

    def test_health_check_exception(self):
        class BadEngineAction(EngineBaseAction):
            def execute(self, **kwargs):
                return 1

            def __getattribute__(self, name):
                if name == 'obj1':
                    raise Exception('I am Bad!')
                else:
                    return EngineBaseAction.__getattribute__(self, name)

        engine_action = BadEngineAction()

        obj1_key = "obj1"
        request = HealthCheckRequest(artifacts=obj1_key)
        expected_response = HealthCheckResponse(status=HealthCheckResponse.NOK)
        response = engine_action._health_check(request=request, context=None)

        assert expected_response.status == response.status

