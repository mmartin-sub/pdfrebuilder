.. _publishing:

##########
Publishing
##########

This guide explains how to build the project and publish it to PyPI.

Prerequisites
=============

- You must have an account on `PyPI <https://pypi.org/>`_.
- You must have `hatch` installed.

Building the Project
====================

The project is built using `hatch`. This will create the wheel and source distribution in the `dist/` directory.

.. code-block:: bash

   hatch build

Publishing to PyPI
==================

You can publish the project to PyPI using `hatch`.

1. **Configure your PyPI credentials**:
   `hatch` will securely store your credentials.

   .. code-block:: bash

      hatch config set publish.pypi.user __token__
      hatch config set publish.pypi.password <your-pypi-api-token>

2. **Publish the package**:
   This command will upload the contents of the `dist/` directory to PyPI.

   .. code-block:: bash

      hatch publish

   By default, this publishes to the public PyPI repository.

Publishing to TestPyPI
----------------------

It is highly recommended to first publish to `TestPyPI <https://test.pypi.org/>`_ to ensure everything is correct.

1. **Configure your TestPyPI credentials**:

   .. code-block:: bash

      hatch config set publish.test.user __token__
      hatch config set publish.test.password <your-testpypi-api-token>

2. **Publish to TestPyPI**:

   .. code-block:: bash

      hatch publish -r test
