from compas.datastructures.mesh import Mesh

from compas_pattern.topology.pattern_operators import conway_dual
from compas_pattern.topology.pattern_operators import conway_join
from compas_pattern.topology.pattern_operators import conway_ambo
from compas_pattern.topology.pattern_operators import conway_kis
from compas_pattern.topology.pattern_operators import conway_needle
from compas_pattern.topology.pattern_operators import conway_gyro

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
    'patterning',
]

def patterning(mesh, operator):
    """Apply a patterning operator on a mesh through general transformation.

    Parameters
    ----------
    mesh : Mesh
        A planar mesh to transform.
    operator_name : string
        An operator for mesh transformation.

    Returns
    -------
    mesh: Mesh
        The remapped mesh.

    Raises
    ------
    -

    """


    operators = {'dual': conway_dual, 
                 'join': conway_join,
                 'ambo': conway_ambo,
                 'kis': conway_kis,
                 'needle': conway_needle,
                 'gyro': conway_gyro,
                 }

    try:
        operators[operator](mesh)
        return mesh
    except:
        return mesh

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
