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

Export an interactive graph with embedded JavaScript for offline viewing:

.. code-block:: console

   circuitspec render graph examples/dual_tmc2209.yaml

The default output is ``artifacts/project_graph.html``. Components, connected
ports, and nets are visible nodes; edges are undirected and have no arrowheads.
The seeded force-directed layout describes topology, not physical placement or
signal flow. Bus diamonds have thicker outlines; power squares use red for
``24V``, orange for ``5V``, green for ``3V3``, black for ``GND``, and purple for
other power nets. Hover to inspect names, component types, and net members.

Choose another HTML path and optionally generate static documentation assets:

.. code-block:: console

   circuitspec render graph examples/dual_tmc2209.yaml --output artifacts/circuit.html \
       --png artifacts/circuit.png --svg artifacts/circuit.svg

Kaleido exports PNG and SVG using Chrome. Install Chrome normally or run
``uv run plotly_get_chrome`` before requesting images. HTML export needs neither
Chrome nor internet access. Output directories are created automatically.

The Python API consumes an already validated project:

.. code-block:: python

   from circuitspec.io import load_project
   from circuitspec.validation import require_valid
   from circuitspec.renderers import render_graph

   project = load_project("examples/dual_tmc2209.yaml")
   require_valid(project)
   fig = render_graph(project)  # plotly.graph_objects.Figure
   fig.write_html("circuit.html", include_plotlyjs=True)
   fig.write_image("circuit.png")  # or circuit.svg

``render_graph`` does not parse or validate specifications. Connected ports are
shown once per instance, including when several connections share a port;
unconnected instances remain visible.

Graphviz DOT output is still available via ``circuitspec render dot`` instead
of ``render graph``. The ``to_dot(project)`` Python API is unchanged.

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

The :doc:`Plotly gallery example <../generated/plotly/plotly_graph_renderer>`
loads YAML, validates it, saves offline HTML and PNG/SVG, and displays the
interactive figure. Chrome must be available for its image exports.

The :doc:`legacy gallery example <../generated/gallery/index>` loads the shared dual
driver YAML, validates it, and exercises the DOT, JSON, and SVG renderers when
Sphinx builds the documentation. It displays the rendered graph and complete
netlist JSON alongside their generating code. Rendering the graph requires
Graphviz to be installed separately, with its ``dot`` executable on ``PATH``;
the Python wrapper is included in the ``docs`` extra.
