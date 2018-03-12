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

from abc import ABCMeta, abstractmethod
import joblib as serializer
from concurrent import futures
import grpc
import json

from .stubs.actions_pb2 import BatchActionResponse, OnlineActionResponse, ReloadResponse, HealthCheckResponse
from .stubs import actions_pb2_grpc

from .._compatibility import six
from .._logging import get_logger


__all__ = ['EngineBaseAction', 'EngineBaseBatchAction', 'EngineBaseOnlineAction']
logger = get_logger('engine_base_action')


class EngineBaseAction():
    __metaclass__ = ABCMeta

    _params = {}
    _persistence_mode = None
    _default_root_path = None
    _previous_step = None
    _is_remote_calling = False
    _local_saved_objects = {}

    def __init__(self, **kwargs):
        self.action_name = self.__class__.__name__
        self._params = self._get_arg(kwargs=kwargs, arg='params')
        self._persistence_mode = self._get_arg(kwargs=kwargs, arg='persistence_mode', default_value='memory')
        self._default_root_path = self._get_arg(kwargs=kwargs, arg='default_root_path', default_value=os.path.join(os.environ['MARVIN_DATA_PATH'], '.artifacts'))
        self._is_remote_calling = self._get_arg(kwargs=kwargs, arg='is_remote_calling', default_value=False)
        logger.debug("Starting {} engine action with {} persistence mode...".format(self.__class__.__name__, self._persistence_mode))

    def _get_arg(self, kwargs, arg, default_value=None):
        return kwargs.get(arg, default_value)

    def _get_object_file_path(self, object_reference):
        engine_name = self.__module__.split('.')[0].replace('marvin_', '').replace('_engine', '')
        directory = os.path.join(self._default_root_path, engine_name)

        if not os.path.exists(directory):
            os.makedirs(directory)

        return os.path.join(directory, "{}".format(object_reference.replace('_', '')))

    def _serializer_dump(self, obj, object_file_path):
        serializer.dump(obj, object_file_path, protocol=2, compress=3)

    def _serializer_load(self, object_file_path):
        return serializer.load(object_file_path)

    def _save_obj(self, object_reference, obj):
        if not self._is_remote_calling:
            if getattr(self, object_reference, None) is not None:
                logger.error("Object {} must be assign only once in each action".format(object_reference))
                raise Exception('MultipleAssignException', object_reference)

        setattr(self, object_reference, obj)

        if self._persistence_mode == 'local':
            object_file_path = self._get_object_file_path(object_reference)
            logger.info("Saving object to {}".format(object_file_path))
            self._serializer_dump(obj, object_file_path)
            logger.info("Object {} saved!".format(object_reference))
            self._local_saved_objects[object_reference] = object_file_path

    def _load_obj(self, object_reference):
        if getattr(self, object_reference, None) is None and self._persistence_mode == 'local':
            object_file_path = self._get_object_file_path(object_reference)
            logger.info("Loading object from {}".format(object_file_path))
            setattr(self, object_reference, self._serializer_load(object_file_path))
            logger.info("Object {} loaded!".format(object_reference))

        return getattr(self, object_reference)

    def _release_local_saved_objects(self):
        for object_reference in self._local_saved_objects.keys():
            logger.info("Removing object {} from memory..".format(object_reference))
            setattr(self, object_reference, None)

        self._local_saved_objects = {}

    @classmethod
    def retrieve_obj(self, object_file_path):
        logger.info("Retrieve object from {}".format(object_file_path))
        return serializer.load(object_file_path)

    def _remote_reload(self, request, context):
        protocol = request.protocol
        artifacts = request.artifacts

        logger.info("Received message from client with protocol [{}] to reload the [{}] artifacts...".format(protocol, artifacts))

        message = "Reloaded"

        if artifacts:
            for artifact in artifacts.split(","):
                self._load_obj(object_reference=artifact)

        else:
            message = "Nothing to reload"

        response_message = ReloadResponse(message=message)

        logger.info("Return final results to the client!")
        return response_message

    def _health_check(self, request, context):
        logger.info("Received message from client with protocol health check [{}] artifacts...".format(request.artifacts))
        try:
            if request.artifacts:
                for artifact in request.artifacts.split(","):
                    if not getattr(self, artifact):
                        return HealthCheckResponse(status=HealthCheckResponse.NOK)
            return HealthCheckResponse(status=HealthCheckResponse.OK)

        except Exception as e:
            logger.error(e)
            return HealthCheckResponse(status=HealthCheckResponse.NOK)


class EngineBaseBatchAction(EngineBaseAction):
    __metaclass__ = ABCMeta

    @abstractmethod
    def execute(self, params, **kwargs):
        pass

    def _pipeline_execute(self, params):
        if self._previous_step:
            self._previous_step._pipeline_execute(params)

        logger.info("Start of the {} execute method!".format(self.action_name))
        self.execute(params)
        logger.info("Finish of the {} execute method!".format(self.action_name))

    def _remote_execute(self, request, context):
        logger.info("Received message from client and sending to engine action...")
        logger.debug("Received Params: {}".format(request.params))

        params = json.loads(request.params) if request.params else self._params

        self._pipeline_execute(params=params)

        self._release_local_saved_objects()

        logger.info("Handling returned message from engine action...")
        response_message = BatchActionResponse(message="Done")

        logger.info("Return final results to the client!")
        return response_message

    def _prepare_remote_server(self, port, workers, rpc_workers):
        server = grpc.server(thread_pool=futures.ThreadPoolExecutor(max_workers=workers), maximum_concurrent_rpcs=rpc_workers)
        actions_pb2_grpc.add_BatchActionHandlerServicer_to_server(self, server)
        server.add_insecure_port('[::]:{}'.format(port))
        return server


class EngineBaseOnlineAction(EngineBaseAction):
    __metaclass__ = ABCMeta

    @abstractmethod
    def execute(self, input_message, params, **kwargs):
        pass

    def _pipeline_execute(self, input_message, params):
        if self._previous_step:
            input_message = self._previous_step._pipeline_execute(input_message, params)

        logger.info("Start of the {} execute method!".format(self.action_name))
        return self.execute(input_message, params)
        logger.info("Finish of the {} execute method!".format(self.action_name))

    def _remote_execute(self, request, context):
        logger.info("Received message from client and sending to engine action...")
        logger.debug("Received Params: {}".format(request.params))
        logger.debug("Received Message: {}".format(request.message))

        input_message = json.loads(request.message) if request.message else None
        params = json.loads(request.params) if request.params else self._params

        _message = self._pipeline_execute(input_message=input_message, params=params)

        logger.info("Handling returned message from engine action...")

        if type(_message) != str:
            _message = json.dumps(_message)

        response_message = OnlineActionResponse(message=_message)

        logger.info("Return final results to the client!")
        return response_message

    def _prepare_remote_server(self, port, workers, rpc_workers):
        server = grpc.server(thread_pool=futures.ThreadPoolExecutor(max_workers=workers), maximum_concurrent_rpcs=rpc_workers)
        actions_pb2_grpc.add_OnlineActionHandlerServicer_to_server(self, server)
        server.add_insecure_port('[::]:{}'.format(port))
        return server
