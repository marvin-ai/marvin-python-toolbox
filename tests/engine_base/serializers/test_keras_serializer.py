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

import mock
import pytest

from marvin_python_toolbox.engine_base import EngineBaseTraining
from marvin_python_toolbox.engine_base import KerasSerializer


@pytest.fixture
def engine():
    class MyEngineAction(KerasSerializer, EngineBaseTraining):
        def execute(self, **kwargs):
            pass
    return MyEngineAction(default_root_path="/tmp/.marvin")


class TestKerasSerializer(object):
    @mock.patch('keras.models.load_model')
    def test__serializer_load_keras(self, mocked_load, engine):
        mocked_load.return_value = {"me": "here"}
        mocked_path = "/tmp/engine/model"
        obj = engine._serializer_load(object_file_path=mocked_path)
        mocked_load.assert_called_once_with(mocked_path)
        assert obj == {"me": "here"}

    @mock.patch('joblib.load')
    def test__serializer_load_not_keras(self, mocked_load, engine):
        mocked_path = "/tmp/engine/dataset"
        mocked_load.return_value = {"me": "here"}
        obj = engine._serializer_load(object_file_path=mocked_path)
        mocked_load.assert_called_once_with(mocked_path)
        assert obj == {"me": "here"}

    def test__serializer_dump_keras(self, engine):
        mocked_obj = mock.MagicMock()
        mocked_path = "/tmp/engine/model"
        engine._serializer_dump(mocked_obj, object_file_path=mocked_path)
        mocked_obj.save.assert_called_once_with(mocked_path)

    @mock.patch('marvin_python_toolbox.engine_base.EngineBaseTraining._serializer_dump')
    def test__serializer_dump_not_keras(self, mocked_dump, engine):
        mocked_obj = mock.MagicMock()
        mocked_path = "/tmp/engine/dataset"
        engine._serializer_dump(mocked_obj, object_file_path=mocked_path)
        mocked_dump.assert_called_once_with(mocked_obj, mocked_path)

