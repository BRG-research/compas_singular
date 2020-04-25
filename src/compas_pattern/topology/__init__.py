"""
********************************************************************************
compas_pattern.topology
********************************************************************************

.. currentmodule:: compas_pattern.topology


Coloring
========

Coloring elements based on their topology.

.. autosummary::
    :toctree: generated/
    :nosignatures:

    is_adjacency_two_colorable


"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from .coloring import *

__all__ = [name for name in dir() if not name.startswith('_')]

