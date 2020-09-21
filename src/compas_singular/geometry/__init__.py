"""
********************************************************************************
compas_singular.geometry
********************************************************************************

.. currentmodule:: compas_singular.geometry


Array
=====

Array functions.

.. autosummary::
    :toctree: generated/
    :nosignatures:

    line_array
    rectangular_array
    circular_array
    spiral_array


Polyline
========

Polyline class with additional methods.

.. autosummary::
    :toctree: generated/
    :nosignatures:

    Polyline


Projection
==========

Projection functions.

.. autosummary::
    :toctree: generated/
    :nosignatures:

    closest_point_on_circle
    closest_point_on_line
    closest_point_on_segment
    closest_point_on_polyline
    closest_point_on_polylines

"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from .array import *  # noqa: F401 F403
from .polyline import *  # noqa: F401 F403
from .projection import *  # noqa: F401 F403

__all__ = [name for name in dir() if not name.startswith('_')]
