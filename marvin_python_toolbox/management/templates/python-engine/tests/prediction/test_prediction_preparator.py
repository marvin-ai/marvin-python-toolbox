#!/usr/bin/env python
# coding=utf-8

try:
    import mock

except ImportError:
    import unittest.mock as mock

from {{project.package}}.prediction import PredictionPreparator


class TestPredictionPreparator:
    def test_execute(self, mocked_params):
        ac = PredictionPreparator()
        ac.execute(input_message="fake message", params=mocked_params)
        assert not ac._params
