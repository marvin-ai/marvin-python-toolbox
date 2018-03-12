#!/usr/bin/env python
# coding=utf-8

"""Trainer engine action.

Use this module to add the project main code.
"""

from .._compatibility import six
from .._logging import get_logger

from marvin_python_toolbox.engine_base import EngineBaseTraining

__all__ = ['Trainer']


logger = get_logger('trainer')


class Trainer(EngineBaseTraining):

    def __init__(self, **kwargs):
        super(Trainer, self).__init__(**kwargs)

    def execute(self, params, **kwargs):
        """
        Setup the model with the result of the algorithm used to training.
        Use the self.dataset prepared in the last action as source of data.

        Eg.

            self.marvin_model = {...}
        """
        self.marvin_model = {}
