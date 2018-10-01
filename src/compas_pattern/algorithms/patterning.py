from compas.datastructures.mesh import Mesh

from compas_pattern.topology.conway_operators import *

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


    operators = {
        'conway_dual': conway_dual,
        'conway_join': conway_join,
        'conway_ambo': conway_ambo,
        'conway_kis': conway_kis,
        'conway_needle': conway_needle,
        'conway_zip': conway_zip,
        'conway_truncate': conway_truncate,
        'conway_ortho': conway_ortho,
        'conway_expand': conway_expand,
        'conway_gyro': conway_gyro,
        'conway_snub': conway_snub,
        'conway_meta': conway_meta,
        'conway_bevel': conway_bevel
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
