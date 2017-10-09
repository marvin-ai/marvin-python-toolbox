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

try:
    import mock
except ImportError:
    import unittest.mock as mock

from marvin_python_toolbox.loader import load_commands_from_file


@mock.patch("marvin_python_toolbox.loader.isinstance")
@mock.patch("marvin_python_toolbox.loader.getmembers")
@mock.patch("marvin_python_toolbox.loader.imp.load_source")
def test_load_commands_from_file(load_source_mocked, getmembers_mocked, isinstance_mocked):
    path = '/tmp'
    load_source_mocked.return_value = 'source'

    commands = load_commands_from_file(path)

    load_source_mocked.assert_called_once_with('custom_commands', '/tmp')
    getmembers_mocked.assert_called_once_with('source')

    assert commands == []
