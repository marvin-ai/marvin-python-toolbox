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
import click

from .._compatibility import six
from .._logging import get_logger

from .pkg import cli as cli_pkg
from .test import cli as cli_test
from .notebook import cli as cli_notebook
from .hive import cli as cli_hive
from .engine import cli as cli_engine

from ..config import parse_ini
from ..loader import load_commands_from_file


__all__ = ['create_cli']


logger = get_logger('management')

EXCLUDE_BY_TYPE = {
    'python-engine': ['engine-generate', 'engine-generateenv'],
    'tool': ['engine-server', 'engine-dryrun', 'engine-httpserver', 'engine-grpcserver', 'engine-deploy', 'engine-httpserver-remote']
}


VERSION_MSG = '''
  __  __            _____ __      __ _____  _   _       
 |  \/  |    /\    |  __ \\\ \    / /|_   _|| \ | |
 | \  / |   /  \   | |__) |\ \  / /   | |  |  \| | 
 | |\/| |  / /\ \  |  _  /  \ \/ /    | |  | . ` | 
 | |  | | / ____ \ | | \ \   \  /    _| |_ | |\  | 
 |_|  |_|/_/    \_\|_|  \_\   \/    |_____||_| \_| 
            _    _             _                 _  _                                                              
           | |  | |           | |               | || |                                                             
           | |_ | |__    ___  | |_  ___    ___  | || |__    ___ __  __                                             
           | __|| '_ \  / _ \ | __|/ _ \  / _ \ | || '_ \  / _ \\ \/ /                                             
  _  _  _  | |_ | | | ||  __/ | |_| (_) || (_) || || |_) || (_) |>  <                                              
 (_)(_)(_)  \__||_| |_| \___|  \__|\___/  \___/ |_||_.__/  \___//_/\_\ v%(version)s
'''


def create_cli(package_name, package_path, type_=None, exclude=None, config=None):
    base_path = os.path.abspath(os.path.join(package_path, '..'))

    if exclude is None:
        exclude = EXCLUDE_BY_TYPE.get(type_, [])

    if config is None:
        # Find the ini directory
        inifilename = 'marvin.ini'
        inidir = base_path

        # Load the ini file
        inipath = os.path.join(inidir, inifilename)
        config_defaults = {
            'inidir': inidir,
            'marvin_packagedir': '{inidir}/{marvin_package}',
        }
        if os.path.exists(inipath):
            config = parse_ini(inipath, config_defaults)
        else:
            config = {}

    exclude = config.get('marvin_exclude', ','.join(exclude))
    if isinstance(exclude, str):
        exclude = exclude.split(',')

    @click.group('custom')
    @click.option('--debug', is_flag=True, help='Enable debug mode.')
    @click.pass_context
    def cli(ctx, debug):
        ctx.obj = {
            'debug': debug,
            'package_name': package_name,
            'package_path': package_path,
            'base_path': base_path,
            'type': type_,
            'config': config,
        }

    # Load internal commands
    commands = {}
    commands.update(cli_pkg.commands)
    commands.update(cli_test.commands)
    commands.update(cli_notebook.commands)
    commands.update(cli_engine.commands)
    commands.update(cli_hive.commands)

    for name, command in commands.items():
        if name not in exclude:
            cli.add_command(command, name=name)

    # Load custom commands from project been managed
    commands_file_paths = [
        config.get('marvin_commandsfile'),
        os.path.join(base_path, 'marvin_commands.py'),
        os.path.join(base_path, 'commands.py')
    ]

    for commands_file_path in commands_file_paths:
        if commands_file_path and os.path.exists(commands_file_path):
            commands = load_commands_from_file(commands_file_path)
            for command in commands:
                cli.add_command(command)
            break

    # Add version and help messages
    from .. import __version__
    cli = click.version_option(version=__version__,
                               message=VERSION_MSG.replace('\n', '\n  '))(cli)

    cli.help = '\b{}\n'.format(VERSION_MSG % {'version': __version__})

    return cli
