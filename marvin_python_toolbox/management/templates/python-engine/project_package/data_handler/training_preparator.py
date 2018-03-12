#!/usr/bin/env python
# coding=utf-8

"""TrainingPreparator engine action.

Use this module to add the project main code.
"""

from .._compatibility import six
from .._logging import get_logger

from marvin_python_toolbox.engine_base import EngineBaseDataHandler

__all__ = ['TrainingPreparator']


logger = get_logger('training_preparator')


class TrainingPreparator(EngineBaseDataHandler):

    def __init__(self, **kwargs):
        super(TrainingPreparator, self).__init__(**kwargs)

    def execute(self, params, **kwargs):
        """
        Setup the dataset with the transformed data that is compatible with the algorithm used to build the model in the next action.
        Use the self.initial_dataset prepared in the last action as source of data.

        Eg.

            self.marvin_dataset = {...}
        """
        self.marvin_dataset = {}

