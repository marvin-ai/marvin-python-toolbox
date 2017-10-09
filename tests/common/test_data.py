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

import os
import pytest
try:
    import mock
except ImportError:
    import unittest.mock as mock

from marvin_python_toolbox.common.data import MarvinData
from marvin_python_toolbox.common.exceptions import InvalidConfigException


@pytest.fixture
def data_path():
    return os.path.expanduser("/tmp/data")


@pytest.fixture
def data_path_key():
    return MarvinData._key


def test_read_from_env(data_path_key, data_path):
    os.environ[data_path_key] = data_path
    assert MarvinData.data_path == os.environ[data_path_key]


def test_path_not_set(data_path_key):
    del os.environ[data_path_key]
    path_ = None
    try:
        path_ = MarvinData.data_path
    except InvalidConfigException:
        assert not path_


@mock.patch('marvin_python_toolbox.common.data.check_path')
def test_unable_to_create_path(check_path, data_path_key, data_path):
    os.environ[data_path_key] = data_path
    check_path.return_value = False

    path_ = None
    try:
        path_ = MarvinData.data_path
    except InvalidConfigException:
        assert not path_


def test_load_data_from_filesystem(data_path_key, data_path):
    data = 'return value'

    # If the data was not found try to load from filesystem
    with mock.patch('marvin_python_toolbox.common.data.open', create=True) as mock_open:
        mock_open.return_value = mock.MagicMock(spec=file)
        mocked_fp = mock_open.return_value.__enter__.return_value
        mocked_fp.read.return_value = data
        content = MarvinData.load_data(os.path.join('named_features', 'brands.json'))

    mocked_fp.read.assert_called_once()
    assert content == data


def test_load_data_from_filesystem_exception(data_path_key, data_path):
    with mock.patch('marvin_python_toolbox.common.data.open') as mock_open:
        mock_open.side_effect = IOError

        # load_data should propagate IOError
        with pytest.raises(IOError):
            MarvinData.load_data(os.path.join('named_features', 'brands.json'))


def test_data_key_using_abspath(data_path_key, data_path):
    assert MarvinData._convert_path_to_key(os.path.join(data_path, 'brands.json')) == 'brands.json'
