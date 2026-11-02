Glossary
========

.. glossary::
   :sorted:

   Bus
      A named group of two or more endpoints that share a communication or
      signal path, such as the UART members in the dual-driver example.

   Component
      A reusable hardware definition that declares a set of named ports.

   Endpoint
      A reference to one port on one component instance, written
      ``instance.port``.

   Instance
      A named use of a component definition within a project. A project may
      contain multiple instances of the same component.

   Net
      A set of connected endpoints. In CircuitSpec, a pairwise connection is
      represented as a net in the exported netlist; buses and power nets have
      explicit names.

   Port
      A named connection point exposed by a component, with a declared type and
      direction.

   Power net
      A named group of power ports connected to a common supply or reference,
      for example ``24V`` or ``GND``.

   Project
      The complete YAML description of a hardware system, including metadata,
      component instances, connections, buses, and power nets.

   Typed port graph
      A graph model whose connection endpoints are component ports with types
      and directions, allowing structural checks before rendering outputs.
