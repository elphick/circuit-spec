CircuitSpec
===========

.. image:: _static/circuitspec-logo.svg
   :alt: CircuitSpec placeholder logo: a circuit trace forming a letter C
   :width: 240 px
   :align: center

**Hardware specification as code.** Describe components and their connections
once, validate the typed port graph, and use that specification as the starting
point for circuit artifacts.

CircuitSpec is an early-stage tool. The current release supports YAML projects,
basic connectivity validation, DOT graph output, JSON netlists, and an
illustrative stripboard connection map. Its renderings are not manufacturing
outputs; review all hardware designs before building them.

.. toctree::
   :maxdepth: 2
   :caption: User guide

   user-guide/installation
   user-guide/first-project
   user-guide/concepts
   user-guide/validation-and-outputs

.. toctree::
   :maxdepth: 1
   :caption: Examples

   generated/gallery/index

.. toctree::
   :maxdepth: 1
   :caption: Reference

   glossary
