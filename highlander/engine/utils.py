# Copyright 2014 - Mirantis, Inc.
# Copyright 2015 - Huawei Technologies Co. Ltd
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

import copy
import six

from highlander.db.v1 import api as db_api
from highlander import exceptions as exc
from highlander import expressions as expr
from highlander.openstack.common import log as logging
from highlander import utils
from highlander.maccleod import parser as spec_parser


LOG = logging.getLogger(__name__)


def validate_input(definition, spec, input):
    input_param_names = copy.copy((input or {}).keys())
    missing_param_names = []

    for p_name, p_value in six.iteritems(spec.get_input()):
        if p_value is utils.NotDefined and p_name not in input_param_names:
            missing_param_names.append(p_name)
        if p_name in input_param_names:
            input_param_names.remove(p_name)

    if missing_param_names or input_param_names:
        msg = 'Invalid input [name=%s, class=%s'
        msg_props = [definition.name, spec.__class__.__name__]

        if missing_param_names:
            msg += ', missing=%s'
            msg_props.append(missing_param_names)

        if input_param_names:
            msg += ', unexpected=%s'
            msg_props.append(input_param_names)

        msg += ']'

        raise exc.InputException(
            msg % tuple(msg_props)
        )
    else:
        utils.merge_dicts(input, spec.get_input(), overwrite=False)


