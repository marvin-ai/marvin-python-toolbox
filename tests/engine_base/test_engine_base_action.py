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

import joblib as serializer
import pytest
import os
import shutil
import copy
try:
    import mock
except ImportError:
    import unittest.mock as mock

from marvin_python_toolbox.engine_base import EngineBaseBatchAction
from marvin_python_toolbox.engine_base import EngineBaseAction, EngineBaseOnlineAction
from marvin_python_toolbox.engine_base.stubs.actions_pb2 import HealthCheckResponse, HealthCheckRequest
from marvin_python_toolbox.engine_base.stubs.actions_pb2 import OnlineActionRequest, ReloadRequest, BatchActionRequest


@pytest.fixture
def engine_action():
    class EngineAction(EngineBaseAction):
        def execute(self, params, **kwargs):
            return 1

    return EngineAction(default_root_path="/tmp/.marvin")


@pytest.fixture
def batch_engine_action():
    class BatchEngineAction(EngineBaseBatchAction):
        def execute(self, params, **kwargs):
            return 1

    return BatchEngineAction(default_root_path="/tmp/.marvin")


class TestEngineBaseAction:
    def setup(self):
        shutil.rmtree("/tmp/.marvin", ignore_errors=True)

    def test_retrieve_obj(self):
        path = '/tmp/test-obj'
        obj = [1, 2]
        serializer.dump(obj, open(path, 'wb'))
        assert obj == EngineBaseAction.retrieve_obj(path)

    def test_constructor(self):
        class EngineAction(EngineBaseAction):
            def execute(self, params, **kwargs):
                return 1

        engine = EngineAction(params={"x", 1}, persistence_mode='x')

        assert engine._params == {"x", 1}
        assert engine._persistence_mode == 'x'

    def test_get_object_file_path(self, engine_action):
        assert engine_action._get_object_file_path(object_reference="xpath") == "/tmp/.marvin/test_base_action/xpath"

    def test_save_obj_memory_persistence(self, engine_action):
        obj = [6, 5, 4]
        object_reference = '_params'
        engine_action._save_obj(object_reference, obj)

        assert obj == engine_action._params
        assert not os.path.exists("/tmp/.marvin/test_base_action/params")

    def test_save_obj_local_persistence(self, engine_action):
        obj = [6, 5, 4]
        object_reference = '_params'
        engine_action._persistence_mode = 'local'
        engine_action._save_obj(object_reference, obj)

        assert obj == engine_action._params
        assert os.path.exists("/tmp/.marvin/test_base_action/params")
        assert list(engine_action._local_saved_objects.keys()) == [object_reference]

    def test_release_saved_objects(self, engine_action):
        obj = [6, 5, 4]
        object_reference = '_params'
        engine_action._persistence_mode = 'local'
        engine_action._save_obj(object_reference, obj)

        assert list(engine_action._local_saved_objects.keys()) == [object_reference]
        engine_action._release_local_saved_objects()
        assert engine_action._params is None

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

        assert obj == engine_action2._params

        engine_action2._persistence_mode = 'memory'
        engine_action2._params = [1]
        engine_action2._load_obj(object_reference)

        assert [1] == engine_action2._params

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
            def execute(self, params, **kwargs):
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

    def test_remote_execute_with_string_response(self):
        class StringReturnedAction(EngineBaseOnlineAction):
            def execute(self, input_message, params, **kwargs):
                return "message 1"

        request = OnlineActionRequest(message="{\"k\": 1}", params="{\"k\": 1}")
        engine_action = StringReturnedAction()
        response = engine_action._remote_execute(request=request, context=None)

        assert response.message == "message 1"

    def test_remote_execute_with_int_response(self):
        class StringReturnedAction(EngineBaseOnlineAction):
            def execute(self, input_message, params, **kwargs):
                return 1

        request = OnlineActionRequest(message="{\"k\": 1}", params="{\"k\": 1}")
        engine_action = StringReturnedAction()
        response = engine_action._remote_execute(request=request, context=None)

        assert response.message == "1"

    def test_remote_execute_with_object_response(self):
        class StringReturnedAction(EngineBaseOnlineAction):
            def execute(self, input_message, params, **kwargs):
                return {"r": 1}

        request = OnlineActionRequest(message="{\"k\": 1}", params="{\"k\": 1}")
        engine_action = StringReturnedAction()
        response = engine_action._remote_execute(request=request, context=None)

        assert response.message == "{\"r\": 1}"

    def test_remote_execute_with_list_response(self):
        class StringReturnedAction(EngineBaseOnlineAction):
            def execute(self, input_message, params, **kwargs):
                return [1, 2]

        request = OnlineActionRequest(message="{\"k\": 1}", params="{\"k\": 1}")
        engine_action = StringReturnedAction()
        response = engine_action._remote_execute(request=request, context=None)

        assert response.message == "[1, 2]"

    @mock.patch('marvin_python_toolbox.engine_base.engine_base_action.EngineBaseAction._load_obj')
    def test_remote_reload_with_artifacts(self, load_obj_mocked, engine_action):
        objs_key = "obj1"
        engine_action._save_obj(objs_key, "check")
        request = ReloadRequest(artifacts=objs_key, protocol='xyz')

        response = engine_action._remote_reload(request, None)
        load_obj_mocked.assert_called_once_with(object_reference=u'obj1')
        assert response.message == "Reloaded"

    @mock.patch('marvin_python_toolbox.engine_base.engine_base_action.EngineBaseAction._load_obj')
    def test_remote_reload_without_artifacts(self, load_obj_mocked, engine_action):
        request = ReloadRequest(artifacts=None, protocol='xyz')

        response = engine_action._remote_reload(request, None)
        load_obj_mocked.assert_not_called()
        assert response.message == "Nothing to reload"


class TestEngineBaseBatchAction:
    def setup(self):
        shutil.rmtree("/tmp/.marvin", ignore_errors=True)

    def test_pipeline_execute_without_previous_steps(self, batch_engine_action):
        batch_engine_action.execute = mock.MagicMock()
        batch_engine_action._pipeline_execute(params=123)
        
        batch_engine_action.execute.assert_called_once_with(123)

    def test_pipeline_execute_with_previous_steps(self, batch_engine_action):
        previous = copy.copy(batch_engine_action)
        previous._pipeline_execute = mock.MagicMock()
        batch_engine_action._previous_step = previous
        batch_engine_action.execute = mock.MagicMock()

        batch_engine_action._pipeline_execute(params=123)
        
        previous._pipeline_execute.assert_called_once_with(123)
        batch_engine_action.execute.assert_called_once_with(123)

    def test_remote_execute_without_request_params(self, batch_engine_action):
        batch_engine_action._params = 123
        batch_engine_action._pipeline_execute = mock.MagicMock()

        request = BatchActionRequest()
        batch_engine_action._remote_execute(request, None)

        batch_engine_action._pipeline_execute.assert_called_once_with(params=123)

    def test_remote_execute_with_request_params(self, batch_engine_action):
        batch_engine_action._params = 123
        batch_engine_action._pipeline_execute = mock.MagicMock()

        request = BatchActionRequest(params='{"test": 123}')
        batch_engine_action._remote_execute(request, None)

        batch_engine_action._pipeline_execute.assert_called_once_with(params={u"test": 123})


