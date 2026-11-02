Your first project
==================

A CircuitSpec project is a YAML document describing the components in a system
and the connections between their ports. The YAML file is the source of truth;
the command-line tools read it to validate the design and create output files.

Create a file called ``motion.yaml``:

.. code-block:: yaml

   project:
     name: simple_motion
     version: 0.1.0

   instances:
     controller:
       component: ESP32_S3_ETH_POE
     driver:
       component: TMC2209

   connections:
     - controller.GPIO38 -> driver.STEP
     - controller.GPIO39 -> driver.DIR

The ``project`` section gives the design a name and version. Each entry under
``instances`` names one component in this design. A connection names its two
endpoints using ``instance.port -> instance.port``.

Validate the file:

.. code-block:: console

   circuitspec validate motion.yaml

When it is valid, CircuitSpec reports the project name and component count. If
validation fails, the CLI prints the problems and returns a non-zero exit status.

The `dual TMC2209 example <https://github.com/elphick/circuit-spec/blob/main/examples/dual_tmc2209.yaml>`_
adds a shared UART bus and named power nets. It is also run in the
:doc:`example gallery <../generated/gallery/index>`.

.. note::

   The built-in library is intentionally small. The current component definitions
   are a starting point for the example system, not authoritative electrical
   models or a complete ESP32/TMC2209 pinout reference.
