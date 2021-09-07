****************************
Densification
****************************

This example shows how to densify a (coarse) quad mesh into a quad mesh. The datastructures allow to consider quad meshes with optional pseudo-quads to include pole compas_singularities. A pseudo-quad has the geometry of a triangular face (looks like a triangle) but has the topology of a quad face (has four vertices).


----


Regular quad mesh
=================

.. literalinclude:: ../../examples/00_densification.py

.. figure:: /_images/00_densification_0.png
    :figclass: figure
    :class: figure-img img-fluid

    Initial coarse quad mesh.

.. figure:: /_images/00_densification_1.png
    :figclass: figure
    :class: figure-img img-fluid

    First densification with a uniform subdivision value.

.. figure:: /_images/00_densification_2.png
    :figclass: figure
    :class: figure-img img-fluid

    Second densification with a uniform target length.

.. figure:: /_images/00_densification_3.png
    :figclass: figure
    :class: figure-img img-fluid

    Edited second densification with a specific subvidision value.

|

----


Quad mesh with pseudo-quads
=========================================

.. literalinclude:: ../../examples/00_densification_poles.py

.. figure:: /_images/00_densification_poles_0.png
    :figclass: figure
    :class: figure-img img-fluid

    Initial coarse quad mesh.

.. figure:: /_images/00_densification_poles_1.png
    :figclass: figure
    :class: figure-img img-fluid

    Densification with a uniform target length.

