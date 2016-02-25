# Copyright 2013 - Mirantis, Inc.
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

import yaml
from yaml import error

from highlander import exceptions as exc


V1_0 = '1.0'

ALL_VERSIONS = [V1_0]


def parse_yaml(text):
    """Loads a text in YAML format as dictionary object.

    :param text: YAML text.
    :return: Parsed YAML document as dictionary.
    """

    try:
        return yaml.safe_load(text) or {}
    except error.YAMLError as e:
        raise exc.DSLParsingException(
            "Definition could not be parsed: %s\n" % e
        )


def get_spec_version(spec_dict):
    # If version is not specified it will '2.0' by default.
    ver = V1_0

    if 'version' in spec_dict:
        ver = spec_dict['version']

    if not ver or str(float(ver)) not in ALL_VERSIONS:
        raise exc.DSLParsingException('Unsupported DSL version: %s' % ver)

    return ver





