# Copyright 2016 - Stratus Technologies
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

import pecan
from pecan import hooks
from pecan import rest
from wsme import types as wtypes

from highlander.api.controllers import resource
from highlander.api.controllers.v1 import validation
from highlander.api.hooks import content_type as ct_hook
import wsmeext.pecan as wsme_pecan

from highlander.openstack.common import log as logging
from highlander.utils import rest_utils
from highlander.services import resiliency_servers

import json
LOG = logging.getLogger(__name__)
RESILIENCY_STRATEGY_TYPES = wtypes.Enum(str, 'ufr', 'ft', 'nm')

class ResiliencyServer(resource.Resource):
    """Resiliency Server resource."""

    id = wtypes.text
    name = wtypes.text
    desc = wtypes.text
    created_at = wtypes.text
    updated_at = wtypes.text
    resiliency_strategy_type = RESILIENCY_STRATEGY_TYPES
    instance_id = wtypes.text

    @classmethod
    def sample(cls):
        return cls(id='123e4567-e89b-12d3-a456-426655440000',
                   name='RG1',
                   desc='THERE CAN BE ONLY ONE.',
                   created_at='1970-01-01T00:00:00.000000',
                   updated_at='1970-01-01T00:00:00.000000',
                   resiliency_strategy_type='ufr',
                   instance_id='123e4567-e89b-12d3-a456-426655440001')


class ResiliencyServers(resource.Resource):
    """A collection of Resiliency Servers."""

    resiliency_servers = [ResiliencyServer]

    @classmethod
    def sample(cls):
        return cls(resiliency_servers=[ResiliencyServer.sample()])


class ResiliencyServersController(rest.RestController, hooks.HookController):
    __hooks__ = [ct_hook.ContentTypeHook("application/json", ['POST', 'PUT'])]

    @rest_utils.wrap_wsme_controller_exception
    @wsme_pecan.wsexpose(ResiliencyServer, wtypes.text)
    def get(self, id):
        """Return the id-referenced resiliency server."""
        LOG.info("Fetch ResiliencyServer [id=%s]" % id)

        db_model = resiliency_servers.get_resiliency_server_v1(id)

        return ResiliencyServer.from_dict(db_model.to_dict())

    @rest_utils.wrap_pecan_controller_exception
    @pecan.expose(content_type="application/json")
    def put(self):
        """Update a resiliency server."""
        data = pecan.request.text
        LOG.info("Update Resiliency Server [data=%s]" % data)
        data = json.loads(data)
        
        rg_db = resiliency_servers.update_resiliency_server_v1(data)
        
        return ResiliencyServer.from_dict(rg_db.to_dict()).to_string()

    @rest_utils.wrap_pecan_controller_exception
    @pecan.expose(content_type="application/json")
    def post(self):
        """Create a new resiliency servers."""
        data = pecan.request.text
        LOG.info("Create resiliency server [data=%s]" % data)
        data = json.loads(data)
        rg_db = resiliency_servers.create_resiliency_server_v1(data)
        pecan.response.status = 201

        return ResiliencyServer.from_dict(rg_db.to_dict()).to_string()

    @rest_utils.wrap_wsme_controller_exception
    @wsme_pecan.wsexpose(None, wtypes.text, status_code=204)
    def delete(self, id):
        """Delete the id-referenced resiliency server."""
        LOG.info("Delete ResiliencyServer [id=%s]" % id)

        resiliency_servers.delete_resiliency_server_v1(id)

    @wsme_pecan.wsexpose(ResiliencyServers)
    def get_all(self):
        """Return all resiliency servers."""
        LOG.info("Fetch resiliency servers.")

        resiliency_server_list = [ResiliencyServers.from_dict(db_model.to_dict())
                          for db_model in resiliency_servers.list_resiliency_servers_v1()]

        return ResiliencyServers(resiliency_servers=resiliency_server_list)
