# Copyright 2014 - Stratus, Inc.
# Copyright 2014 - Mirantis, Inc.
# Copyright 2015 - StackStorm, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from oslo.config import cfg
from oslo import messaging
from oslo.messaging.rpc import client

from highlander import context as auth_ctx
from highlander.engine import base
from highlander import exceptions as exc
from highlander.openstack.common import log as logging


LOG = logging.getLogger(__name__)


_TRANSPORT = None

_ENGINE_CLIENT = None
_EXECUTOR_CLIENT = None


def cleanup():
    """Intended to be used by tests to recreate all RPC related objects."""

    global _TRANSPORT
    global _ENGINE_CLIENT
    global _EXECUTOR_CLIENT

    _TRANSPORT = None
    _ENGINE_CLIENT = None
    _EXECUTOR_CLIENT = None


def get_transport():
    global _TRANSPORT

    if not _TRANSPORT:
        _TRANSPORT = messaging.get_transport(cfg.CONF)

    return _TRANSPORT






def wrap_messaging_exception(method):
    """This decorator unwrap remote error in one of HighlanderException.

    oslo.messaging has different behavior on raising exceptions
    when fake or rabbit transports are used. In case of rabbit
    transport it raises wrapped RemoteError which forwards directly
    to API. Wrapped RemoteError contains one of HighlanderException raised
    remotely on Engine and for correct exception interpretation we
    need to unwrap and raise given exception and manually send it to
    API layer.
    """
    def decorator(*args, **kwargs):
        try:
            return method(*args, **kwargs)

        except client.RemoteError as e:
            exc_cls = getattr(exc, e.exc_type)
            raise exc_cls(e.value)

    return decorator




