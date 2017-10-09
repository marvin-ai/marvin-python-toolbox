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

import os
import shutil
import tempfile
import uuid
import pytest

try:
    import mock
except ImportError:
    import unittest.mock as mock

from marvin_python_toolbox.common.profiling import profiling


class TestProfiling:

    def test_decorator_file_creation(self):
        output_path = tempfile.mkdtemp()
        uid = str(uuid.uuid4())

        @profiling(output_path=output_path, uid=uid, info={'test': 42})
        def foo():
            return

        foo()

        assert os.path.isfile(os.path.join(output_path, uid + '.pstats'))
        assert os.path.isfile(os.path.join(output_path, uid + '.dot'))
        assert os.path.isfile(os.path.join(output_path, uid + '.png'))
        assert os.path.isfile(os.path.join(output_path, uid + '.json'))

        shutil.rmtree(output_path)

    def test_decorator_disabled(self):
        output_path = tempfile.mkdtemp()
        uid = str(uuid.uuid4())

        @profiling(enable=False, output_path=output_path, uid=uid, info={'test': 42})
        def foo():
            return

        foo()

        assert not os.path.isfile(os.path.join(output_path, uid + '.pstats'))
        assert not os.path.isfile(os.path.join(output_path, uid + '.dot'))
        assert not os.path.isfile(os.path.join(output_path, uid + '.png'))
        assert not os.path.isfile(os.path.join(output_path, uid + '.json'))

        shutil.rmtree(output_path)

    def test_context_manager_file_creation(self):
        output_path = tempfile.mkdtemp()
        uid = str(uuid.uuid4())

        with profiling(output_path=output_path, uid=uid, info={'test': 42}) as prof:
            def foo():
                return

            foo()

        assert os.path.isfile(os.path.join(output_path, uid + '.pstats'))
        assert os.path.isfile(os.path.join(output_path, uid + '.dot'))
        assert os.path.isfile(os.path.join(output_path, uid + '.png'))
        assert os.path.isfile(os.path.join(output_path, uid + '.json'))

        shutil.rmtree(output_path)

    def test_context_manager_disabled(self):
        output_path = tempfile.mkdtemp()
        uid = str(uuid.uuid4())

        with profiling(enable=False, output_path=output_path, uid=uid, info={'test': 42}) as prof:
            def foo():
                return

            foo()

        assert not os.path.isfile(os.path.join(output_path, uid + '.pstats'))
        assert not os.path.isfile(os.path.join(output_path, uid + '.dot'))
        assert not os.path.isfile(os.path.join(output_path, uid + '.png'))
        assert not os.path.isfile(os.path.join(output_path, uid + '.json'))

        shutil.rmtree(output_path)

    def test_callable_param(self):
        output_path = tempfile.mkdtemp()
        uid = str(uuid.uuid4())

        @profiling(enable=lambda *args, **kwargs: True, output_path=lambda *args, **kwargs: output_path, uid=lambda *args, **kwargs: uid, info=lambda *args, **kwargs: {'test': 42})
        def foo():
            return

        foo()

        assert os.path.isfile(os.path.join(output_path, uid + '.pstats'))
        assert os.path.isfile(os.path.join(output_path, uid + '.dot'))
        assert os.path.isfile(os.path.join(output_path, uid + '.png'))
        assert os.path.isfile(os.path.join(output_path, uid + '.json'))

        shutil.rmtree(output_path)

    def test_exception_recover(self):
        output_path = tempfile.mkdtemp()
        uid = str(uuid.uuid4())

        @profiling(enable=True, output_path=output_path, uid=lambda *args, **kwargs: uid)
        def foo():
            raise RuntimeError()

        with pytest.raises(RuntimeError):
            foo()

        assert os.path.isfile(os.path.join(output_path, uid + '.pstats'))
        assert os.path.isfile(os.path.join(output_path, uid + '.dot'))
        assert os.path.isfile(os.path.join(output_path, uid + '.png'))

        shutil.rmtree(output_path)

    def test_disabled_exception_recover(self):
        output_path = tempfile.mkdtemp()
        uid = str(uuid.uuid4())

        @profiling(enable=False, output_path=output_path, uid=lambda *args, **kwargs: uid)
        def foo():
            raise RuntimeError()

        with pytest.raises(RuntimeError):
            foo()

        assert not os.path.isfile(os.path.join(output_path, uid + '.pstats'))
        assert not os.path.isfile(os.path.join(output_path, uid + '.dot'))
        assert not os.path.isfile(os.path.join(output_path, uid + '.png'))

        shutil.rmtree(output_path)

    def test_invalid_info(self):
        output_path = tempfile.mkdtemp()
        uid = str(uuid.uuid4())

        @profiling(enable=True, output_path=output_path,
                   uid=lambda *args, **kwargs: uid, info=uuid.uuid4())
        def foo():
            return

        foo()

        assert os.path.isfile(os.path.join(output_path, uid + '.pstats'))
        assert os.path.isfile(os.path.join(output_path, uid + '.dot'))
        assert os.path.isfile(os.path.join(output_path, uid + '.png'))

        shutil.rmtree(output_path)

    @mock.patch('marvin_python_toolbox.common.profiling.subprocess')
    def test_subprocess_exception(self, subprocess_mock):
        subprocess_mock.call.side_effect = Exception()

        output_path = tempfile.mkdtemp()
        uid = str(uuid.uuid4())

        @profiling(enable=True, output_path=output_path,
                   uid=lambda *args, **kwargs: uid, info=uuid.uuid4())
        def foo():
            return

        foo()

        assert os.path.isfile(os.path.join(output_path, uid + '.pstats'))
        assert not os.path.isfile(os.path.join(output_path, uid + '.dot'))
        assert not os.path.isfile(os.path.join(output_path, uid + '.png'))

        shutil.rmtree(output_path)

    def test_jupyter_repr_html(self):
        output_path = tempfile.mkdtemp()
        uid = str(uuid.uuid4())

        with profiling(output_path=output_path, uid=lambda *args, **kwargs: uid, info={'test': 42}) as prof:
            def foo():
                return

            foo()
        prof_repr_html = prof._repr_html_()
        assert '<pre>' in prof_repr_html
        assert '<img' in prof_repr_html
        assert os.path.join(output_path, uid + '.png') in prof_repr_html

        shutil.rmtree(output_path)

    @mock.patch('marvin_python_toolbox.common.profiling.subprocess')
    def test_subprocess_exception_jupyter_repr_html(self, subprocess_mock):
        subprocess_mock.call.side_effect = Exception()

        output_path = tempfile.mkdtemp()
        uid = str(uuid.uuid4())

        with profiling(output_path=output_path, uid=uid, info={'test': 42}) as prof:
            def foo():
                return

            foo()
        prof_repr_html = prof._repr_html_()
        assert '<pre>' in prof_repr_html
        assert '<img' not in prof_repr_html
        assert os.path.join(output_path, uid + '.png') not in prof_repr_html

        shutil.rmtree(output_path)