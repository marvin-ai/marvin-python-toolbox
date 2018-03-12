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

"""Configuration module.
"""

import os
from configparser import ConfigParser, NoSectionError
from configobj import ConfigObj

# Use six to create code compatible with Python 2 and 3.
# See http://pythonhosted.org/six/
from .._compatibility import six
from .._logging import get_logger

from .exceptions import InvalidConfigException
from .utils import from_json


__all__ = ['Configuration', 'Config', 'load_conf_from_file']


logger = get_logger('core')


def load_conf_from_file(path=None, section='marvin'):
    data = {}
    config_parser = ConfigParser()
    config_path = path  # try to get config path from args
    if not config_path:  # try to get config file from env
        config_path = os.getenv('MARVIN_CONFIG_FILE') or os.getenv('CONFIG_FILE')
    if not config_path:  # use default file
        config_path = os.getenv("DEFAULT_CONFIG_PATH")
    logger.info('Loading configuration values from "{path}"...'.format(path=config_path))
    config_parser = ConfigObj(config_path)
    try:
        data = config_parser[section]
    except NoSectionError:
        pass

    return data


DEFAULT_PREFIX = 'marvin.'
DEFAULT_SECT = 'marvin'


class Configuration(object):
    """
    Abstracts persistent configuration.

    Reads configurations and defaults from a `/etc/marvin/marvin.ini` file.

    Usage:

        Configuration.get('my.key')

    """
    _conf = {}
    _default_sect = DEFAULT_SECT
    PREFIX = DEFAULT_PREFIX

    @classmethod
    def reset(cls):
        cls._conf = {}
        cls._default_sect = DEFAULT_SECT
        cls.PREFIX = DEFAULT_PREFIX

    @classmethod
    def _load(cls, section=None):
        section = section or cls._default_sect
        cls._conf[section] = load_conf_from_file(section=section)

    @classmethod
    def get(cls, key, section=None, **kwargs):
        """
        Retrieves a config value from dict.
        If not found twrows an InvalidScanbooconfigException.
        """
        section = section or cls._default_sect
        if section not in cls._conf:
            cls._load(section=section)

        value = cls._conf[section].get(key)

        # if not found in context read default
        if not value and section != cls._default_sect:
            value = cls._conf[cls._default_sect].get(key) if cls._default_sect in cls._conf else None

        if value is None:
            if 'default' in kwargs:  # behave as {}.get(x, default='fallback')
                _def_value = kwargs['default']
                logger.warn("Static configuration [{}] was not found. Using the default value [{}].".format(key, _def_value))
                return _def_value
            else:
                raise InvalidConfigException(u'Not found entry: {}'.format(key))

        try:
            value = from_json(value)  # parse value
        except (TypeError, ValueError):
            pass  # if not json parseable, then keep the string value

        return value

    @classmethod
    def keys(cls, section=None):
        """Get a list with all config keys"""
        section = section or cls._default_sect
        if section not in cls._conf:
            cls._load(section=section)
        return cls._conf[section].keys()


# Alias
Config = Configuration

