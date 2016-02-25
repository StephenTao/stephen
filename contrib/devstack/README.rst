1. Follow Devstack documentation to setup a host for Devstack. Then clone
   Devstack source code::

      $ git clone https://github.com/openstack-dev/devstack

1. Clone Highlander source code::

      $ git clone https://github.com/stratustech/highlander

1. Copy Highlander integration scripts to Devstack::

      $ cp highlander/contrib/devstack/lib/highlander ${DEVSTACK_DIR}/lib
      $ cp highlander/contrib/devstack/extras.d/70-highlander.sh ${DEVSTACK_DIR}/extras.d/

1. Create/modify a ``localrc`` file as input to devstack::

      $ cd devstack
      $ touch localrc

1. The Highlander service is not enabled by default, so it must be enabled in ``localrc``
   before running ``stack.sh``. This example of ``localrc``
   file shows all of the settings required for Highlander::

      # Enable Highlander
      enable_service highlander

1. Deploy your OpenStack Cloud with Highlander::

   $ ./stack.sh


Note: 
1. All needed Highlander keystone endpoints will be automatically created
during installation.
1. Python-highlanderclient also will be automatically cloned and installed.
