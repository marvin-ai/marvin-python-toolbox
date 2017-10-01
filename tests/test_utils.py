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

import uuid
import datetime
import json

import pytest

try:
    import mock
except ImportError:
    import unittest.mock as mock

from marvin_python_toolbox.common.utils import (class_property, memoized_class_property, get_datetime, deprecated,
                                        to_json, from_json, is_valid_json, validate_json, generate_key, to_slug,
                                        get_local_ip_address, url_encode, getattr_qualified, chunks, check_path)
from marvin_python_toolbox.common.exceptions import InvalidJsonException

instance_count = 0


# ==============================================================================
# Test memoized_class_property

class Dummy:
    @memoized_class_property
    def my_cls_attribute(cls):
        global instance_count
        instance_count += 1
        return 42

    @class_property
    def my_cls_property(cls):
        return 'oi'

    def any_method(self):
        return self.my_cls_attribute


def test_initial_instance_count():
    global instance_count
    assert 0 == instance_count


def test_property():
    assert 42 == Dummy.my_cls_attribute


def test_access_from_instance_method():
    assert 42 == Dummy().any_method()


def test_create_only_one_instance():
    global instance_count

    Dummy.my_cls_attribute
    assert 1 == instance_count

    Dummy.my_cls_attribute
    assert 1 == instance_count


def test_class_property():
    assert Dummy.my_cls_property == 'oi'


# ==============================================================================
# test to_json & from_json

def test_to_json():
    d = {'i': 42, 's': 'string', 'dt': datetime.datetime.now(), 'id': uuid.uuid4()}
    assert isinstance(to_json(d), basestring)


def test_to_json_with_obj_with_id():
    class Obj(object):
        id = '42'

    d = {'i': Obj()}
    assert isinstance(to_json(d), basestring)


def test_to_json_with_obj_without_id():
    class Obj(object):
        pass

    d = {'i': Obj()}
    with pytest.raises(TypeError):
        to_json(d)


def test_to_json_with_numpy():
    class FakeNumpyFloat(object):
        def item(self):
            return 0.666

    d = {'float': FakeNumpyFloat()}
    assert to_json(d) == '{"float": 0.666}'


def test_from_json():
    d = {'i': 42, 's': 'string', 'dt': datetime.datetime.now(), 'id': uuid.uuid4()}
    assert isinstance(from_json(to_json(d)), dict)


def test_validate_json():
    valid = {
        'prop': ['a', 'b' , 'c']
    }
    invalid = {
        'prop': 'a'
    }
    schema = {
        'type': 'object',
        'properties': {
            'prop': {
                'type': 'array',
                'items': { 'type': 'string' }
            }
        }
    }
    validate_json(valid, schema=schema)

    with pytest.raises(InvalidJsonException):
        validate_json(invalid, schema=schema)


def test_is_valid_json():
    valid = {
        'prop': ['a', 'b' , 'c']
    }
    invalid = {
        'prop': 'a'
    }
    schema = {
        'type': 'object',
        'properties': {
            'prop': {
                'type': 'array',
                'items': { 'type': 'string' }
            }
        }
    }
    assert is_valid_json(valid, schema=schema) is True
    assert is_valid_json(invalid, schema=schema) is False

    assert is_valid_json(json.dumps(valid), schema=json.dumps(schema)) is True
    assert is_valid_json(json.dumps(invalid), schema=json.dumps(schema)) is False


def test_generate_key():
    value = 'www.image.com.br'
    valid_sha256 = '58643ebba1abbbd92c586957a98c9f3e8a104b681eb37b99df50b2e1044bbf20'
    assert generate_key(value) == valid_sha256


def test_generate_key_with_unicode():
    value = u'http://static.wmobjects.com.br/imgres/arquivos/ids/2509201-344-344/torradeira-cuisinart-tan-4-\u2013-branca.jpg'
    assert generate_key(value)


def test_to_slug():
    assert to_slug('any text') == "any-text"


def test_chunk():
    assert len(list(chunks([1, 2, 3, 4], 2))) == 2


def test_getattr_qualified():
    class B(object):
        c = {'d': 'e'}

    class A(object):
        b = B()

    a = A()

    assert getattr_qualified(a, 'b') == a.b
    assert getattr_qualified(a, 'b.c') == a.b.c
    assert getattr_qualified(a, 'b.c["d"]') == a.b.c['d']
    assert getattr_qualified(a, "b.c['d']") == a.b.c['d']
    assert getattr_qualified(a, "b.c[d]") == a.b.c['d']
    assert getattr_qualified(a, "b.c[f]", 'default') == 'default'
    assert getattr_qualified(a, "x.c[f]", 'default') == 'default'

    with pytest.raises(AttributeError):
        getattr_qualified(a, 'x.c[f]')

    with pytest.raises(KeyError):
        getattr_qualified(a, 'b.c["z"]')

    with pytest.raises(TypeError):
        getattr_qualified(a, 'b', 'default', 'bla')


@mock.patch('marvin_python_toolbox.common.utils.os.path.exists')
def test_path_not_exists(path_exists_mock):
    path_exists_mock.return_value = False
    assert not check_path('temp')


@mock.patch('marvin_python_toolbox.common.utils.os.makedirs')
@mock.patch('marvin_python_toolbox.common.utils.os.path.exists')
def test_path_creation(path_exists_mock, makedirs_mock):
    path_exists_mock.side_effect = [False, True]
    makedirs_mock.return_value = None
    assert check_path('temp', create=True)


def test_get_datetime():
    date = get_datetime()
    date = date.split()

    assert len(date[0]) == 10
    assert len(date[1]) == 8
    assert date[2] == 'UTC'


def test_deprecated():
    @deprecated
    def deprecated_func():
        pass

    with pytest.warns(DeprecationWarning):
        deprecated_func()


def test_url_encode():
    original = u'http://host.com/path_with_special_char_áéíóú?and=query&string=true'
    transformed = 'http://host.com/path_with_special_char_%C3%A1%C3%A9%C3%AD%C3%B3%C3%BA?and=query&string=true'
    assert url_encode(original) == transformed


def test_url_encode_string():
    original = 'http://host.com/path_with_special_char_\xc3\xa1\xc3\xa9\xc3\xad\xc3\xb3\xc3\xba?and=query&string=true'
    transformed = 'http://host.com/path_with_special_char_%C3%A1%C3%A9%C3%AD%C3%B3%C3%BA?and=query&string=true'
    assert url_encode(original) == transformed


def test_get_local_ip_address():
    ip = get_local_ip_address()
    assert isinstance(ip, basestring)
    assert len(ip.split('.')) == 4
