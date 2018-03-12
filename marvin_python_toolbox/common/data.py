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

"""Data Module.

"""

import os
import requests
import progressbar

# Use six to create code compatible with Python 2 and 3.
# See http://pythonhosted.org/six/
from .._compatibility import six
from .utils import check_path
from .exceptions import InvalidConfigException
from six import with_metaclass
from .._logging import get_logger

logger = get_logger('common.data')


class AbstractMarvinData(type):
    @property
    def data_path(cls):
        return cls.get_data_path()


class MarvinData(with_metaclass(AbstractMarvinData)):
    _key = 'MARVIN_DATA_PATH'

    @classmethod
    def get_data_path(cls):
        """
        Read data path from the following sources in order of priority:

        1. Environment variable

        If not found raises an exception

        :return: str - datapath
        """
        marvin_path = os.environ.get(cls._key)
        if not marvin_path:
            raise InvalidConfigException('Data path not set!')

        is_path_created = check_path(marvin_path, create=True)
        if not is_path_created:
            raise InvalidConfigException('Data path does not exist!')

        return marvin_path

    @classmethod
    def _convert_path_to_key(cls, path):
        if path.startswith(os.path.sep):
            path = os.path.relpath(path, start=cls.data_path)
        return '/'.join(path.split(os.path.sep))

    @classmethod
    def load_data(cls, relpath):
        """
        Load data from the following sources in order of priority:

        1. Filesystem

        :param relpath: path relative to "data_path"
        :return: str - data content
        """
        filepath = os.path.join(cls.data_path, relpath)
        with open(filepath) as fp:
            content = fp.read()

        return content

    @classmethod
    def download_file(cls, url, local_file_name=None, force=False, chunk_size=1024):
        """
        Download file from a given url
        """

        local_file_name = local_file_name if local_file_name else url.split('/')[-1]
        filepath = os.path.join(cls.data_path, local_file_name)

        if not os.path.exists(filepath) or force:
            try:
                headers = requests.head(url, allow_redirects=True).headers
                length = headers.get('Content-Length')

                logger.info("Starting download of {} file with {} bytes ...".format(url, length))

                widgets = [
                    'Downloading file please wait...', progressbar.Percentage(),
                    ' ', progressbar.Bar(),
                    ' ', progressbar.ETA(),
                    ' ', progressbar.FileTransferSpeed(),
                ]
                bar = progressbar.ProgressBar(widgets=widgets, max_value=int(length) + chunk_size).start()

                r = requests.get(url, stream=True)

                with open(filepath, 'wb') as f:
                    total_chunk = 0

                    for chunk in r.iter_content(chunk_size):
                        if chunk:
                            f.write(chunk)
                            total_chunk += chunk_size
                            bar.update(total_chunk)

                bar.finish()

            except:
                if os.path.exists(filepath):
                    os.remove(filepath)

                raise

        return filepath
