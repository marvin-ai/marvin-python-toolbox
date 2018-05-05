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
from io import IOBase


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
        mock_open.return_value = mock.MagicMock(spec=IOBase)
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


@mock.patch('marvin_python_toolbox.common.data.progressbar')
@mock.patch('marvin_python_toolbox.common.data.requests')
def test_download_file(mocked_requests, mocked_progressbar):
    file_url = 'google.com/file.json'
    file_path = MarvinData.download_file(file_url)
    assert file_path == '/tmp/data/file.json'

    file_path = MarvinData.download_file(file_url, local_file_name='myfile')
    assert file_path == '/tmp/data/myfile'

@mock.patch('marvin_python_toolbox.common.data.progressbar')
@mock.patch('marvin_python_toolbox.common.data.requests')
def test_download_file_delete_file_if_exception(mocked_requests, mocked_progressbar):
    mocked_requests.get.side_effect = Exception()
    with open('/tmp/data/error.json', 'w') as f:
        f.write('test')
    
    file_url = 'google.com/error.json'
    with pytest.raises(Exception) as excinfo:
        file_path = MarvinData.download_file(file_url, force=True)

    assert os.path.exists('/tmp/data/error.json') is False

@mock.patch('marvin_python_toolbox.common.data.progressbar.ProgressBar')
@mock.patch('marvin_python_toolbox.common.data.requests')
def test_download_file_write_file_if_content(mocked_requests, mocked_progressbar):
    from requests import Response
    file_url = 'google.com/file.json'

    response = mock.Mock(spec=Response)
    response.iter_content.return_value = 'x'
    mocked_requests.get.return_value = response
        
    mocked_open = mock.mock_open()
    with mock.patch('marvin_python_toolbox.common.data.open', mocked_open, create=True):
        MarvinData.download_file(file_url, force=True)

    mocked_open.assert_called_once_with('/tmp/data/file.json', 'wb')
    handle = mocked_open()
    handle.write.assert_called_once_with('x')

@mock.patch('marvin_python_toolbox.common.data.progressbar.ProgressBar')
@mock.patch('marvin_python_toolbox.common.data.requests')
def test_download_file_dont_write_file_if_no_content(mocked_requests, mocked_progressbar):
    from requests import Response
    file_url = 'google.com/file.json'

    response = mock.Mock(spec=Response)
    response.iter_content.return_value = ''
    mocked_requests.get.return_value = response
        
    mocked_open = mock.mock_open()
    with mock.patch('marvin_python_toolbox.common.data.open', mocked_open, create=True):
        MarvinData.download_file(file_url, force=True)

    mocked_open.assert_called_once_with('/tmp/data/file.json', 'wb')
    handle = mocked_open()
    assert handle.write.call_count == 0