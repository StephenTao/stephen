# -*- coding: utf-8 -*-
#
# Copyright 2013 - Mirantis, Inc.
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

import six
import sqlalchemy as sa
from oslo.db.sqlalchemy import models as oslo_models
from oslo_utils import timeutils
from sqlalchemy import event
from sqlalchemy.ext import declarative
from sqlalchemy.orm import attributes
from sqlalchemy.orm import session as orm_session

from highlander import utils
from highlander.services import security


def id_column():
    return sa.Column(
        sa.String(36),
        primary_key=True,
        default=utils.generate_unicode_uuid
    )


def get_session():
    from heat.db.sqlalchemy import api as db_api
    return db_api.get_session()


class _HighlanderModelBase(oslo_models.ModelBase, oslo_models.TimestampMixin):
    """Base class for all Highlander SQLAlchemy DB Models."""

    __table__ = None

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    def __eq__(self, other):
        if type(self) is not type(other):
            return False

        for col in self.__table__.columns:
            # In case of single table inheritance a class attribute
            # corresponding to a table column may not exist so we need
            # to skip these attributes.
            if (hasattr(self, col.name)
                and hasattr(other, col.name)
                and getattr(self, col.name) != getattr(other, col.name)):
                return False

        return True

    def to_dict(self):
        """sqlalchemy based automatic to_dict method."""
        d = {}

        # If a column is unloaded at this point, it is
        # probably deferred. We do not want to access it
        # here and thereby cause it to load.
        unloaded = attributes.instance_state(self).unloaded

        for col in self.__table__.columns:
            if col.name not in unloaded and hasattr(self, col.name):
                d[col.name] = getattr(self, col.name)

        datetime_to_str(d, 'created_at')
        datetime_to_str(d, 'updated_at')

        return d

    def get_clone(self):
        """Clones current object, loads all fields and returns the result."""
        m = self.__class__()

        for col in self.__table__.columns:
            if hasattr(self, col.name):
                setattr(m, col.name, getattr(self, col.name))

        setattr(m, 'created_at', getattr(self, 'created_at').isoformat(' '))
        setattr(m, 'updated_at', getattr(self, 'updated_at').isoformat(' '))

        return m

    def update_and_save(self, values, session=None):
        if not session:
            session = orm_session.Session.object_session(self)
            if not session:
                session = get_session()
        session.begin()
        for k, v in six.iteritems(values):
            setattr(self, k, v)
        session.commit()

    def __repr__(self):
        return '%s %s' % (type(self).__name__, self.to_dict().__repr__())


def datetime_to_str(dct, attr_name):
    if dct.get(attr_name) is not None:
        dct[attr_name] = dct[attr_name].isoformat(' ')


class SoftDelete(object):
    deleted_at = sa.Column(sa.DateTime)

    def soft_delete(self, session=None):
        """Mark this object as deleted."""
        self.update_and_save({'deleted_at': timeutils.utcnow()},
                             session=session)


HighlanderModelBase = declarative.declarative_base(cls=_HighlanderModelBase)


# Secure model related stuff.


class HighlanderSecureModelBase(HighlanderModelBase):
    """Base class for all secure models."""

    __abstract__ = True
    scope = sa.Column(sa.String(8), default='private')
    project_id = sa.Column(sa.String(80), default=security.get_project_id)


def _set_project_id(target, value, oldvalue, initiator):
    return security.get_project_id()


def register_secure_model_hooks():
    # Make sure 'project_id' is always properly set.
    for sec_model_class in utils.iter_subclasses(HighlanderSecureModelBase):
        if '__abstract__' not in sec_model_class.__dict__:
            event.listen(
                sec_model_class.project_id,
                'set',
                _set_project_id,
                retval=True
            )
