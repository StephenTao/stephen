Highlander
=======

Workflow Service for OpenStack cloud.


Prerequisites
-------------

It is necessary to install some specific system libs for installing Highlander. They can be installed on most popular operating system using their package manager (for Ubuntu - *apt*, for Fedora, CentOS - *yum*, for Mac OS - *brew* or *macports*).
The list of needed packages is shown below:

1. **python-dev**
2. **python-setuptools**
3. **python-pip**
4. **libffi-dev**
5. **libxslt1-dev (or libxslt-dev)**
6. **libxml2-dev**
7. **libyaml-dev**
8. **libssl-dev**

In case of ubuntu, just run::

    apt-get install python-dev python-setuptools libffi-dev libxslt1-dev libxml2-dev libyaml-dev libssl-dev

**Highlander can be used without authentication at all or it can works with OpenStack.**
In case of OpenStack, it works **only on Keystone v3**, make sure **Keystone v3** is installed.

Installation
------------

First of all, clone the repo and go to the repo directory::


    git clone https://github.com/stratustech/highlander.git
    cd highlander



**Devstack installation**



**Virtualenv installation**::

    tox

This will install necessary virtual environments and run all the project tests. Installing virtual environments may take significant time (~10-15 mins).

**Local installation**::

    pip install -e .

or::

    python setup.py install

===================
Configuring Highlander
===================

Highlander configuration is needed for getting it work correctly either with real OpenStack environment or without OpenStack environment.


1. Copy highlander.conf::

    cp etc/highlander.conf.sample etc/hihglander.conf

  *Note: hihglander.conf.sample is the example configuration file.*


2. Edit file *etc/highlander.conf*
3. **If you are not using OpenStack, skip this item.** Provide valid keystone auth properties::

    [keystone_authtoken]
    auth_uri = http://<Keystone-host>:5000/v3
    identity_uri = http://<Keystone-host:35357/
    auth_version = v3
    admin_user = <user>
    admin_password = <password>
    admin_tenant_name = <tenant>

4. **If you don't use OpenStack**, provide *auth_enable = False* in config file::

    [pecan]
    auth_enable = False

5. Also, configure rabbit properties: *rabbit_userid*, *rabbit_password*, *rabbit_host* in section *default*.

6. Configure database. **SQLite can't be used in production.** Use *MySQL* or *PostreSQL* instead. Here are the steps how to connect *MySQL* DB to Highlander:

* Make sure you have installed **mysql-server** package on your Highlander machine.
* Install *MySQL driver* for python::

    pip install mysql-python

  or, if you work in virtualenv, run::

    tox -evenv -- pip install mysql-python

* Create the database and grant privileges::

    mysql -u root -p


    CREATE DATABASE highlander;

    USE highlander
    GRANT ALL ON highlander.* TO 'root'@'localhost';

* Configure connection in Highlander config::

    [database]
    connection = mysql://root:@localhost:3306/highlander

Before the first run
--------------------


Before starting Highlander server, run sync_db script. It prepares the DB, creates in it all standard actions and standard workflows which Highlander provides for all hihglander users.


**If you use virtualenv**::

    tools/sync_db.sh --config-file path_to_config*

**Or run sync_db directly**::

    python tools/sync_db.py --config-file path_to_config*

*Note: After local installation you will see **highlander-server** and **highlander-db-manage** commands in your environment*.

Migrations
----------

*highlander-db-manage* command can be used for migrations. If Highlander is not installed in system then this script can be

 found at *highlander/db/sqlalchemy/migration/cli.py*, it can be executed using Python.

For updating the database to the latest revision type::

    highlander-db-manage --config-file <path-to-highlander.conf> upgrade head

For more detailed information about *highlander-db-manage* script please see migration readme here - https://github.com/stackforge/highlander/blob/master/highlander/db/sqlalchemy/migration/alembic_migrations/README.md


Running Highlander API server
--------------------------

To run Highlander API server perform the following command in a shell::

    tox -evenv -- python highlander/cmd/launch.py --server api --config-file path_to_config*

Running Highlander Engines
-----------------------

To run Highlander Engine perform the following command in a shell::

    tox -evenv -- python highlander/cmd/launch.py --server engine --config-file path_to_config*

Running Highlander Task Executors
------------------------------
To run Highlander Task Executor instance perform the following command in a shell::

    tox -evenv -- python highlander/cmd/launch.py --server executor --config-file path_to_config

Note that at least one Engine instance and one Executor instance should be running so that workflow tasks are processed by Highlander.

If it is needed to run some tasks on specific executor then *task affinity* feature can be used to send these tasks directly to specific executor. In configuration file edit section "executor" *host* property::

    [executor]
    host = my_favorite_executor

Then start (restart) executor. Use *target* task property to specify this executor::

    ... Workflow YAML ...
    task1:
      ...
      target: my_favorite_executor
    ... Workflow YAML ...

Running Multiple Highlander Servers Under the Same Process
-------------------------------------------------------
To run more than one server (API, Engine, or Task Executor) on the same process, perform the following command in a shell::

    tox -evenv -- python highlander/cmd/launch.py --server api,engine --config-file path_to_config

The --server command line option can be a comma delimited list. The valid options are "all" (by default if not specified) or any combination of "api", "engine", and "executor". It's important to note that the "fake" transport for the rpc_backend defined in the config file should only be used if "all" the Highlander servers are launched on the same process. Otherwise, messages do not get delivered if the Highlander servers are launched on different processes because the "fake" transport is using an in process queue.

Highlander client
--------------

Python-highlanderclient is available here - https://github.com/stackforge/python-highlanderclient


Debugging
---------

To debug using a local engine and executor without dependencies such as RabbitMQ, create etc/highlander.conf with the following settings::

    [DEFAULT]
    rpc_backend = fake

    [pecan]
    auth_enable = False

and run in pdb, PyDev or PyCharm::

    highlander/cmd/launch.py --server all --config-file etc/highlander.conf --use-debugger

Running examples
----------------

To run the examples find them in highlander-extra repository (https://github.com/stackforge/highlander-extra) and follow the instructions on each example.

Tests
-----

There is an ability to run part of functional tests in non-openstack mode locally. To do this:

1. set *auth_enable = False* in the *highlander.conf* and restart Highlander
2. execute::

    ./run_functional_tests.sh

To run tests for only one version need to specify it: bash run_functional_tests.sh v1

More information about automated tests for Highlander can be found here: https://wiki.openstack.org/wiki/Highlander/Testing
