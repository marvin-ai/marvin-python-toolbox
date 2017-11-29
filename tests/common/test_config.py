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
import os

try:
    import mock
except ImportError:
    import unittest.mock as mock

from marvin_python_toolbox.common.config import Config, load_conf_from_file
from marvin_python_toolbox.common.exceptions import InvalidConfigException


class TestConfig:
    def teardown_method(self, test_method):
        Config.reset()

    @mock.patch('marvin_python_toolbox.common.config.ConfigObj')
    def test_load_conf_from_file(self, ConfigParserMocked):
        filepath = '/path/to/config/file.ini'

        load_conf_from_file(filepath)

        ConfigParserMocked.assert_called_once_with(filepath)

    @mock.patch('marvin_python_toolbox.common.config.ConfigObj')
    @mock.patch('marvin_python_toolbox.common.config.os.getenv')
    def test_load_conf_from_env(self, getenv_mocked, ConfigParserMocked):
        filepath = '/path/to/config/file.ini'

        getenv_mocked.return_value = filepath
        load_conf_from_file()

        ConfigParserMocked.assert_called_once_with(filepath)

    @mock.patch('marvin_python_toolbox.common.config.ConfigObj')
    def test_load_conf_from_default_path(self, ConfigParserMocked):
        load_conf_from_file()

        ConfigParserMocked.assert_called_once_with(os.environ['DEFAULT_CONFIG_PATH'])

    @mock.patch('marvin_python_toolbox.common.config.ConfigObj')
    def test_load_conf_from_default_path_with_invalid_section(self, ConfigParserMocked):
        from ConfigParser import NoSectionError

        ConfigParserMocked.return_value.items.side_effect = NoSectionError('')
        assert len(load_conf_from_file(section='invalidsection')) == 0

    @mock.patch('marvin_python_toolbox.common.config.load_conf_from_file')
    def test_get(self, load_conf_from_file_mocked, config_fixture):
        load_conf_from_file_mocked.return_value = config_fixture
        assert Config.get('key') == config_fixture['key']

    @mock.patch('marvin_python_toolbox.common.config.load_conf_from_file')
    def test_get_invalid_key(self, load_conf_from_file_mocked, config_fixture):
        load_conf_from_file_mocked.return_value = config_fixture
        assert 'invalidkey' not in config_fixture
        with pytest.raises(InvalidConfigException):
            Config.get('invalidkey')

    @mock.patch('marvin_python_toolbox.common.config.load_conf_from_file')
    def test_get_invalid_key_with_default(self, load_conf_from_file_mocked, config_fixture):
        load_conf_from_file_mocked.return_value = config_fixture
        assert 'invalidkey' not in config_fixture
        assert Config.get('invalidkey', default='default_value') == 'default_value'

    @mock.patch('marvin_python_toolbox.common.config.load_conf_from_file')
    def test_get_with_invalid_section(self, load_conf_from_file_mocked, config_fixture):
        load_conf_from_file_mocked.return_value = {}
        with pytest.raises(InvalidConfigException):
            Config.get('key', section='invalidsection')

    @mock.patch('marvin_python_toolbox.common.config.load_conf_from_file')
    def test_keys_alread_loaded(self, load_conf_from_file_mocked, config_fixture):
        load_conf_from_file_mocked.return_value = config_fixture
        Config._load()
        assert Config.keys() == config_fixture.keys()

    @mock.patch('marvin_python_toolbox.common.config.load_conf_from_file')
    def test_keys(self, load_conf_from_file_mocked, config_fixture):
        load_conf_from_file_mocked.return_value = config_fixture
        assert Config.keys() == config_fixture.keys()

    @mock.patch('marvin_python_toolbox.common.config.load_conf_from_file')
    def test_keys_with_invalid_section(self, load_conf_from_file_mocked):
        load_conf_from_file_mocked.return_value = {}
        assert Config.keys(section='invalidsection') == []

    @mock.patch('os.getenv')
    def test_read_with_real_file(self, env_read):
        env_read.return_value = 'tests/fixtures/config.sample'
        assert Config.get('models.default_context_name') == 'pdl'
        assert Config.get('models.default_context_name', section='section') == 'pdl2'
        assert Config.get('models.default_type_name') == 'pdl'
        assert Config.get('models.default_type_name') == Config.get('models.default_type_name', section='section')

