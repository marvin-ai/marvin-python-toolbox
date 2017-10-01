#!/usr/bin/env python
# coding=utf-8

import os.path

from .data_handler import *
from .prediction import *
from .training import *


# Get package version number from "VERSION" file
with open(os.path.join(os.path.dirname(__file__), 'VERSION'), 'rb') as f:
    __version__ = f.read().decode('ascii').strip()

