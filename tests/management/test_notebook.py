#!/usr/bin/env python
# coding=utf-8

# Copyright [2017] [B2W Digital]
#
# Licensed under the Apache License, Version 2.0 (the 'License');
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an 'AS IS' BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# from click.testing import CliRunner

try:
    import mock
except ImportError:
    import unittest.mock as mock

import os
from marvin_python_toolbox.management.notebook import notebook


class mocked_ctx(object):
    obj = {'base_path': '/tmp'}


@mock.patch('marvin_python_toolbox.management.notebook.sys')
@mock.patch('marvin_python_toolbox.management.notebook.os.system')
def test_notebook(system_mocked, sys_mocked):
    ctx = mocked_ctx()
    port = 8888
    enable_security = False
    spark_conf = '/opt/spark/conf'
    system_mocked.return_value = 1

    notebook(ctx, port, enable_security, spark_conf)

    system_mocked.assert_called_once_with('SPARK_CONF_DIR=/opt/spark/conf YARN_CONF_DIR=/opt/spark/conf jupyter notebook --notebook-dir /tmp/notebooks --ip 0.0.0.0 --port 8888 --no-browser --config ' + os.environ["MARVIN_ENGINE_PATH"] + '/marvin_python_toolbox/extras/notebook_extensions/jupyter_notebook_config.py --NotebookApp.token=')


@mock.patch('marvin_python_toolbox.management.notebook.sys')
@mock.patch('marvin_python_toolbox.management.notebook.os.system')
def test_notebook_with_security(system_mocked, sys_mocked):
    ctx = mocked_ctx()
    port = 8888
    enable_security = True
    spark_conf = '/opt/spark/conf'
    system_mocked.return_value = 1

    notebook(ctx, port, enable_security, spark_conf)

    system_mocked.assert_called_once_with('SPARK_CONF_DIR=/opt/spark/conf YARN_CONF_DIR=/opt/spark/conf jupyter notebook --notebook-dir /tmp/notebooks --ip 0.0.0.0 --port 8888 --no-browser --config ' + os.environ["MARVIN_ENGINE_PATH"] + '/marvin_python_toolbox/extras/notebook_extensions/jupyter_notebook_config.py')
