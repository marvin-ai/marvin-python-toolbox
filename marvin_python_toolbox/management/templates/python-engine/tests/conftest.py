#!/usr/bin/env python
# coding=utf-8

import os
import pytest

os.environ['TESTING'] = 'True'


@pytest.fixture
def mocked_params():
    return {'params': 1}

