"""
********************************************************************************
compas_singular.algorithms
********************************************************************************

.. currentmodule:: compas_singular.algorithms


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

import compas

if not compas.IPY:
    from .isomorphism import *  # noqa: F401 F403

from .layout import *  # noqa: F401 F403
from .propagation import *  # noqa: F401 F403
from .triangulation import *  # noqa: F401 F403
from .twocoloring import *  # noqa: F401 F403

from .decomposition import *  # noqa: F401 F403


__all__ = [name for name in dir() if not name.startswith('_')]
