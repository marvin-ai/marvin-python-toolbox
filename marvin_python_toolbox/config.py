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
import os.path
import copy

import configparser

from ._compatibility import six
from ._logging import get_logger


__all__ = ['find_inidir', 'parse_ini']


logger = get_logger('config')


def find_inidir(inifilename='marvin.ini'):
    inidir = None
    currentdir = os.getcwd()

    while True:
        logger.debug('Looking for marvinini in {}'.format(currentdir))
        if os.path.exists(os.path.join(currentdir, inifilename)):
            inidir = currentdir
            logger.debug('marvinini found {}'.format(inidir))
            break

        parentdir = os.path.abspath(os.path.join(currentdir, os.pardir))
        if currentdir == parentdir:
            # currentdir is '/'
            logger.debug('marvinini not found')
            break

        currentdir = parentdir

    return inidir


def parse_ini(inipath, defaults=None):
    if defaults is None:
        defaults = {}

    logger.debug("Parsing marvinini '{}' with defaults '{}'".format(inipath, defaults))

    config_raw = configparser.ConfigParser()
    config_raw.read(inipath)

    config = copy.deepcopy(defaults)

    for section in config_raw.sections():
        # Firt pass
        for key, value in config_raw.items(section):
            key = '_'.join((section, key)).lower()
            logger.debug('Processing {}: {}'.format(key, value))
            processed_value = value.format(**config)
            config[key] = processed_value

    # Second pass
    for key, value in config.items():
        processed_value = value.format(**config)
        if ',' in processed_value:
            processed_value = processed_value.split(',')
        config[key] = processed_value

    logger.debug('marvinini loaded: {}'.format(config))

    return config
