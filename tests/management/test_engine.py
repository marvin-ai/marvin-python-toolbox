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


from marvin_python_toolbox.management.engine import MarvinDryRun
from marvin_python_toolbox.management.engine import dryrun


class mocked_ctx(object):
    obj = {'package_name': 'test_package'}


class mocked_acquisitor():
    def __init__(self, persistence_mode, is_remote_calling, default_root_path):
        self.persistence_mode = persistence_mode
        self.is_remote_calling = is_remote_calling
        self.default_root_path = default_root_path

    def execute(self, **kwargs):
        print ('test')


@mock.patch('marvin_python_toolbox.management.engine.time.time')
@mock.patch('marvin_python_toolbox.management.engine.MarvinDryRun')
@mock.patch('marvin_python_toolbox.management.engine.sys.exit')
@mock.patch('marvin_python_toolbox.management.engine.os.system')
def test_dryrun(system_mocked, exit_mocked, MarvinDryRun_mocked, time_mocked):
    params = '/tmp/params'
    messages_file = '/tmp/messages'
    feedback_file = '/tmp/feedback'
    action = 'all'
    spark_conf = '/opt/spark/conf'
    time_mocked.return_value = 555

    dryrun(ctx=mocked_ctx, action=action, params_file=params, messages_file=messages_file, feedback_file=feedback_file, initial_dataset=None, dataset=None, model=None, metrics=None, response=False, spark_conf=spark_conf, profiling=None)

    time_mocked.assert_called()
    exit_mocked.assert_called_with("Stoping process!")
    MarvinDryRun_mocked.assert_called_with(ctx=mocked_ctx, messages=[{}, {}], print_response=False)

    MarvinDryRun_mocked.return_value.execute.assert_called_with(clazz='Feedback', dataset=None, initial_dataset=None, metrics=None, model=None, params={}, profiling_enabled=None)

    action = 'acquisitor'

    dryrun(ctx=mocked_ctx, action=action, params_file=params, messages_file=messages_file, feedback_file=feedback_file, initial_dataset=None, dataset=None, model=None, metrics=None, response=False, spark_conf=spark_conf, profiling=None)

    time_mocked.assert_called()
    MarvinDryRun_mocked.assert_called_with(ctx=mocked_ctx, messages=[{}, {}], print_response=False)


@mock.patch('marvin_python_toolbox.management.engine.json.dumps')
@mock.patch('marvin_python_toolbox.management.engine.dynamic_import')
def test_marvindryrun(import_mocked, dumps_mocked):
    messages = ['/tmp/messages', '/tmp/feedback']
    response = 'response'
    clazz = 'PredictionPreparator'
    import_mocked.return_value = mocked_acquisitor

    test_dryrun = MarvinDryRun(ctx=mocked_ctx, messages=messages, print_response=response)
    test_dryrun.execute(clazz=clazz, params=None, initial_dataset=None, dataset=None, model=None, metrics=None, profiling_enabled=True)

    import_mocked.assert_called_with("{}.{}".format('test_package', 'PredictionPreparator'))
    dumps_mocked.assert_called_with(None, indent=4, sort_keys=True)

    clazz = 'Feedback'
    test_dryrun.execute(clazz=clazz, params=None, initial_dataset=None, dataset=None, model=None, metrics=None, profiling_enabled=False)

    import_mocked.assert_called_with("{}.{}".format('test_package', 'Feedback'))

    clazz = 'Predictor'
    test_dryrun.execute(clazz=clazz, params=None, initial_dataset=None, dataset=None, model=None, metrics=None, profiling_enabled=False)

    import_mocked.assert_called_with("{}.{}".format('test_package', 'PredictionPreparator'))

    clazz = 'test'
    test_dryrun.execute(clazz=clazz, params=None, initial_dataset=None, dataset=None, model=None, metrics=None, profiling_enabled=True)
    test_dryrun.execute(clazz=clazz, params=None, initial_dataset=None, dataset=None, model=None, metrics=None, profiling_enabled=False)

    import_mocked.assert_called_with("{}.{}".format('test_package', 'test'))

    response = False
    clazz = 'PredictionPreparator'

    MarvinDryRun(ctx=mocked_ctx, messages=messages, print_response=response)
    test_dryrun = MarvinDryRun(ctx=mocked_ctx, messages=messages, print_response=response)
    test_dryrun.execute(clazz=clazz, params=None, initial_dataset=None, dataset=None, model=None, metrics=None, profiling_enabled=False)

    dumps_mocked.assert_called_with(None, indent=4, sort_keys=True)
