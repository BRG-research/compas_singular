"""
********************************************************************************
compas_pattern
********************************************************************************

.. currentmodule:: compas_pattern


.. toctree::
    :maxdepth: 1

    compas_pattern.algorithms
    compas_pattern.datastructures
    compas_pattern.rhino
    compas_pattern.geometry
    compas_pattern.topology
    compas_pattern.utilities

"""

from __future__ import print_function

import os


__author__    = ['Robin Oval', ]
__copyright__ = 'Copyright 2019 - Block Research Group, ETH Zurich'
__license__   = 'MIT License'
__email__     = 'rpho2@cam.ac.uk'

__version__ = '0.0.1'


HERE = os.path.dirname(__file__)
HOME = os.path.abspath(os.path.join(HERE, '../..'))
DATA = os.path.abspath(os.path.join(HERE, '../../data'))
TEMP = os.path.abspath(os.path.join(HERE, '../../temp'))

__all__ = []