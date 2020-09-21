"""
********************************************************************************
compas_singular.datastructures
********************************************************************************

.. currentmodule:: compas_singular.datastructures


Network
=======

Network class.

.. autosummary::
    :toctree: generated/
    :nosignatures:

    Network

Mesh
=====

Mesh class.

Core
----

.. autosummary::
    :toctree: generated/
    :nosignatures:

    Mesh

Operations
----------

.. autosummary::
    :toctree: generated/
    :nosignatures:

    mesh_move_vertex_by
    mesh_move_by
    mesh_move_vertices_by
    mesh_move_vertex_to
    mesh_move_vertices_to

Coloring
--------

.. autosummary::
    :toctree: generated/
    :nosignatures:

    mesh_vertex_2_coloring
    mesh_vertex_n_coloring
    mesh_face_2_coloring
    mesh_face_n_coloring


Quad Mesh
=========

QuadMesh class.

Core
----

.. autosummary::
    :toctree: generated/
    :nosignatures:

    QuadMesh

Morphing
--------

.. autosummary::
    :toctree: generated/
    :nosignatures:

    fold
    fold_vertex_group

Coloring
--------

.. autosummary::
    :toctree: generated/
    :nosignatures:

    quad_mesh_strip_2_coloring
    quad_mesh_strip_n_coloring
    quad_mesh_polyedge_2_coloring
    quad_mesh_polyedge_n_coloring

Shape grammar
-------------

.. autosummary::
    :toctree: generated/
    :nosignatures:

    add_opening
    add_handle

Pattern grammar
---------------

.. autosummary::
    :toctree: generated/
    :nosignatures:

    add_and_delete_strips
    add_strip
    add_strips
    delete_strip
    delete_strips
    split_strip
    split_strips
    strip_polyedge_update
    strips_to_split_to_prevent_boundary_collapse
    collateral_strip_deletions
    total_boundary_deletions

Coarse Quad Mesh
================

CoarseQuadMesh class.

Core
----

.. autosummary::
    :toctree: generated/
    :nosignatures:

    CoarseQuadMesh

Coloring
--------

.. autosummary::
    :toctree: generated/
    :nosignatures:

    dense_quad_mesh_polyedge_2_coloring

Pseudo Quad Mesh
================

PseudoQuadMesh class.

Core
----

.. autosummary::
    :toctree: generated/
    :nosignatures:

    PseudoQuadMesh

Pole grammar
------------

.. autosummary::
    :toctree: generated/
    :nosignatures:

    split_quad_in_pseudo_quads
    merge_pseudo_quads_in_quad

Coarse Pseudo Quad Mesh
=======================

CoarsePseudoQuadMesh class.

.. autosummary::
    :toctree: generated/
    :nosignatures:

    CoarsePseudoQuadMesh

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from .mesh import *  # noqa: F401 F403
from .mesh_quad import *  # noqa: F401 F403
from .mesh_quad_coarse import *  # noqa: F401 F403
from .mesh_quad_pseudo import *  # noqa: F401 F403
from .mesh_quad_pseudo_coarse import *  # noqa: F401 F403
from .network import *  # noqa: F401 F403
from .skeleton import *  # noqa: F401 F403

__all__ = [name for name in dir() if not name.startswith('_')]
