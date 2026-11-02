Validation and outputs
======================

Validate before rendering
-------------------------

Run validation from the repository root:

.. code-block:: console

   circuitspec validate examples/dual_tmc2209.yaml

The current validator checks that components and ports are known, connections
use compatible port types and directions, bus and power members use appropriate
port kinds, and named nets do not duplicate or reassign endpoints.

Validation does **not** yet check electrical limits, complete pin requirements,
UART address conflicts, or manufacturing design rules. A successful result is
not proof that a circuit is safe or ready to build.

Graph output
------------

Export a Graphviz DOT description:

.. code-block:: console

   circuitspec render graph examples/dual_tmc2209.yaml -o circuit.dot

DOT describes component-level relationships and labels each edge with the
connected ports. You can inspect or render it with Graphviz tools installed
separately.

Netlist output
--------------

Export connections, buses, and power nets as JSON:

.. code-block:: console

   circuitspec export netlist examples/dual_tmc2209.yaml -o netlist.json

The JSON contains project metadata, component references, and a list of named
nets and their endpoint members.

Illustrative stripboard view
----------------------------

Generate a simple SVG connectivity map:

.. code-block:: console

   circuitspec render stripboard examples/dual_tmc2209.yaml -o stripboard.svg

This view shows labeled component positions and net rows. It is **not** a
manufacturing-ready stripboard layout: it does not place real footprints, define
copper cuts, check clearances, or account for electrical constraints. Review
and engineer the physical design independently before construction.

Executable example
------------------

The :doc:`gallery example <../generated/gallery/index>` loads the shared dual
driver YAML, validates it, and exercises the DOT, JSON, and SVG renderers when
Sphinx builds the documentation.
