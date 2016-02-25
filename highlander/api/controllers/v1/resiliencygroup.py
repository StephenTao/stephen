# Copyright 2015 - Stratus Technologies
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

import json

import pecan
import wsmeext.pecan as wsme_pecan
from pecan import hooks
from pecan import rest
from wsme import types as wtypes

from highlander.api.controllers import resource
from highlander.api.hooks import content_type as ct_hook
from highlander.openstack.common import log as logging
from highlander.services import resiliency_groups
from highlander.utils import rest_utils

LOG = logging.getLogger(__name__)
RESILIENCY_STRATEGY_TYPES = wtypes.Enum(str, 'ufr', 'ft', 'nm')


class ResiliencyGroup(resource.Resource):
    """Resiliency Group resource."""

    id = wtypes.text
    name = wtypes.text
    desc = wtypes.text
    created_at = wtypes.text
    updated_at = wtypes.text
    resiliency_strategy_type = RESILIENCY_STRATEGY_TYPES

    @classmethod
    def sample(cls):
        return cls(id='123e4567-e89b-12d3-a456-426655440000',
                   name='RG1',
                   desc='THERE CAN BE ONLY ONE.',
                   created_at='1970-01-01T00:00:00.000000',
                   updated_at='1970-01-01T00:00:00.000000',
                   resiliency_strategy_type='ufr')


class ResiliencyGroups(resource.Resource):
    """A collection of Resiliency Groups."""

    resiliency_groups = [ResiliencyGroup]

    @classmethod
    def sample(cls):
        return cls(resiliency_groups=[ResiliencyGroup.sample()])


class ResiliencyGroupsController(rest.RestController, hooks.HookController):
    __hooks__ = [ct_hook.ContentTypeHook("application/json", ['POST', 'PUT'])]

    @rest_utils.wrap_wsme_controller_exception
    @wsme_pecan.wsexpose(ResiliencyGroup, wtypes.text)
    def get(self, id):
        """Return the id-referenced resiliency group."""
        LOG.info("Fetch ResiliencyGroup [id=%s]" % id)

        db_model = resiliency_groups.get_resiliency_group_v1(id)

        return ResiliencyGroup.from_dict(db_model.to_dict())

    @rest_utils.wrap_pecan_controller_exception
    @pecan.expose(content_type="text/plain")
    def put(self):
        """Update a resiliency group."""
        data = pecan.request.text
        LOG.info("Update Resiliency Group [data=%s]" % data)

        rg_db = resiliency_groups.update_resiliency_group_v1(data)

        return ResiliencyGroup.from_dict(rg_db.to_dict()).to_string()

    @rest_utils.wrap_pecan_controller_exception
    @pecan.expose(content_type="application/json")
    def post(self):
        """Create a new resiliency groups."""
        data = pecan.request.text
        LOG.info("Create resiliency group [data=%s]" % data)
        data = json.loads(data)

        rg_db = resiliency_groups.create_resiliency_group_v1(data)
        pecan.response.status = 201

        return ResiliencyGroup.from_dict(rg_db.to_dict()).to_string()

    @rest_utils.wrap_wsme_controller_exception
    @wsme_pecan.wsexpose(None, wtypes.text, status_code=204)
    def delete(self, id):
        """Delete the id-referenced resiliency group."""
        LOG.info("Delete ResiliencyGroup [id=%s]" % id)

        resiliency_groups.delete_resiliency_group_v1(id)

    @wsme_pecan.wsexpose(ResiliencyGroups)
    def get_all(self):
        """Return all resiliency groups."""
        LOG.info("Fetch resiliency groups.")

        resiliency_group_list = [ResiliencyGroups.from_dict(db_model.to_dict())
                                 for db_model in resiliency_groups.list_resiliency_groups_v1()]

        return ResiliencyGroups(resiliency_groups=resiliency_group_list)
