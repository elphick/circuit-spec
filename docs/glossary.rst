Glossary
========

.. glossary::
   :sorted:

   Bus
      A net used for a shared communication or signal path, such as UART in the
      dual-driver example.

   Component
      A reusable hardware definition that declares a set of named ports.

   Endpoint
      A reference to one port on one component instance, written
      ``instance.port``.

   Instance
      A named use of a component definition within a project. A project may
      contain multiple instances of the same component.

   Net
      A named set of two or more electrically connected endpoints.

   Port
      A named connection point exposed by a component, with a declared type and
      direction.

   Power net
      A net connecting power ports to a common supply or reference, for example
      ``24V`` or ``GND``.

   Project
      The complete YAML description of a hardware system, including metadata,
      component instances, and nets.

   Typed port graph
      A graph model whose net endpoints are component ports with types and
      directions, allowing structural checks before rendering outputs.
