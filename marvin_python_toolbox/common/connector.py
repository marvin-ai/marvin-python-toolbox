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

"""Marvin Connector module.

This module is responsible to create and provide diferents types of connectors.

"""


def get_gurobi_model(host='localhost'):
    """Return a remote Gurobi Model Object"""

    import rpyc

    conn = rpyc.classic.connect(host)
    m = conn.modules.gurobipy.Model()
    m.__conn = conn

    def _close(self):
        self._conn.close()

    m._close = _close

    return m

