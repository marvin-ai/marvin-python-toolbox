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

import sys
import os
import os.path
import subprocess
import shutil
import tempfile
import click

from .pkg import copy


@click.group('test')
def cli():
    pass


@cli.command('test', help='Run tests.')
@click.option('--cov/--no-cov', default=True)
@click.option('--no-capture', is_flag=True)
@click.option('--pdb', is_flag=True)
@click.argument('args', default='')
@click.pass_context
def test(ctx, cov, no_capture, pdb, args):
    os.environ['TESTING'] = 'true'

    if args:
        args = args.split(' ')
    else:
        args = ['tests']

    if no_capture:
        args += ['--capture=no']

    if pdb:
        args += ['--pdb']

    cov_args = []
    if cov:
        cov_args += ['--cov', os.path.relpath(ctx.obj['package_path'],
                                              start=ctx.obj['base_path']),
                     '--cov-report', 'html',
                     '--cov-report', 'xml',
                     '--cov-report', 'term-missing',
                     ]

    command = ['py.test'] + cov_args + args
    print(' '.join(command))
    env = os.environ.copy()
    exitcode = subprocess.call(command, cwd=ctx.obj['base_path'], env=env)
    sys.exit(exitcode)


@cli.command('test-tox', help='Run tests using a new virtualenv.')
@click.argument('args', default='')
@click.pass_context
def tox(ctx, args):
    os.environ['TESTING'] = 'true'

    if args:
        args = ['-a'] + args.split(' ')
    else:
        args = []
    # Copy the project to a tmp dir
    tmp_dir = tempfile.mkdtemp()
    tox_dir = os.path.join(tmp_dir, ctx.obj['package_name'])
    copy(ctx.obj['base_path'], tox_dir)
    command = ['python', 'setup.py', 'test'] + args
    env = os.environ.copy()
    exitcode = subprocess.call(command, cwd=tox_dir, env=env)
    shutil.rmtree(tmp_dir)
    sys.exit(exitcode)


@cli.command('test-tdd', help='Watch for changes to run tests automatically.')
@click.option('--cov/--no-cov', default=False)
@click.option('--no-capture', is_flag=True)
@click.option('--pdb', is_flag=True)
@click.option('--partial', is_flag=True)
@click.argument('args', default='')
@click.pass_context
def tdd(ctx, cov, no_capture, pdb, partial, args):
    os.environ['TESTING'] = 'true'

    if args:
        args = args.split(' ')
    else:
        args = [os.path.relpath(
            os.path.join(ctx.obj['base_path'], 'tests'))]

    if no_capture:
        args += ['--capture=no']

    if pdb:
        args += ['--pdb']

    if partial:
        args += ['--testmon']

    cov_args = []
    if cov:
        cov_args += ['--cov', os.path.relpath(ctx.obj['package_path'],
                                              start=ctx.obj['base_path']),
                     '--cov-report', 'html',
                     '--cov-report', 'xml',
                     '--cov-report', 'term-missing',
                     ]

    command = ['ptw', '-p', '--'] + cov_args + args
    print(' '.join(command))
    env = os.environ.copy()
    exitcode = subprocess.call(command, cwd=ctx.obj['base_path'], env=env)
    sys.exit(exitcode)


@cli.command('test-checkpep8', help='Check python code style.')
@click.pass_context
def pep8(ctx):
    command = ['pep8', ctx.obj['package_name']]
    exitcode = subprocess.call(command, cwd=ctx.obj['base_path'])
    if exitcode == 0:
        print('Congratulations! Everything looks good.')
    sys.exit(exitcode)
