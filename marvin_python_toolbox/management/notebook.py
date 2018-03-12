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

from __future__ import print_function

import os
import sys
import click


@click.group('notebook')
def cli():
    pass


@cli.command('notebook', help='Start the Jupyter notebook server.')
@click.option('--port', '-p', default=8888, help='Jupyter server port')
@click.option('--enable-security', is_flag=True, help='Enable jupyter notebook token security.')
@click.option('--spark-conf', '-c', envvar='SPARK_CONF_DIR', type=click.Path(exists=True), help='Spark configuration folder path to be used in this session')
@click.pass_context
def notebook_cli(ctx, port, enable_security, spark_conf):
    notebook(ctx, port, enable_security, spark_conf)


def notebook(ctx, port, enable_security, spark_conf):
    notebookdir = os.path.join(ctx.obj['base_path'], 'notebooks')
    command = [
        "SPARK_CONF_DIR={0} YARN_CONF_DIR={0}".format(spark_conf if spark_conf else os.path.join(os.environ["SPARK_HOME"], "conf")),
        'jupyter', 'notebook',
        '--notebook-dir', notebookdir,
        '--ip', '0.0.0.0',
        '--port', str(port),
        '--no-browser',
        '--config', os.path.join(os.environ["MARVIN_TOOLBOX_PATH"], 'extras', 'notebook_extensions', 'jupyter_notebook_config.py')
    ]

    command.append("--NotebookApp.token=") if not enable_security else None

    ret = os.system(' '.join(command))
    sys.exit(ret)
