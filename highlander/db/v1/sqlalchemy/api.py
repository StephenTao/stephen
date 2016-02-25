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
import sys

import sqlalchemy as sa
from oslo.config import cfg
from oslo.db import exception as db_exc
from oslo.utils import timeutils

from highlander import exceptions as exc
from highlander.db.sqlalchemy import base as b
from highlander.db.sqlalchemy import model_base as mb
from highlander.db.sqlalchemy import sqlite_lock
from highlander.db.v1.sqlalchemy import models
from highlander.openstack.common import log as logging
from highlander.services import security

CONF = cfg.CONF
LOG = logging.getLogger(__name__)


def get_backend():
    """Consumed by openstack common code.

    The backend is this module itself.
    :return Name of db backend.
    """
    return sys.modules[__name__]


def setup_db():
    try:

        models.ResiliencyGroup.metadata.create_all(b.get_engine())
    except sa.exc.OperationalError as e:
        raise exc.DBException("Failed to setup database: %s" % e)


def drop_db():
    global _facade

    try:
        models.ResiliencyGroup.metadata.drop_all(b.get_engine())
        _facade = None
    except Exception as e:
        raise exc.DBException("Failed to drop database: %s" % e)


# Transaction management.

def start_tx():
    b.start_tx()


def commit_tx():
    b.commit_tx()


def rollback_tx():
    b.rollback_tx()


def end_tx():
    b.end_tx()


@contextlib.contextmanager
def transaction():
    try:
        start_tx()
        yield
        commit_tx()
    finally:
        end_tx()


@b.session_aware()
def acquire_lock(model, id, session=None):
    if b.get_driver_name() != 'sqlite':
        query = _secure_query(model).filter("id = '%s'" % id)

        query.update(
            {'updated_at': timeutils.utcnow()},
            synchronize_session=False
        )
    else:
        sqlite_lock.acquire_lock(id, session)


def _secure_query(model):
    query = b.model_query(model)

    if issubclass(model, mb.HighlanderSecureModelBase):
        query = query.filter(
            sa.or_(
                model.project_id == security.get_project_id(),
                model.scope == 'public'
            )
        )

    return query


def _delete_all(model, session=None, **kwargs):
    _secure_query(model).filter_by(**kwargs).delete()


def _get_collection_sorted_by_name(model, **kwargs):
    return _secure_query(model).filter_by(**kwargs).order_by(model.name).all()


def _get_collection_sorted_by_time(model, **kwargs):
    query = _secure_query(model)

    return query.filter_by(**kwargs).order_by(model.created_at).all()


def _get_db_object_by_name(model, name):
    return _secure_query(model).filter_by(name=name).first()


def _get_db_object_by_id(model, id):
    return _secure_query(model).filter_by(id=id).first()


#
# Resiliency Group functions
#

def get_resiliency_group(id):
    rg = _get_resiliency_group(id)

    if not rg:
        raise exc.NotFoundException(
            "Resiliency Group not found [id=%s]" % id)

    return rg


def get_resiliency_groups(**kwargs):
    return _get_collection_sorted_by_name(models.ResiliencyGroup, **kwargs)


@b.session_aware()
def create_resiliency_group(values, session=None):
    rg = models.ResiliencyGroup()

    rg.update(values)

    try:
        rg.save(session=session)
    except db_exc.DBDuplicateEntry as e:
        raise exc.DBDuplicateEntry(
            "Duplicate entry for ResiliencyGroup: %s" % e.columns
        )

    return rg


@b.session_aware()
def update_resiliency_group(id, values, session=None):
    rg = _get_resiliency_group(id)

    if not rg:
        raise exc.NotFoundException(
            "Resiliency Group not found [id=%s]" % id)

    rg.update(values.copy())

    return rg


@b.session_aware()
def create_or_update_resiliency_group(id, values, session=None):
    if not _get_resiliency_group(id):
        return create_resiliency_group(values)
    else:
        return update_resiliency_group(id, values)


@b.session_aware()
def delete_resiliency_group(id, session=None):
    rg = _get_resiliency_group(id)

    if not rg:
        raise exc.NotFoundException(
            "Resiliency Group not found [id=%s]" % id)

    session.delete(rg)


def _get_resiliency_group(id):
    return _get_db_object_by_id(models.ResiliencyGroup, id)


@b.session_aware()
def delete_resiliency_groups(**kwargs):
    return _delete_all(models.ResiliencyGroup, **kwargs)


#
# Resiliency Server Group functions
#

def get_resiliency_server_group(id):
    rg = _get_resiliency_server_group(id)

    if not rg:
        raise exc.NotFoundException(
            "Resiliency ServerGroup not found [id=%s]" % id)

    return rg


def get_resiliency_server_groups(**kwargs):
    return _get_collection_sorted_by_name(models.ResiliencyServerGroup, **kwargs)


@b.session_aware()
def create_resiliency_server_group(values, session=None):
    rg = models.ResiliencyServerGroup()

    rg.update(values)

    try:
        rg.save(session=session)
    except db_exc.DBDuplicateEntry as e:
        raise exc.DBDuplicateEntry(
            "Duplicate entry for ResiliencyServerGroup: %s" % e.columns
        )

    return rg


@b.session_aware()
def update_resiliency_server_group(id, values, session=None):
    rg = _get_resiliency_server_group(id)

    if not rg:
        raise exc.NotFoundException(
            "Resiliency ServerGroup not found [id=%s]" % id)

    rg.update(values.copy())

    return rg


@b.session_aware()
def create_or_update_resiliency_server_group(id, values, session=None):
    if not _get_resiliency_server_group(id):
        return create_resiliency_server_group(values)
    else:
        return update_resiliency_server_group(id, values)


@b.session_aware()
def delete_resiliency_server_group(id, session=None):
    rg = _get_resiliency_server_group(id)

    if not rg:
        raise exc.NotFoundException(
            "Resiliency ServerGroup not found [id=%s]" % id)

    session.delete(rg)


def _get_resiliency_server_group(id):
    return _get_db_object_by_id(models.ResiliencyServerGroup, id)


@b.session_aware()
def delete_resiliency_server_groups(**kwargs):
    return _delete_all(models.ResiliencyServerGroup, **kwargs)


#
# Generic Resiliency Server functions
#

def get_resiliency_server(id):
    rs = _get_resiliency_server(id)

    if not rs:
        raise exc.NotFoundException(
            "Resiliency Server not found [id=%s]" % id)

    return rs


def get_resiliency_servers(**kwargs):
    return _get_collection_sorted_by_name(models.ResiliencyServer, **kwargs)


@b.session_aware()
def create_resiliency_server(values, session=None):
    rs = models.ResiliencyServer()
    print "here"
    LOG.info(values)

    rs.update(values)

    try:
        rs.save(session=session)
    except db_exc.DBDuplicateEntry as e:
        raise exc.DBDuplicateEntry(
            "Duplicate entry for ResiliencyServer: %s" % e.columns
        )

    return rs


@b.session_aware()
def update_resiliency_server(id, values, session=None):
    rs = _get_resiliency_server(id)

    if not rs:
        raise exc.NotFoundException(
            "Resiliency Server not found [id=%s]" % id)

    rs.update(values.copy())

    return rs


@b.session_aware()
def create_or_update_resiliency_server(id, values, session=None):
    if not _get_resiliency_server(id):
        return create_resiliency_server(values)
    else:
        return update_resiliency_server(id, values)


@b.session_aware()
def delete_resiliency_server(id, session=None):
    rs = _get_resiliency_server(id)

    if not rs:
        raise exc.NotFoundException(
            "Resiliency Server not found [id=%s]" % id)

    session.delete(rs)


def _get_resiliency_server(id):
    return _get_db_object_by_id(models.ResiliencyServer, id)


@b.session_aware()
def delete_resiliency_servers(**kwargs):
    return _delete_all(models.ResiliencyServer, **kwargs)


#
# Resiliency Disk Logical functions
#

def get_resiliency_disk_logical(id):
    rs = _get_resiliency_disk_logical(id)

    if not rs:
        raise exc.NotFoundException(
            "Resiliency DiskLogical not found [id=%s]" % id)

    return rs


def get_resiliency_disk_logicals(**kwargs):
    return _get_collection_sorted_by_name(models.ResiliencyDiskLogical, **kwargs)


@b.session_aware()
def create_resiliency_disk_logical(values, session=None):
    rs = models.ResiliencyDiskLogical()

    rs.update(values.copy())

    try:
        rs.save(session=session)
    except db_exc.DBDuplicateEntry as e:
        raise exc.DBDuplicateEntry(
            "Duplicate entry for ResiliencyDiskLogical: %s" % e.columns
        )

    return rs


@b.session_aware()
def update_resiliency_disk_logical(id, values, session=None):
    rs = _get_resiliency_disk_logical(id)

    if not rs:
        raise exc.NotFoundException(
            "Resiliency DiskLogical not found [id=%s]" % id)

    rs.update(values.copy())

    return rs


@b.session_aware()
def create_or_update_resiliency_disk_logical(id, values, session=None):
    if not _get_resiliency_disk_logical(id):
        return create_resiliency_disk_logical(values)
    else:
        return update_resiliency_disk_logical(id, values)


@b.session_aware()
def delete_resiliency_disk_logical(id, session=None):
    rs = _get_resiliency_disk_logical(id)

    if not rs:
        raise exc.NotFoundException(
            "Resiliency DiskLogical not found [id=%s]" % id)

    session.delete(rs)


def _get_resiliency_disk_logical(id):
    return _get_db_object_by_id(models.ResiliencyDiskLogical, id)


@b.session_aware()
def delete_resiliency_disk_logicals(**kwargs):
    return _delete_all(models.ResiliencyDiskLogical, **kwargs)


#
# Resiliency Disk functions
#

def get_resiliency_disk(id):
    rs = _get_resiliency_disk(id)

    if not rs:
        raise exc.NotFoundException(
            "Resiliency Disk not found [id=%s]" % id)

    return rs


def get_resiliency_disks(**kwargs):
    return _get_collection_sorted_by_name(models.ResiliencyDisk, **kwargs)


@b.session_aware()
def create_resiliency_disk(values, session=None):
    rs = models.ResiliencyDisk()

    rs.update(values.copy())

    try:
        rs.save(session=session)
    except db_exc.DBDuplicateEntry as e:
        raise exc.DBDuplicateEntry(
            "Duplicate entry for ResiliencyDisk: %s" % e.columns
        )

    return rs


@b.session_aware()
def update_resiliency_disk(id, values, session=None):
    rs = _get_resiliency_disk(id)

    if not rs:
        raise exc.NotFoundException(
            "Resiliency Disk not found [id=%s]" % id)

    rs.update(values.copy())

    return rs


@b.session_aware()
def create_or_update_resiliency_disk(id, values, session=None):
    if not _get_resiliency_disk(id):
        return create_resiliency_disk(values)
    else:
        return update_resiliency_disk(id, values)


@b.session_aware()
def delete_resiliency_disk(id, session=None):
    rs = _get_resiliency_disk(id)

    if not rs:
        raise exc.NotFoundException(
            "Resiliency Disk not found [id=%s]" % id)

    session.delete(rs)


def _get_resiliency_disk(id):
    return _get_db_object_by_id(models.ResiliencyDisk, id)


@b.session_aware()
def delete_resiliency_disks(**kwargs):
    return _delete_all(models.ResiliencyDisk, **kwargs)


#
# Resiliency NicLogical functions
#

def get_resiliency_nic_logical(id):
    rs = _get_resiliency_nic_logical(id)

    if not rs:
        raise exc.NotFoundException(
            "Resiliency Nic Logical not found [id=%s]" % id)

    return rs


def get_resiliency_nic_logicals(**kwargs):
    return _get_collection_sorted_by_name(models.ResiliencyNicLogical, **kwargs)


@b.session_aware()
def create_resiliency_nic_logical(values, session=None):
    rs = models.ResiliencyNicLogical()

    rs.update(values.copy())

    try:
        rs.save(session=session)
    except db_exc.DBDuplicateEntry as e:
        raise exc.DBDuplicateEntry(
            "Duplicate entry for ResiliencyNicLogical: %s" % e.columns
        )

    return rs


@b.session_aware()
def update_resiliency_nic_logical(id, values, session=None):
    rs = _get_resiliency_nic_logical(id)

    if not rs:
        raise exc.NotFoundException(
            "Resiliency Nic Logical not found [id=%s]" % id)

    rs.update(values.copy())

    return rs


@b.session_aware()
def create_or_update_resiliency_nic_logical(id, values, session=None):
    if not _get_resiliency_nic_logical(id):
        return create_resiliency_nic_logical(values)
    else:
        return update_resiliency_nic_logical(id, values)


@b.session_aware()
def delete_resiliency_nic_logical(id, session=None):
    rs = _get_resiliency_nic_logical(id)

    if not rs:
        raise exc.NotFoundException(
            "Resiliency Nic Logical not found [id=%s]" % id)

    session.delete(rs)


def _get_resiliency_nic_logical(id):
    return _get_db_object_by_id(models.ResiliencyNicLogical, id)


@b.session_aware()
def delete_resiliency_nic_logicals(**kwargs):
    return _delete_all(models.ResiliencyNicLogical, **kwargs)


#
# Resiliency Nic functions
#

def get_resiliency_nic(id):
    rs = _get_resiliency_nic(id)

    if not rs:
        raise exc.NotFoundException(
            "Resiliency Nic not found [id=%s]" % id)

    return rs


def get_resiliency_nics(**kwargs):
    return _get_collection_sorted_by_name(models.ResiliencyNic, **kwargs)


@b.session_aware()
def create_resiliency_nic(values, session=None):
    rs = models.ResiliencyNic()

    rs.update(values.copy())

    try:
        rs.save(session=session)
    except db_exc.DBDuplicateEntry as e:
        raise exc.DBDuplicateEntry(
            "Duplicate entry for ResiliencyNic: %s" % e.columns
        )

    return rs


@b.session_aware()
def update_resiliency_nic(id, values, session=None):
    rs = _get_resiliency_nic(id)

    if not rs:
        raise exc.NotFoundException(
            "Resiliency Nic not found [id=%s]" % id)

    rs.update(values.copy())

    return rs


@b.session_aware()
def create_or_update_resiliency_nic(id, values, session=None):
    if not _get_resiliency_nic(id):
        return create_resiliency_nic(values)
    else:
        return update_resiliency_nic(id, values)


@b.session_aware()
def delete_resiliency_nic(id, session=None):
    rs = _get_resiliency_nic(id)

    if not rs:
        raise exc.NotFoundException(
            "Resiliency Nic not found [id=%s]" % id)

    session.delete(rs)


def _get_resiliency_nic(id):
    return _get_db_object_by_id(models.ResiliencyNic, id)


@b.session_aware()
def delete_resiliency_nics(**kwargs):
    return _delete_all(models.ResiliencyNic, **kwargs)
