# Copyright 2014 - Mirantis, Inc.
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

from oslo.config import cfg

from highlander.db.v1 import api as db_api
from highlander import config
from highlander.openstack.common import log as logging


CONF = cfg.CONF
LOG = logging.getLogger(__name__)


def main():
    config.parse_args()

    if len(CONF.config_file) == 0:
        print "Usage: sync_db --config-file <path-to-config-file>"
        return exit(1)

    logging.setup('Highlander')
    db_api.setup_db()



if __name__ == '__main__':
    main()
