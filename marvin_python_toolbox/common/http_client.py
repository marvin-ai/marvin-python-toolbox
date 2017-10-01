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

"""Http Client Module.

"""
import requests
import math

from .utils import to_json

# Use six to create code compatible with Python 2 and 3.
# See http://pythonhosted.org/six/
from .._compatibility import six
from .._logging import get_logger
from .exceptions import HTTPException


__all__ = ['HttpClient', 'ListResultSet', 'HttpResponse', 'ApiClient']


logger = get_logger('http_client')


class HttpClient(object):
    """
    Http REST client

    used as superclass for the specific API classes
    override the `host` property method to return the api server host

    usage:

        class MyApiClient(object):
            @property
            def host(self):
                return "http://myapiurl:8000"

    """

    def url(self, path):
        """
        Build url for the specified path.

        :param path: [string] the url path for the api endpoint

        :return: [string] formated url
        """

        if 'http://' in path or 'https://' in path:
            return path
        else:
            return self.host + path

    def parse_response(self, response):
        """
        Parse the response and build a `scanboo_common.http_client.HttpResponse` object.
        For successful responses, convert the json data into a dict.

        :param response: the `requests` response

        :return: [HttpResponse] response object
        """
        status = response.status_code
        if response.ok:
            data = response.json()
            return HttpResponse(ok=response.ok, status=status, errors=None, data=data)
        else:
            try:
                errors = response.json()
            except ValueError:
                errors = response.content
            return HttpResponse(ok=response.ok, status=status, errors=errors, data=None)

    def request_header(self):
        """
        Build a headers dict with:
          - the content type as json

        :return: [dict] headers dict
        """
        return {
            'Content-Type': 'application/json',
            'Csrf-Token': 'nocheck',
        }

    def get_all(self, path, data=None, limit=100):
        """Encapsulates GET all requests"""
        return ListResultSet(path=path, data=data or {}, limit=limit)

    def get(self, path, data=None):
        """Encapsulates GET requests"""
        data = data or {}
        response = requests.get(self.url(path), params=data, headers=self.request_header())
        return self.parse_response(response)

    def post(self, path, data=None):
        """Encapsulates POST requests"""
        data = data or {}
        response = requests.post(self.url(path), data=to_json(data), headers=self.request_header())
        return self.parse_response(response)

    def put(self, path, data=None):
        """Encapsulates PUT requests"""
        data = data or {}
        response = requests.put(self.url(path), data=to_json(data), headers=self.request_header())
        return self.parse_response(response)

    def delete(self, path, data=None):
        """Encapsulates DELETE requests"""
        data = data or {}
        response = requests.delete(self.url(path), data=to_json(data), headers=self.request_header())
        return self.parse_response(response)


class ListResultSet(object):
    """
    Used to encapsulate the result of requests of lists.
    """

    def __init__(self, path, data=None, limit=50, page=1):
        self.path = path
        self.params = data or {}
        self.limit = limit
        self.page = page

        self.response = None
        self._objects = []

        self._process()

    def __len__(self):
        return self.response.data.get('total', 0)

    def __iter__(self):
        more_results = True

        while more_results:
            for item in self._objects:
                yield item

            next_page = self._next_page()
            if next_page:
                self.page = next_page
                self._process()
            else:
                more_results = False

    def _next_page(self):
        new_page = None
        if math.ceil(self.response.data['total'] / float(self.limit)) >= (self.page + 1):
            new_page = self.page + 1
        return new_page

    def _process(self):
        url = api_client.url(self.path)
        self.params.update({'page': self.page, 'per_page': self.limit})

        response = requests.get(url, params=self.params, headers=api_client.request_header())
        response = api_client.parse_response(response)

        try:
            self._objects = response.data['objects']
        except TypeError:
            raise HTTPException(response.errors)
        self.response = response


class ApiClient(HttpClient):
    """
    Data Api client abstracttion.
    See `scanboo_common.http_client.HttpClient` for more info.
    """

    @property
    def host(self):
        # url = Configuration.get('api.url')
        url = 'http://localhost:8000'
        return url[:-1] if url.endswith('/') else url


class HttpResponse(object):
    """
    Http response utility class.

    :attr ok: [bool] request returned ok
    :attr status: [int] http status code
    :attr data: [dict] dictionary containing the returned data
    :attr errors: [dict | str] dict when errors is json parsable or the raw error string
    """

    def __init__(self, ok, status, errors, data):
        self.ok = ok
        self.status = status
        self.errors = errors
        self.data = data


# ApiClient "singleton"
api_client = ApiClient()
