"""
********************************************************************************
singular
********************************************************************************

.. currentmodule:: singular


.. toctree::
    :maxdepth: 1

    singular.algorithms
    singular.datastructures
    singular.rhino
    singular.geometry
    singular.topology
    singular.utilities

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