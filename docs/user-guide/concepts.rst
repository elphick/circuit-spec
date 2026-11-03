Core concepts
=============

Projects and instances
----------------------

A **project** describes one electronic system. The ``instances`` mapping gives
each physical or logical component an instance name, such as ``controller`` or
``turntable``. Multiple instances may refer to the same component definition.

Components and ports
--------------------

A **component** is a reusable definition with named **ports**. Ports have a
kind, such as ``signal``, ``bus``, or ``power``, and a direction, such as input,
output, or bidirectional. An instance exposes the ports defined for its
component. For example, ``turntable.STEP`` refers to the ``STEP`` port of the
``turntable`` instance.

Nets
----

A **net** groups two or more endpoints that are electrically connected:

.. code-block:: yaml

   nets:
     A_STEP: [controller.GPIO38, turntable.STEP]
     UART: [controller.GPIO40, turntable.UART, camera_slide.UART]

Signal, bus, and power connectivity all use the same ``nets`` mapping. Port
types determine their validation and graph styling; names such as ``UART``,
``3V3``, ``24V``, and ``GND`` remain ordinary net names.

Typed port graph
----------------

CircuitSpec models a design as named nets containing component-port endpoints.
Validation checks that an endpoint exists, that the port belongs to the named
component, and that each net contains compatible port types according to the
built-in definitions.

This validation is structural. It does not calculate voltage, current, timing,
signal integrity, or whether the chosen hardware is safe for a particular
application.
