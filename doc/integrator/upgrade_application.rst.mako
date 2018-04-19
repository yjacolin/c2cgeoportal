.. _integrator_upgrade_application:

==================================
Upgrading a GeoMapFish application
==================================


Then you have 4 different ways...


Upgrade a version 2.2
~~~~~~~~~~~~~~~~~~~~~

Add a section ``managed_files: [...]`` in the ``project.yaml.mako`` file.
The files that are not in this section will be overwritten,
see upgrade config to see original replacements (section `default_project_file`):
`for non Docker version <https://github.com/camptocamp/c2cgeoportal/blob/${git_branch}/geoportal/c2cgeoportal_geoportal/scaffolds/nondockerupdate/%2Bdot%2Bupgrade.yaml_tmpl>`_,
`for Docker version <https://github.com/camptocamp/c2cgeoportal/blob/${git_branch}/geoportal/c2cgeoportal_geoportal/scaffolds/update/%2Bdot%2Bupgrade.yaml_tmpl>`_.

Prepare the upgrade:

.. prompt:: bash

   git submodule deinit <package>/static/lib/cgxp/
   git rm .gitmodules
   curl https://raw.githubusercontent.com/camptocamp/c2cgeoportal/${git_branch}/docker-run > docker-run
   chmod +x docker-run
   git add docker-run project.yaml.mako
   git commit --quiet --message="Start upgrade"
   make --makefile=<user>.mk project.yaml

For non-Docker:

.. prompt:: bash

   ./docker-run --version=<version> --home --image=camptocamp/geomapfish-build ${'\\'}
       c2cupgrade --nondocker --makefile=<user>.mk

And for Docker (experimental):

.. prompt:: bash

   ./docker-run --version=<version> --home --image=camptocamp/geomapfish-build ${'\\'}
       c2cupgrade --force-docker --new-makefile=Makefile --makefile=<package>.mk

Where ``<version>`` is ``${major_version}.0`` for the first stable release of the version ``${major_version}``.

Then follow the instructions.

.. note:: Know issue

   if you have the following message:

   .. code::

      Host key verification failed.
      fatal: Could not read from remote repository.

      Please make sure you have the correct access rights
      and the repository exists.

   you can do the following command to fix it:

   .. prompt:: bash

      ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts


From a version 2.3 and next
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Change the version in the file ``.config`` to the wanted version.

For non Docker project:

.. prompt:: bash

   ./docker-run --home make --makefile=<user>.mk upgrade

For Docker project:

.. prompt:: bash

   ./docker-run --home make upgrade

Then follow the instructions.


Convert a version 2.3 to Docker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add ``UPGRADE_ARGS += --force-docker --new-makefile=Makefile`` in your ``<user>.mk`` file.

.. prompt:: bash

   git add <user>.mk
   git commit --message="Start upgrade"
   ./docker-run --home make --makefile=temp.mk upgrade

Then follow the instructions.

Remove the ``UPGRADE_ARGS`` in your ``<user>.mk`` file.

.. prompt:: bash

   git add <user>.mk
   git commit --quiet --message="Finish upgrade"


Convert a version 2.3 to non-Docker
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add the ``apache_vhost`` in the ``template_vars`` of the ``project.yaml.mako`` file.
Add ``UPGRADE_ARGS += --nondocker --new-makefile=<package>.mk`` in the ``Makefile``.

.. prompt:: bash

   git add project.yaml.mako Makefile
   git commit --message="Start upgrade"
   ./docker-run --home make --new-makefile=<user>.mk upgrade

Then follow the instructions.

Remove the ``UPGRADE_ARGS`` in your ``Makefile``.


Upgrade the database
--------------------

The database will be automatically upgraded during the upgrade process.

To upgrade only the database you can use alembic directly.

The help:

.. prompt:: bash

   ./docker-run alembic --help

Upgrade the main schema:

.. prompt:: bash

   ./docker-run alembic --name=main upgrade head

Upgrade the static schema:

.. prompt:: bash

   ./docker-run alembic --name=static upgrade head

.. _integrator_upgrade_application_cgxp_to_ngeo:

-----------------
From CGXP to ngeo
-----------------

Layer definition for ngeo clients is separate and different from layer
definition for CGXP clients, see :ref:`administrator_administrate_layers`
for details.
To migrate the layer definitions from the CGXP structure to the ngeo
structure, you can use the script ``.build/venv/bin/themev1tov2``.

Text translations for ngeo clients are separate and different from text
translations for CGXP clients.
To migrate the text translations from CGXP to ngeo, you can use the script
``.build/venv/bin/l10nv1tov2``.
For example, for converting french texts the script can be used as follows:

.. code:: bash

   .build/venv/bin/l10nv1tov2 fr geoportal/static/js/Proj/Lang/fr.js \
   geoportal/locale/fr/LC_MESSAGES/geoportal-client.po
