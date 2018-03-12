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

from abc import ABCMeta
from .._compatibility import six
from .._logging import get_logger

from .engine_base_action import EngineBaseBatchAction


__all__ = ['EngineBaseTraining']
logger = get_logger('engine_base_training')


class EngineBaseTraining(EngineBaseBatchAction):
    __metaclass__ = ABCMeta

    _dataset = None
    _model = None
    _metrics = None

    def __init__(self, **kwargs):
        self._dataset = self._get_arg(kwargs=kwargs, arg='dataset')
        self._model = self._get_arg(kwargs=kwargs, arg='model')
        self._metrics = self._get_arg(kwargs=kwargs, arg='metrics')

        super(EngineBaseTraining, self).__init__(**kwargs)

    @property
    def marvin_dataset(self):
        return self._load_obj(object_reference='_dataset')

    @marvin_dataset.setter
    def marvin_dataset(self, dataset):
        self._save_obj(object_reference='_dataset', obj=dataset)

    @property
    def marvin_model(self):
        return self._load_obj(object_reference='_model')

    @marvin_model.setter
    def marvin_model(self, model):
        self._save_obj(object_reference='_model', obj=model)

    @property
    def marvin_metrics(self):
        return self._load_obj(object_reference='_metrics')

    @marvin_metrics.setter
    def marvin_metrics(self, metrics):
        self._save_obj(object_reference='_metrics', obj=metrics)

