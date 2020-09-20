"""
********************************************************************************
compas_singular.utilities
********************************************************************************

.. currentmodule:: compas_singular.utilities


Lists
=====

Some utilities to manipulate lists.

.. autosummary::
    :toctree: generated/
    :nosignatures:

    list_split
    sublist_from_to_items_in_closed_list
    are_items_in_list
    common_items
    remove_isomorphism_in_integer_list


Pareto
======

Some utilities to extract Pareto fronts.

.. autosummary::
    :toctree: generated/
    :nosignatures:

    extract_pareto_indices
    is_dominating


"""

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from .lists import *  # noqa: F401 F403
from .pareto import *  # noqa: F401 F403

__all__ = [name for name in dir() if not name.startswith('_')]
