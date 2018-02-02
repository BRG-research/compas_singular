from compas.datastructures.mesh import Mesh

from compas_pattern.topology.grammar_primitive import primitive_1
from compas_pattern.topology.grammar_primitive import primitive_2
from compas_pattern.topology.grammar_primitive import primitive_3
from compas_pattern.topology.grammar_primitive import primitive_4
from compas_pattern.topology.grammar_primitive import primitive_5

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
    'extended_21',
]

def extended_21(mesh, fkey, a):

    c = primitive_2(mesh, fkey, a)
    fkey_1 = mesh.halfedge[a][c]
    primitive_1(mesh, fkey_1, a, c)

    return 0

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
