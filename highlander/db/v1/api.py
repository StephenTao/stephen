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

import contextlib

from oslo.db import api as db_api

from highlander.openstack.common import log as logging

_BACKEND_MAPPING = {
    'sqlalchemy': 'highlander.db.v1.sqlalchemy.api',
}

IMPL = db_api.DBAPI('sqlalchemy', backend_mapping=_BACKEND_MAPPING)
LOG = logging.getLogger(__name__)

def setup_db():
    IMPL.setup_db()

def drop_db():
    IMPL.drop_db()

# Transaction control.

def start_tx():
    IMPL.start_tx()

def commit_tx():
    IMPL.commit_tx()

def rollback_tx():
    IMPL.rollback_tx()

def end_tx():
    IMPL.end_tx()

@contextlib.contextmanager
def transaction():
    with IMPL.transaction():
        yield

# Locking.

def acquire_lock(model, id):
    IMPL.acquire_lock(model, id)

#
# Resiliency Group functions
#

def get_resiliency_group(id):
    return IMPL.get_resiliency_group(id)

def get_resiliency_groups():
    return IMPL.get_resiliency_groups()

def create_resiliency_group(values):
    return IMPL.create_resiliency_group(values)

def update_resiliency_group(id, values):
    return IMPL.update_resiliency_group(id, values)

def create_or_update_resiliency_group(id, values):
    return IMPL.create_or_update_resiliency_group(id, values)

def delete_resiliency_group(id):
    IMPL.delete_resiliency_group(id)

def delete_resiliency_groups(**kwargs):
    return IMPL.delete_resiliency_groups(**kwargs)

#
# Resiliency Server functions
#

def get_resiliency_server_group(id):
    return IMPL.get_resiliency_server_group(id)

def get_resiliency_server_groupss(**kwargs):
    return IMPL.get_resiliency_server_groupss(**kwargs)

def create_resiliency_server_group(values, session=None):
    return IMPL.create_resiliency_server_group(values)

def update_resiliency_server_group(id, values, session=None):
    return IMPL.update_resiliency_server_group(id, values)

def create_or_update_resiliency_server_group(id, values):
    return IMPL.create_or_update_resiliency_server_group(id, values)

def delete_resiliency_server_group(id, session=None):
    IMPL.delete_resiliency_server_group(id)

def delete_resiliency_server_groups(**kwargs):
    return IMPL.delete_resiliency_server_groups(**kwargs)

#
# Resiliency Server functions
#

def get_resiliency_server(id):
    return IMPL.get_resiliency_server(id)

def get_resiliency_servers(**kwargs):
    return IMPL.get_resiliency_servers(**kwargs)

def create_resiliency_server(values, session=None):
    return IMPL.create_resiliency_server(values)

def update_resiliency_server(id, values, session=None):
    return IMPL.update_resiliency_server(id, values)

def create_or_update_resiliency_server(id, values):
    return IMPL.create_or_update_resiliency_server(id, values)

def delete_resiliency_server(id, session=None):
    IMPL.delete_resiliency_server(id)

def delete_resiliency_servers(**kwargs):
    return IMPL.delete_resiliency_servers(**kwargs)

#
# UFR Resiliency Server functions
#

def get_ufr_resiliency_server(id):
    return IMPL.get_ufr_resiliency_server(id)

def get_ufr_resiliency_servers(**kwargs):
    return IMPL.get_ufr_resiliency_servers(**kwargs)

def create_ufr_resiliency_server(values, session=None):
    return IMPL.create_ufr_resiliency_server(values)

def update_ufr_resiliency_server(id, values, session=None):
    return IMPL.update_ufr_resiliency_server(id, values)

def create_or_update_ufr_resiliency_server(id, values):
    return IMPL.create_or_update_ufr_resiliency_server(id, values)

def delete_ufr_resiliency_server(id, session=None):
    IMPL.delete_ufr_resiliency_server(id)

def delete_ufr_resiliency_servers(**kwargs):
    return IMPL.delete_ufr_resiliency_servers(**kwargs)

#
# FT Resiliency Server functions
#

def get_ft_resiliency_server(id):
    return IMPL.get_ft_resiliency_server(id)

def get_ft_resiliency_servers(**kwargs):
    return IMPL.get_ft_resiliency_servers(**kwargs)

def create_ft_resiliency_server(values, session=None):
    return IMPL.create_ft_resiliency_server(values)

def update_ft_resiliency_server(id, values, session=None):
    return IMPL.update_ft_resiliency_server(id, values)

def create_or_update_ft_resiliency_server(id, values):
    return IMPL.create_or_update_ft_resiliency_server(id, values)

def delete_ft_resiliency_server(id, session=None):
    IMPL.delete_ft_resiliency_server(id)

def delete_ft_resiliency_servers(**kwargs):
    return IMPL.delete_ft_resiliency_servers(**kwargs)

#
# NM Resiliency Server functions
#

def get_nm_resiliency_server(id):
    return IMPL.get_nm_resiliency_server(id)

def get_nm_resiliency_servers(**kwargs):
    return IMPL.get_nm_resiliency_servers(**kwargs)

def create_nm_resiliency_server(values, session=None):
    return IMPL.create_nm_resiliency_server(values)

def update_nm_resiliency_server(id, values, session=None):
    return IMPL.update_nm_resiliency_server(id, values)

def create_or_update_nm_resiliency_server(id, values):
    return IMPL.create_or_update_nm_resiliency_server(id, values)

def delete_nm_resiliency_server(id, session=None):
    IMPL.delete_nm_resiliency_server(id)

def delete_nm_resiliency_servers(**kwargs):
    return IMPL.delete_nm_resiliency_servers(**kwargs)

#
# NM Resiliency Server Cluster functions
#

def get_nm_resiliency_cluster(id):
    return IMPL.get_nm_resiliency_cluster(id)

def get_nm_resiliency_clusters(**kwargs):
    return IMPL.get_nm_resiliency_clusters(**kwargs)

def create_nm_resiliency_cluster(values, session=None):
    return IMPL.create_nm_resiliency_cluster(values)

def update_nm_resiliency_cluster(id, values, session=None):
    return IMPL.update_nm_resiliency_cluster(id, values)

def create_or_update_nm_resiliency_cluster(id, values):
    return IMPL.create_or_update_nm_resiliency_cluster(id, values)

def delete_nm_resiliency_cluster(id, session=None):
    IMPL.delete_nm_resiliency_cluster(id)

def delete_nm_resiliency_clusters(**kwargs):
    return IMPL.delete_nm_resiliency_clusters(**kwargs)

#
# Resiliency Disk functions
#

def get_resiliency_disk(id):
    return IMPL.get_resiliency_disk(id)

def get_resiliency_disks(**kwargs):
    return IMPL.get_resiliency_disks(**kwargs)

def create_resiliency_disk(values, session=None):
    return IMPL.create_resiliency_disk(values)

def update_resiliency_disk(id, values, session=None):
    return IMPL.update_resiliency_disk(id, values)

def create_or_update_resiliency_disk(id, values):
    return IMPL.create_or_update_resiliency_disk(id, values)

def delete_resiliency_disk(id, session=None):
    IMPL.delete_resiliency_disk(id)

def delete_resiliency_disks(**kwargs):
    return IMPL.delete_resiliency_disks(**kwargs)