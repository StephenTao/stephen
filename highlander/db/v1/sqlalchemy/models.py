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

import sqlalchemy as sa
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import backref
from sqlalchemy.orm import relationship

from highlander import utils
from highlander.db.sqlalchemy import model_base as mb
from highlander.db.sqlalchemy import types as st

RESILIENCY_STRATEGY_TYPES = sa.Enum('ufr', 'ft', 'nm')


def id_column_with_fk(fk):
    return sa.Column(
        sa.String(36),
        sa.ForeignKey(fk),
        primary_key=True,
        default=utils.generate_unicode_uuid
    )


class ResiliencyBase(mb.HighlanderSecureModelBase, mb.SoftDelete):
    __abstract__ = True

    id = mb.id_column()
    name = sa.Column(sa.String(80))
    desc = sa.Column(sa.String(255))


#
# Represents a grouping of server groups (pairs for UFR/FT, clusters for NM)
#

class ResiliencyGroup(ResiliencyBase):
    __tablename__ = 'resiliency_group'

    __table_args__ = (
        sa.UniqueConstraint('name', 'project_id'),
    )

    resiliency_strategy_type = sa.Column(RESILIENCY_STRATEGY_TYPES, nullable=False)

    # Heat stack "foreign key"
    stack_id = sa.Column(sa.String(36))


#
# Represents a pair (UFR/FT) or cluster (NM) of resiliency servers
#

class ResiliencyServerGroup(ResiliencyBase):
    __tablename__ = 'resiliency_server_group'

    __table_args__ = (
        sa.UniqueConstraint('name', 'project_id'),
    )

    resiliency_strategy_type = sa.Column(RESILIENCY_STRATEGY_TYPES, nullable=False)


ResiliencyServerGroup.resiliency_group_id = sa.Column(
    sa.String(36),
    sa.ForeignKey(ResiliencyGroup.id),
    nullable=True
)

ResiliencyGroup.resiliency_server_groups = relationship(
    ResiliencyServerGroup,
    backref=backref('resiliency_group', remote_side=[ResiliencyGroup.id]),
    cascade='all, delete-orphan',
    foreign_keys=ResiliencyServerGroup.resiliency_group_id,
    lazy='select'
)


#
# Represents an individual instance belonging to a resiliency server group
#

class ResiliencyServer(ResiliencyBase):
    """Resiliency server object."""

    __tablename__ = 'resiliency_server'

    # Main properties.
    resiliency_strategy_type = sa.Column(RESILIENCY_STRATEGY_TYPES, nullable=False)

    __table_args__ = (
        sa.UniqueConstraint('name', 'project_id'),
    )

    # Not making instance_id a foreign key to the associated Nova table for now,
    # because I don't believe cross-database references are possible.  Neutron
    # seems to do this with "device_id" on ports, which is a UUID of a Nova
    # instance
    instance_id = sa.Column(sa.String(36))

    # Which side am I? (1 or 2 for UFR/FT, 1 to N for NM)
    resiliency_id = sa.Column(sa.Integer)

    # Am I a replacement?
    is_recovery = sa.Column(sa.Boolean)
    target_recovery_hypervisor_id = sa.Column(sa.String(255))

    # Was I relocated?
    was_relocated = sa.Column(sa.Boolean)
    
    # Am I affinitized?  If so, to what grouping?
    affinity = sa.Column(sa.String(80))

    __mapper_args__ = {
        'polymorphic_identity': 'resiliency_server',
        'polymorphic_on': resiliency_strategy_type
    }


# Who replaced me (if anyone)?
ResiliencyServer.replacement_resiliency_server_id = sa.Column(
    sa.String(36),
    sa.ForeignKey(ResiliencyServer.id),
    nullable=True
)

ResiliencyServer.resiliency_server_group_id = sa.Column(
    sa.String(36),
    sa.ForeignKey(ResiliencyServerGroup.id),
    nullable=True
)

ResiliencyServerGroup.resiliency_servers = relationship(
    ResiliencyServer,
    backref=backref('resiliency_server_group', remote_side=[ResiliencyServerGroup.id]),
    cascade='all, delete-orphan',
    foreign_keys=ResiliencyServer.resiliency_server_group_id,
    lazy='select'
)


#
# Represents a logical disk shared between the resiliency servers belonging
# to a particular resiliency server group
#

class ResiliencyDiskLogical(ResiliencyBase):
    """Resiliency logical disk object."""

    __tablename__ = 'resiliency_disk_logical'

    # Which disk am I? (1, 2, 3, etc...)
    disk_id = sa.Column(sa.Integer)
    disk_size = sa.Column(sa.String(40))
    type = sa.Column(sa.String(40))

    __mapper_args__ = {
        'polymorphic_identity': 'resiliency_disk_logical',
        'polymorphic_on': type
    }


ResiliencyDiskLogical.resiliency_server_group_id = sa.Column(
    sa.String(36),
    sa.ForeignKey(ResiliencyServerGroup.id),
    nullable=False
)

ResiliencyServerGroup.resiliency_disk_logicals = relationship(
    ResiliencyDiskLogical,
    backref=backref('resiliency_server_group', remote_side=[ResiliencyServerGroup.id]),
    cascade='all, delete-orphan',
    foreign_keys=ResiliencyDiskLogical.resiliency_server_group_id,
    lazy='select'
)


#
# Represents the physical disk/volume associated with a particular resiliency
# server belonging to a particular resiliency server group
#

class ResiliencyDisk(ResiliencyBase):
    """Resiliency disk physical object."""

    __tablename__ = 'resiliency_disk'

    disk_size = sa.Column(sa.String(40))
    type = sa.Column(sa.String(40))
    volume_id = sa.Column(sa.String(36))
    resiliency_id = sa.Column(sa.Integer)

    __mapper_args__ = {
        'polymorphic_identity': 'resiliency_disk',
        'polymorphic_on': type
    }


ResiliencyDisk.resiliency_server_id = sa.Column(
    sa.String(36),
    sa.ForeignKey(ResiliencyServer.id),
    nullable=False
)

ResiliencyServer.resiliency_disks = relationship(
    ResiliencyDisk,
    backref=backref('resiliency_server', remote_side=[ResiliencyServer.id]),
    cascade='all, delete-orphan',
    foreign_keys=ResiliencyDisk.resiliency_server_id,
    lazy='select'
)


#
# Represents a logical nic shared between the resiliency servers belonging
# to a particular resiliency server group (also known as a free-floating
# port in Stratus terminology)
#

class ResiliencyNicLogical(ResiliencyBase):
    """Resiliency nic logical object."""

    __tablename__ = 'resiliency_nic_logical'

    type = sa.Column(sa.String(40))
    # Which nic am I (1, 2, 3, etc...)?
    nic_id = sa.Column(sa.Integer)
    # For free-floating (logical) ports
    port_id = sa.Column(sa.String(36))

    __mapper_args__ = {
        'polymorphic_identity': 'resiliency_nic',
        'polymorphic_on': type
    }


ResiliencyNicLogical.resiliency_server_group_id = sa.Column(
    sa.String(36),
    sa.ForeignKey(ResiliencyServerGroup.id),
    nullable=False
)

ResiliencyServerGroup.resiliency_nic_logicals = relationship(
    ResiliencyNicLogical,
    backref=backref('resiliency_server_group', remote_side=[ResiliencyServerGroup.id]),
    cascade='all, delete-orphan',
    foreign_keys=ResiliencyNicLogical.resiliency_server_group_id,
    lazy='select'
)


#
# Represents the physical nic associated with a particular resiliency
# server belonging to a particular resiliency server group
#

class ResiliencyNic(ResiliencyBase):
    """Represents a port."""

    __tablename__ = 'resiliency_nic'

    port_id = sa.Column(sa.String(36))

    __mapper_args__ = {
        'polymorphic_identity': 'resiliency_nic_port',
    }


ResiliencyNic.resiliency_server_id = sa.Column(
    sa.String(36),
    sa.ForeignKey(ResiliencyServer.id),
    nullable=False
)

ResiliencyServer.resiliency_nics = relationship(
    ResiliencyNic,
    backref=backref('resiliency_server', remote_side=[ResiliencyServer.id]),
    cascade='all, delete-orphan',
    foreign_keys=ResiliencyNic.resiliency_server_id,
    lazy='select'
)


#
# FT objects
#

class FTBase(mb.HighlanderSecureModelBase):
    """Abstract FT base object."""

    __abstract__ = True

    id = mb.id_column()
    state = sa.Column(st.JsonDictType())

    @declared_attr
    def resiliency_server_id(self):
        return sa.Column(sa.String(36), sa.ForeignKey(ResiliencyServer.id), primary_key=True)


#
# PVM Objects
#

class FTPvm(FTBase):
    """Represents a PVM as understood by a particular FT node."""

    __tablename__ = 'ft_pvm'

    ax_removal_pending = sa.Column(sa.Boolean)
    device_affinity = sa.Column(sa.Boolean)
    force_boot_override = sa.Column(sa.Boolean)
    ft_protected = sa.Column(sa.Boolean)
    host1_version = sa.Column(sa.String(20))
    host2_version = sa.Column(sa.String(20))
    name = sa.Column(sa.String(255))
    preferred_ax = sa.Column(sa.Integer)
    product_name = sa.Column(sa.String(255))
    protection_mode = sa.Column(sa.String(20))
    remote_ax_visible = sa.Column(sa.Boolean)
    version = sa.Column(sa.String(20))
    previous_state_change_date_time = sa.Column(sa.DateTime)
    automated_recovery = sa.Column(sa.Boolean)

    def to_dict(self):
        d = super(FTPvm, self).to_dict()

        mb.datetime_to_str(d, 'previous_state_change_date_time')

        return d


class FTPvmChildBase(FTBase):
    """Abstract FTPvm child object."""

    __abstract__ = True

    @declared_attr
    def ft_pvm_id(self):
        return sa.Column(sa.String(36), sa.ForeignKey(FTPvm.id))


class FTGuestOs(FTPvmChildBase):
    """Represents the GuestOS of a PVM as understood by a particular FT node."""

    __tablename__ = 'ft_guest_os'

    auto_resynch = sa.Column(sa.Boolean)
    auto_start = sa.Column(sa.Boolean)
    currently_capable_of_online_migration = sa.Column(sa.Boolean)
    synch_idle_timer = sa.Column(sa.Integer)
    synch_idle_timer_limits = sa.Column(st.JsonDictType())


class FTGuestOsChildBase(FTPvmChildBase):
    """Abstract FTGuestOs child object."""

    __abstract__ = True

    @declared_attr
    def ft_guest_os_id(self):
        return sa.Column(sa.String(36), sa.ForeignKey(FTGuestOs.id))

    pci_bus = sa.Column(sa.String(20))
    pci_domain = sa.Column(sa.String(20))
    pci_function = sa.Column(sa.String(20))
    pci_slot = sa.Column(sa.String(20))


class FTLDisk(FTGuestOsChildBase):
    """Represents a logical disk of a PVM as understood by a particular FT node."""

    __tablename__ = 'ft_ldisk'

    boot_device = sa.Column(sa.Boolean)
    sector_size = sa.Column(sa.Integer)
    total_num_sectors = sa.Column(sa.Integer)
    mirror_copy_state = sa.Column(sa.String(20))
    mirror_copy_source = sa.Column(sa.Integer)
    mirror_copy_target = sa.Column(sa.Integer)
    capacity = sa.Column(sa.Integer)
    percent_complete = sa.Column(sa.Integer)
    mirror_copy_rate = sa.Column(sa.Integer)
    mirror_copy_type = sa.Column(sa.String(20))
    ldisk_id = sa.Column(sa.Integer)
    ldisk_type = sa.Column(sa.String(20))


FTLDisk.resiliency_disk_id = sa.Column(
    sa.String(36),
    sa.ForeignKey(ResiliencyDisk.id),
    nullable=True
)


class FTLNic(FTGuestOsChildBase):
    """Represents a logical NIC of a PVM as understood by a particular FT node."""

    __tablename__ = 'ft_lnic'

    lnic_id = sa.Column(sa.Integer)
    # need some sort of foreign-key column that refers to free-floating port
    desired_ip = sa.Column(sa.String(15))


FTLNic.resiliency_nic_id = sa.Column(
    sa.String(36),
    sa.ForeignKey(ResiliencyNic.id),
    nullable=True
)


class FTALink(FTPvmChildBase):
    """Represents the ALinks of a PVM as understood by a particular FT node."""

    __tablename__ = 'ft_alink'


class FTALinkChildBase(FTPvmChildBase):
    """Abstract FTALink child object."""

    __abstract__ = True

    @declared_attr
    def ft_alink_id(self):
        return sa.Column(sa.String(36), sa.ForeignKey(FTALink.id))


class FTPath(FTALinkChildBase):
    """Represents one ALink path of a PVM as understood by a particular FT node."""

    __tablename__ = 'ft_path'

    path_id = sa.Column(sa.Integer)


class FTQuorum(FTPvmChildBase):
    """Represents the Quorum of a PVM as understood by a particular FT node."""

    __tablename__ = 'ft_quorum'

    quorum_service_enabled = sa.Column(sa.Boolean)
    boot_blocked = sa.Column(sa.Boolean)
    boot_blocked_reason = sa.Column(sa.String(255))
    join_blocked = sa.Column(sa.Boolean)
    join_blocked_reason = sa.Column(sa.String(255))
    elected_host_name = sa.Column(sa.String(255))
    elected_host_ip_address = sa.Column(sa.String(255))
    preferred_host_name = sa.Column(sa.String(255))
    preferred_host_ip_address = sa.Column(sa.String(255))
    alternate_host_name = sa.Column(sa.String(255))
    alternate_host_ip_address = sa.Column(sa.String(255))
    enabled = sa.Column(sa.Boolean)
    preferred_host_port = sa.Column(sa.Integer)
    alternate_host_port = sa.Column(sa.Integer)
    suppress_degraded_pvm = sa.Column(sa.Boolean)


class FTQuorumChildBase(FTPvmChildBase):
    """Abstract FTQuorum child object."""

    __abstract__ = True

    @declared_attr
    def ft_quorum_id(self):
        return sa.Column(sa.String(36), sa.ForeignKey(FTQuorum.id))


class FTQLink(FTQuorumChildBase):
    """Represents one Quorum link of a PVM as understood by a particular FT node."""

    __tablename__ = 'ft_qlink'

    qlink_id = sa.Column(sa.Integer)
    which = sa.Column(sa.String(20))

    __table_args__ = (
        sa.UniqueConstraint('ft_quorum_id', 'qlink_id', 'which'),
    )


#
# AX Objects
#

class FTAx(FTBase):
    """Represents an AX as understood by a particular FT node."""

    __tablename__ = 'ft_ax'

    auto_start = sa.Column(sa.Boolean)
    ax_id = sa.Column(sa.Integer)
    init_interval = sa.Column(sa.Integer)
    offline_mode = sa.Column(sa.Boolean)
    remote_ax_status = sa.Column(sa.String(20))
    scrub_interval = sa.Column(sa.Integer)
    scrub_switch = sa.Column(sa.Boolean)
    sw_revision = sa.Column(sa.String(20))

    ft_pvm_id = sa.Column(sa.String(36), sa.ForeignKey(FTPvm.id))


class FTAxChildBase(FTBase):
    """Abstract FTAx child object."""

    __abstract__ = True

    @declared_attr
    def ft_ax_id(self):
        return sa.Column(sa.String(36), sa.ForeignKey(FTAx.id))


class FTGuest(FTAxChildBase):
    """Represents the underlying Guest of an AX as understood by a particular FT node."""

    __tablename__ = 'ft_guest'

    autoSynch = sa.Column(sa.Boolean)
    autoBoot = sa.Column(sa.Boolean)


class FTDisk(FTAxChildBase):
    """Represents an underlying Disk of an AX as understood by a particular FT node."""

    __tablename__ = 'ft_disk'

    capacity = sa.Column(sa.Integer)
    mirrored = sa.Column(sa.Boolean)
    virtual_disk = sa.Column(sa.Boolean)
    ax_access = sa.Column(sa.Boolean)
    sector_size = sa.Column(sa.Integer)
    number_of_sectors = sa.Column(sa.Integer)
    immigrant = sa.Column(sa.Boolean)
    scrub_switch = sa.Column(sa.Boolean)
    ft_scrub_status = sa.Column(st.JsonDictType())
    enabled = sa.Column(sa.Boolean)
    zbc_switch = sa.Column(sa.Boolean)
    ft_zbc_status = sa.Column(st.JsonDictType())
    type = sa.Column(sa.String(20))
    previous_state_change_date_time = sa.Column(sa.DateTime)

    ft_ldisk_id = sa.Column(sa.String(36), sa.ForeignKey(FTLDisk.id))


class FTNic(FTAxChildBase):
    """Represents an underlying NIC of an AX as understood by a particular FT node."""

    __tablename__ = 'ft_nic'

    ft_ip_config = sa.Column(st.JsonDictType())
    ft_remote_ip_config = sa.Column(st.JsonDictType())
    device_name = sa.Column(sa.String(255))
    enabled = sa.Column(sa.Boolean)
    mac = sa.Column(sa.String(17))
    network_bridge = sa.Column(sa.String(255))

    ft_lnic_id = sa.Column(sa.String(36), sa.ForeignKey(FTLNic.id))


class FTLinkA(FTAxChildBase):
    """Represents an underlying ALink interface of an AX as understood by a particular FT node."""

    __tablename__ = 'ft_linka'

    adapter_id = sa.Column(sa.Integer)
    adapter_name = sa.Column(sa.String(255))
    ft_ip_config = sa.Column(st.JsonDictType())
    ft_remote_ip_config = sa.Column(st.JsonDictType())


# register all hooks related to secure models
mb.register_secure_model_hooks()
