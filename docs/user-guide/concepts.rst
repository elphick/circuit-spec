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

Connections and nets
--------------------

A **connection** joins two endpoints. The shorthand
``controller.GPIO38 -> turntable.STEP`` describes a one-to-one connection.
Multiple connections may use the same component but each one remains an
individual pair in the current graph model.

A **bus** and a **power net** each group two or more endpoints under one name.
Use buses for shared links such as UART, and power nets for common rails such as
``3V3``, ``24V``, or ``GND``. These named groups are included in graph and
netlist output.

Typed port graph
----------------

CircuitSpec models a design as a graph whose vertices are component ports rather
than just component boxes. This lets validation check that an endpoint exists,
that the port belongs to the named component, and that connected port types and
directions are sensible according to the built-in definitions.

This validation is structural. It does not calculate voltage, current, timing,
signal integrity, or whether the chosen hardware is safe for a particular
application.
