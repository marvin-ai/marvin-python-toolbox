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

import findspark
findspark.init()

# is important to import these classes after findspark.init call
from pyspark.tests import ReusedPySparkTestCase
from marvin_python_toolbox.common.data_source_provider import get_spark_session

try:
    import mock
except ImportError:
    import unittest.mock as mock


class TestDataSourceProvider:
    @mock.patch("pyspark.sql.SparkSession")
    def test_get_spark_session(self, mocked_session):
        spark = get_spark_session()
        assert spark
        mocked_session.assert_has_calls([
            mock.call.builder.appName('marvin-engine'),
            mock.call.builder.appName().getOrCreate()]
        )

        spark = get_spark_session(app_name='TestEngine')
        assert spark
        mocked_session.assert_has_calls([
            mock.call.builder.appName('TestEngine'),
            mock.call.builder.appName().getOrCreate()]
        )

        spark = get_spark_session(configs=[("spark.xxx", "true")])
        assert spark
        mocked_session.assert_has_calls([
            mock.call.builder.appName('TestEngine'),
            mock.call.builder.appName().getOrCreate()]
        )

    @mock.patch("pyspark.sql.SparkSession")
    def test_get_spark_session_with_hive(self, mocked_session):
        spark = get_spark_session(enable_hive=True)
        assert spark

        mocked_session.assert_has_calls([
            mock.call.builder.appName('marvin-engine'),
            mock.call.builder.appName().enableHiveSupport(),
            mock.call.builder.appName().enableHiveSupport().getOrCreate()]
        )


class TestSparkDataSource(ReusedPySparkTestCase):
    def test_spark_initialization(self):
        rdd = self.sc.parallelize(['Hi there', 'Hi'])
        counted = rdd.flatMap(lambda word: word.split(' ')).map(lambda word: (word, 1)).reduceByKey(lambda acc, n: acc + n)
        assert counted.collectAsMap() == {'Hi': 2, 'there': 1}
