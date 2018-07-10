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
from ..._logging import get_logger

logger = get_logger('engine_base_data_handler')
__all__ = ['KerasSerializer']


class KerasSerializer(object):
    def _serializer_load(self, object_file_path):
        if object_file_path.split(os.sep)[-1] == 'model':
            from keras.models import load_model

            logger.debug("Loading model {} using keras serializer.".format(object_file_path))
            return load_model(object_file_path)
        else:
            return super(KerasSerializer, self)._serializer_load(object_file_path)

    def _serializer_dump(self, obj, object_file_path):
        if object_file_path.split(os.sep)[-1] == 'model':
            logger.debug("Saving model {} using keras serializer.".format(object_file_path))
            obj.save(object_file_path)
        else:
            super(KerasSerializer, self)._serializer_dump(obj, object_file_path)
