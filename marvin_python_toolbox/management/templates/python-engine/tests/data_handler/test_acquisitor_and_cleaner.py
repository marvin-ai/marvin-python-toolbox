#!/usr/bin/env python
# coding=utf-8

try:
    import mock

except ImportError:
    import unittest.mock as mock

from {{project.package}}.data_handler import AcquisitorAndCleaner


class TestAcquisitorAndCleaner:
    def test_execute(self, mocked_params):
        ac = AcquisitorAndCleaner()
        ac.execute(params=mocked_params)
        assert not ac._params

