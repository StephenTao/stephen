# Copyright 2015 - Mirantis, Inc.
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

# TODO(rakhmerov): Add checks for timestamps.

import copy
from highlander.db.v1 import api as api2
from highlander.db.v1.resiliencegroups import api as db_groups_api
from highlander import context as auth_context
from highlander.services import security

from oslo.config import cfg
from highlander import exceptions


from highlander.tests import base as test_base
from highlander.db.v1.resiliencegroups import api as db_groups_api

RESILIENCE_GROUPS = [
    {
        'name': 'group_1',
        'desc': 'group_1 desc',
        'updated_at': None,
        'project_id': '1233',
        'trust_id': '1234'
    },
    {
         'name': 'group_2',
        'desc': 'group_2 desc',
        'updated_at': None,
        'project_id': '1233',
        'trust_id': '1234'
    },
]


class SQLAlchemyTest(test_base.DbTestCase):
    def setUp(self):
        super(SQLAlchemyTest, self).setUp()

        cfg.CONF.set_default('auth_enable', True, group='pecan')
        self.addCleanup(cfg.CONF.set_default, 'auth_enable', False,
                        group='pecan')


class ResiliencGroupTest(SQLAlchemyTest):
    def test_create_and_get_and_load_resiliencygroup(self):

        created =db_groups_api.create_resiliencegroup(RESILIENCE_GROUPS[0])
        fetched = db_groups_api.get_resiliencegroup(created['name'])
        self.assertEqual(created, fetched)
        fetched = db_groups_api.load_resiliencegroup(created.name)
        self.assertEqual(created, fetched)
        self.assertRaises(exceptions.NotFoundException, db_groups_api.get_resiliencegroup,"not-existing-wb")

    def test_resiliencegroup_private(self):
        # Create a Groups(scope=private) as under one project
        # then make sure it's NOT visible for other projects.
        created1 = db_groups_api.create_resiliencegroup(RESILIENCE_GROUPS[1])
        fetched = db_groups_api.get_resiliencegroups()
        self.assertEqual(1, len(fetched))
        self.assertEqual(created1, fetched[0])

        # Create a new user.
        ctx =auth_context.HighlanderContext(
            user_id='9-0-44-5',
            project_id='99-88-33',
            user_name='test-user',
            project_name='test-another',
            is_admin=False
        )
        auth_context.set_ctx(ctx)
        fetched = db_groups_api.get_resiliencegroups()

        self.assertEqual(0, len(fetched))
