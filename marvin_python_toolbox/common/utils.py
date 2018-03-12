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

"""Utils Module.

"""
import os
import re
import datetime
import time
import json
import simplejson
import uuid
import hashlib
import jsonschema
import warnings
from slugify import slugify

# Use six to create code compatible with Python 2 and 3.
# See http://pythonhosted.org/six/
from .._compatibility import xrange, text_type, quote
from .._logging import get_logger
from .exceptions import InvalidJsonException


logger = get_logger('utils')


class memoized_class_property(object):
    """Creates a singleton class property

    Usage:

        class MyClass:
            @memoized_class_property
            def bla(cls):
                print 'only once'
                return 42

        MyClass.bla
        # 'only once'
        # 42

        MyClass.bla
        # 42
    """

    def __init__(self, wrapped):
        self.wrapped = wrapped
        try:
            self.__doc__ = wrapped.__doc__
        except:  # pragma: no cover
            pass

    # if called on a class, inst is None and objtype is the class
    # if called on an instance, inst is the instance, and objtype
    # the class
    def __get__(self, inst, objtype=None):
        val = self.wrapped(objtype)
        setattr(objtype, self.wrapped.__name__, val)
        return val


class class_property(object):
    """Creates a class property

    Usage:

        class MyClass:
            @classproperty
            def bla(cls):
                print 'hi'
                return 42

        MyClass.bla
        # 'hi'
        # 42

        MyClass.bla
        # 'hi'
        # 42
    """

    def __init__(self, wrapped):
        self.wrapped = wrapped
        try:
            self.__doc__ = wrapped.__doc__
        except:  # pragma: no cover
            pass

    def __get__(self, inst, objtype=None):
        val = self.wrapped(objtype)
        return val


def chunks(lst, size):
    """Yield successive n-sized chunks from lst."""
    for i in xrange(0, len(lst), size):
        yield lst[i:i + size]


def _to_json_default(obj):
    """Helper to convert non default objects to json.

    Usage:
        simplejson.dumps(data, default=_to_json_default)
    """
    # Datetime
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()

    # UUID
    if isinstance(obj, uuid.UUID):
        return str(obj)

    # numpy
    if hasattr(obj, 'item'):
        return obj.item()

    # # Enum
    # if hasattr(obj, 'value'):
    #     return obj.value

    try:
        return obj.id
    except Exception:
        raise TypeError('{obj} is not JSON serializable'.format(obj=repr(obj)))


datetime_regex = re.compile('(\d{4})-(\d{2})-(\d{2})T(\d{2}):(\d{2}):(\d{2})')
uuid_regex = re.compile('^[0-9a-f]{8}(-[0-9a-f]{4}){3}-[0-9a-f]{12}$')


def _from_json_object_hook(obj):
    """Converts a json string, where datetime and UUID objects were converted
    into strings using the '_to_json_default', into a python object.

    Usage:
        simplejson.loads(data, object_hook=_from_json_object_hook)
    """

    for key, value in obj.items():
        # Check for datetime objects
        if isinstance(value, str):
            dt_result = datetime_regex.match(value)
            if dt_result:
                year, month, day, hour, minute, second = map(
                    lambda x: int(x), dt_result.groups())
                obj[key] = datetime.datetime(
                    year, month, day, hour, minute, second)
            else:
                dt_result = uuid_regex.match(value)
                if dt_result:
                    obj[key] = uuid.UUID(value)
    return obj


def to_json(data):
    """Convert non default objects to json."""
    return json.dumps(data, default=_to_json_default)


def from_json(json_str):
    return simplejson.loads(json_str, object_hook=_from_json_object_hook)


def validate_json(data, schema):
    if isinstance(data, str):
        data = from_json(data)
    if isinstance(schema, str):
        schema = from_json(schema)

    try:
        jsonschema.validate(data, schema)
    except jsonschema.ValidationError as e:
        raise InvalidJsonException(e.message)


def is_valid_json(data, schema):
    ret = True
    try:
        validate_json(data, schema)
    except InvalidJsonException:
        ret = False
    return ret


def generate_key(string):
    return hashlib.sha256(string.encode('utf-8')).hexdigest()


def to_slug(strvalue):
    """Wrapper to convert any string on slug"""
    return slugify(strvalue)


def getattr_qualified(obj, name, *args):
    if len(args) > 1:
        raise TypeError(
            'getattr_qualified expected at most 3 arguments, got {}'.format(len(args) + 2))
    has_default = False
    if args:
        default = args[0]
        has_default = True
    # get attribute names
    for attr in name.split("."):
        key = None
        # check if is a dict
        if '[' in attr:
            # get the attr name and key
            attr, key = attr[:-1].split('[')
            # remove quotes
            if key[0] in ('"', "'") and key[0] == key[-1]:
                key = key[1:-1]
        try:
            obj = getattr(obj, attr)
        except AttributeError:
            if not has_default:
                raise
            return default
        if key:
            try:
                obj = obj[key]
            except KeyError:
                if not has_default:
                    raise
                return default
    return obj


def check_path(path, create=False):
    """
    Check for a path on filesystem

    :param path: str - path name
    :param create: bool - create if do not exist
    :return: bool - path exists
    """
    if not os.path.exists(path):
        if create:
            os.makedirs(path)
            return os.path.exists(path)
        else:
            return False

    return True


def get_datetime():
    """
    Get the current date and time in UTC

    :return: string
    """
    return datetime.datetime.fromtimestamp(time.time()).strftime('%Y-%m-%d %H:%M:%S') + ' UTC'


def deprecated(func):
    def new_func(*args, **kwargs):
        warnings.simplefilter('always', DeprecationWarning)  # turn off filter
        warnings.warn("Call to deprecated function {}.".format(
            func.__name__), category=DeprecationWarning, stacklevel=2)
        warnings.simplefilter('default', DeprecationWarning)  # reset filter
        return func(*args, **kwargs)

    new_func.__name__ = func.__name__
    new_func.__doc__ = func.__doc__
    new_func.__dict__.update(func.__dict__)
    return new_func


def url_encode(url):
    """
    Convert special characters using %xx escape.

    :param url: str
    :return: str - encoded url
    """
    if isinstance(url, text_type):
        url = url.encode('utf8')
    return quote(url, ':/%?&=')
