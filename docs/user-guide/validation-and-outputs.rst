Validation and outputs
======================

Validate before rendering
-------------------------

Run validation from the repository root:

.. code-block:: console

   circuitspec validate examples/dual_tmc2209.yaml

The validator checks that components and ports are known, nets are non-empty
and uniquely named, endpoints are not duplicated or assigned to multiple nets,
and each net uses compatible port types.

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
shown once per instance, including when they are listed in multiple nets;
unconnected instances remain visible.

Graphviz DOT output is still available via ``circuitspec render dot`` instead
of ``render graph``. The ``to_dot(project)`` Python API is unchanged.

Netlist output
--------------

Export all nets and their endpoints as YAML:

.. code-block:: console

   circuitspec export netlist examples/dual_tmc2209.yaml -o netlist.yaml

The exported mapping contains each net name and its ``instance.port`` endpoints.

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

The :doc:`Plotly gallery example <../generated/gallery/02_plotly_graph_renderer>`
loads YAML, validates it, saves offline HTML and PNG/SVG, and displays the
interactive figure with ``plotly.io.show``. Plotly's Sphinx-Gallery scraper
generates a thumbnail using Kaleido, so Chrome must be available during the
documentation build. The gallery figure loads Plotly JavaScript from a CDN;
exported HTML embeds it for offline viewing. Outside documentation builds,
``show`` uses your normal Plotly renderer.

The :doc:`legacy gallery example <../generated/gallery/01_plot_dual_tmc2209>` loads the shared dual
driver YAML, validates it, and exercises the DOT, YAML, and SVG renderers when
Sphinx builds the documentation. It displays the rendered graph and complete
netlist YAML alongside their generating code. Rendering the graph requires
Graphviz to be installed separately, with its ``dot`` executable on ``PATH``;
the Python wrapper is included in the ``docs`` extra.
