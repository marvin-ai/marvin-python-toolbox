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

"""Compatibility module.

Import this module to help to write code compatible with Python 2 and 3.
"""

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import
from __future__ import unicode_literals
from six.moves.urllib.parse import urlparse, quote
from six import StringIO, iteritems, text_type
from six.moves import xrange
import six

__all__ = ['six']

# Add here any code that have to differentiate between python 2 and 3.
