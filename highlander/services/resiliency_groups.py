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

from highlander.db.v1 import api as db_api_v1

def list_resiliency_groups_v1():

    with db_api_v1.transaction():
        rg_db = db_api_v1.get_resiliency_groups()

    return rg_db

def get_resiliency_group_v1(id):

    with db_api_v1.transaction():
        rg_db = db_api_v1.get_resiliency_group(id)

    return rg_db

def create_resiliency_group_v1(data):

    with db_api_v1.transaction():
        rg_db = db_api_v1.create_resiliency_group(data)

    return rg_db

def update_resiliency_group_v1(data):

    with db_api_v1.transaction():
        rg_db = db_api_v1.update_resiliency_group(data['id'], data)

    return rg_db

def delete_resiliency_group_v1(id):
    
    with db_api_v1.transaction():
        rg_db = db_api_v1.delete_resiliency_group(id)

    return rg_db