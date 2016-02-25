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


from highlander.engine import base

from highlander.openstack.common import log as logging




LOG = logging.getLogger(__name__)

# Submodules of highlander.engine will throw NoSuchOptError if configuration
# options required at top level of this  __init__.py are not imported before
# the submodules are referenced.


class DefaultEngine(base.Engine):
    def __init__(self, engine_client):
        self._engine_client = engine_client

   
   
