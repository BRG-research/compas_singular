"""
********************************************************************************
compas_pattern.algorithms
********************************************************************************

.. currentmodule:: compas_pattern.algorithms


Coloring
========

Algorithm for two-colouring of quad meshes.

.. autosummary::
    :toctree: generated/
    :nosignatures:

    TwoColourableProjection


Decomposition
=============

Algorithm for decomposition of surfaces into coarse quad meshes. Optional point and curve features.

.. autosummary::
    :toctree: generated/
    :nosignatures:

    surface_discrete_mapping
    boundary_triangulation
    Skeleton
    SkeletonDecomposition
    DecompositionRemap    
    

Interpolation
=============

Algorithm for combination and interpolation of quad meshes.

.. autosummary::
    :toctree: generated/
    :nosignatures:


"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from .coloring import *
from .decomposition import *
from .interpolation import *

__all__ = [name for name in dir() if not name.startswith('_')]
