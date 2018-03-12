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

import os
import json
import subprocess
import cProfile
import pstats
import uuid
from functools import wraps
from .._compatibility import StringIO

from .._logging import get_logger

logger = get_logger('profiling')


class Profile(cProfile.Profile):
    def __init__(self, sortby='tottime', *args, **kwargs):
        self.sortby = sortby
        self.image_path = None
        super(Profile, self).__init__(*args, **kwargs)

    def _repr_html_(self):
        s = StringIO()
        stats = pstats.Stats(self, stream=s).sort_stats(self.sortby)
        stats.print_stats(10)
        stats_value = s.getvalue()
        html = '<pre>{}</pre>'.format(stats_value)
        if self.image_path:
            html += '<img src="{}" style="margin: 0 auto;">'.format(self.image_path)
        return html


class profiling(object):
    def __init__(self, enable=True, output_path='profiling', uid=uuid.uuid4, info=None, sortby='tottime'):
        self.enable = enable
        self.output_path = output_path
        self.uid = uid
        self.info = info
        self.sortby = sortby

        self.enable_profiling = enable

    def __call__(self, func):

        @wraps(func)
        def func_wrapper(*args, **kwargs):
            enable_ = self.enable
            if callable(enable_):
                enable_ = enable_(*args, **kwargs)
                self.enable_profiling = bool(enable_)

            if self.enable_profiling:
                self.__enter__()
            response = None
            try:
                response = func(*args, **kwargs)
            except Exception:
                raise
            finally:
                if self.enable_profiling:
                    output_path_ = self.output_path
                    if callable(output_path_):
                        self.output_path = output_path_(*args, **kwargs)
                    uid_ = self.uid
                    if callable(uid_):
                        self.uid = uid_()
                    info_ = self.info
                    if callable(info_):
                        self.info = info_(response, *args, **kwargs)

                    self.__exit__(None, None, None)

            return response

        return func_wrapper

    def __enter__(self):
        pr = None
        if self.enable_profiling:
            pr = Profile(sortby=self.sortby)
            pr.enable()
        self.pr = pr
        return pr

    def __exit__(self, type, value, traceback):
        if self.enable_profiling:
            pr = self.pr
            pr.disable()
            # args accept functions
            output_path = self.output_path
            uid = self.uid
            info = self.info
            if callable(uid):
                uid = uid()

            # make sure the output path exists
            if not os.path.exists(output_path):  # pragma: no cover
                os.makedirs(output_path, mode=0o774)

            # collect profiling info
            stats = pstats.Stats(pr)
            stats.sort_stats(self.sortby)
            info_path = os.path.join(output_path, '{}.json'.format(uid))
            stats_path = os.path.join(output_path, '{}.pstats'.format(uid))
            dot_path = os.path.join(output_path, '{}.dot'.format(uid))
            png_path = os.path.join(output_path, '{}.png'.format(uid))
            if info:
                try:
                    with open(info_path, 'w') as fp:
                        json.dump(info, fp, indent=2, encoding='utf-8')
                except Exception as e:
                    logger.error('An error occurred while saving %s: %s.', info_path, e)
            stats.dump_stats(stats_path)
            # create profiling graph
            try:
                subprocess.call(['gprof2dot', '-f', 'pstats', '-o', dot_path, stats_path])
                subprocess.call(['dot', '-Tpng', '-o', png_path, dot_path])
                pr.image_path = png_path
            except Exception:
                logger.error('An error occurred while creating profiling image! '
                             'Please make sure you have installed GraphViz.')
            logger.info('Saving profiling data (%s)', stats_path[:-7])
