Installation
============

CircuitSpec targets Python 3.12 or newer and uses `UV <https://docs.astral.sh/uv/>`_
to manage the project environment.

Install the package and its documentation dependencies from a repository checkout:

.. code-block:: console

   uv sync --extra docs

You can then run the command-line interface through UV:

.. code-block:: console

   uv run circuitspec --help

To build the documentation locally:

.. code-block:: console

   uv run sphinx-build -b html docs docs/_build/html

Open ``docs/_build/html/index.html`` in a browser to read the generated guide.
