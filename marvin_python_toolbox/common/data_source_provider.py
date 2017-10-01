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

"""Marvin Data Source module.

This module is responsible to create and provide diferents types of data source objects.

"""


def get_spark_session(enable_hive=False, app_name='marvin-engine', configs=[]):
    """Return a Spark Session object"""

    # Prepare spark context to be used
    import findspark
    findspark.init()
    from pyspark.sql import SparkSession

    # prepare spark sesseion to be returned
    spark = SparkSession.builder

    spark = spark.appName(app_name)
    spark = spark.enableHiveSupport() if enable_hive else spark

    # if has configs
    for config in configs:
        spark = spark.config(config)

    return spark.getOrCreate()
