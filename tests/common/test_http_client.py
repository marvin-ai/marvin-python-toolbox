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

import json
import pytest
import httpretty
from httpretty import httpretty as httpretty_object

from marvin_python_toolbox.common.http_client import ApiClient, ListResultSet
from marvin_python_toolbox.common.exceptions import HTTPException


class TestHttpClient:

    @httpretty.activate
    def test_list_result_set(self):
        data = [{'id': str(n)} for n in range(100)]
        per_page = 2
        total_pages = len(data) / per_page

        def fake_items(start=0):
            httpretty.register_uri(
                httpretty.GET, "http://localhost:8000/service1/",
                body=json.dumps({
                    'objects': data[start:start + per_page],
                    'total': len(data),
                }),
                content_type="application/json",
                status=200,
            )

        fake_items(0)
        result_set = ListResultSet(path='/service1/', limit=per_page)

        assert len(result_set) == len(data)

        # force iter all
        all_items = list(result_set)
        assert len(all_items) == len(data)

        assert len(httpretty_object.latest_requests) == total_pages

    @httpretty.activate
    def test_get_ok(self):

        httpretty.register_uri(httpretty.GET, "http://localhost:8000/service1/",
                               body='[{"id": "1"}]',
                               content_type="application/json",
                               status=200)

        response = ApiClient().get('/service1/')
        assert response.ok
        assert response.data is not None

    @httpretty.activate
    def test_get_not_ok(self):

        httpretty.register_uri(httpretty.GET, "http://localhost:8000/service1/",
                               body='[{"error": "deu merda"}]',
                               content_type="application/json",
                               status=500)

        response = ApiClient().get('/service1/')
        assert not response.ok

    @httpretty.activate
    def test_get_not_ok_not_json(self):

        httpretty.register_uri(httpretty.GET, "http://localhost:8000/service1/",
                               body='error: "deu merda"',
                               content_type="text/html",
                               status=500)

        response = ApiClient().get('/service1/')
        assert not response.ok

    @httpretty.activate
    def test_get_all_ok(self):

        httpretty.register_uri(httpretty.GET, "http://localhost:8000/service1/",
                               body='{"objects": [{"id": "3"}], "total": 3}',
                               content_type="application/json",
                               status=200)

        httpretty.register_uri(httpretty.GET, "http://localhost:8000/service1/",
                               body='{"objects": [{"id": "1"}, {"id": "2"}], "total": 3}',
                               content_type="application/json",
                               status=200)

        response = ApiClient().get_all('/service1/', limit=2)
        response_list = list(response)
        assert len(response) == 3
        assert len(response_list) == 3
        assert response_list[0]['id'] == '1'
        assert response_list[1]['id'] == '2'
        assert response_list[2]['id'] == '3'

    @httpretty.activate
    def test_get_all_not_ok(self):

        httpretty.register_uri(httpretty.GET, "http://localhost:8000/service1/",
                               body='{"error": "deu merda"}',
                               content_type="application/json",
                               status=500)

        with pytest.raises(HTTPException):
            response = ApiClient().get_all('/service1/', limit=2)

    @httpretty.activate
    def test_get_all_not_ok_second_page(self):

        httpretty.register_uri(httpretty.GET, "http://localhost:8000/service1/",
                               body='{"error": "deu merda"}',
                               content_type="application/json",
                               status=500)

        httpretty.register_uri(httpretty.GET, "http://localhost:8000/service1/",
                               body='{"objects": [{"id": "1"}, {"id": "2"}], "total": 3}',
                               content_type="application/json",
                               status=200)

        response = ApiClient().get_all('/service1/', limit=2)
        assert len(response) == 3

        with pytest.raises(HTTPException):
            response_list = list(response)

    @httpretty.activate
    def test_post_not_ok(self):

        httpretty.register_uri(httpretty.POST, "http://localhost:8000/service1/",
                               body='[{"error": "name required"}]',
                               content_type='text/json',
                               status=500)

        response = ApiClient().post('/service1/', {"name": "americanas", "url": "www.americanas.com.br"})
        assert not response.ok

    @httpretty.activate
    def test_post_ok(self):

        httpretty.register_uri(httpretty.POST, "http://localhost:8000/service1/",
                               body='{"success": true}',
                               content_type='text/json',
                               status=201)

        response = ApiClient().post('/service1/', {"name": "americanas", "url": "www.americanas.com.br"})
        assert response.ok

    @httpretty.activate
    def test_put_not_ok(self):

        httpretty.register_uri(httpretty.PUT, "http://localhost:8000/service1/",
                               body='[{"error": "name required"}]',
                               content_type="application/json",
                               status=500)

        response = ApiClient().put('/service1/', {"id": "1", "url": "www.americanas.com.br"})
        assert not response.ok

    @httpretty.activate
    def test_put_ok(self):

        httpretty.register_uri(httpretty.PUT, "http://localhost:8000/service1/",
                               body='{"success": true}',
                               content_type='text/json',
                               status=200)

        response = ApiClient().put('/service1/', {"id": "1", "name": "americanas", "url": "www.americanas.com.br"})
        assert response.ok

    @httpretty.activate
    def test_delete_not_ok(self):

        httpretty.register_uri(httpretty.DELETE, "http://localhost:8000/service1/",
                               body='[{"error": "name required"}]',
                               content_type="application/json",
                               status=500)

        response = ApiClient().delete('/service1/')
        assert not response.ok

    @httpretty.activate
    def test_delete_ok(self):

        httpretty.register_uri(httpretty.DELETE, "http://localhost:8000/service1/",
                               body='{"success": true}',
                               content_type='text/json',
                               status=200)

        response = ApiClient().delete('/service1/')
        assert response.ok

    @httpretty.activate
    def test_full_url_path(self):

        httpretty.register_uri(httpretty.GET, "http://localhost:9999/service_full/",
                               body='[{"id": "1"}]',
                               content_type="application/json",
                               status=200)

        response = ApiClient().get('http://localhost:9999/service_full/')
        assert response.ok
        assert response.data is not None
