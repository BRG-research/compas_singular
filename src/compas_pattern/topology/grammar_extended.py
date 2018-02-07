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

    b = mesh.face_vertex_descendant(fkey, a)
    c = mesh.face_vertex_descendant(fkey, b)
    d = mesh.face_vertex_descendant(fkey, c)

    c = primitive_2(mesh, fkey, a)
    fkey_1 = mesh.halfedge[a][c]
    e = primitive_1(mesh, fkey_1, a, c)

    return [a, b, c, d, e]

def extended_21443(mesh, fkey, a):
    
    a, b, c, d, g = extended_21(mesh, fkey, a)

    fkey_1 = mesh.halfedge[g][c]

    e = primitive_4(mesh, fkey_1, d, c, g)

    fkey_2 = mesh.halfedge[c][g]

    f = primitive_4(mesh, fkey_2, b, c, g)

    fkey_3 = primitive_3(mesh, g, c)

    return 0 #[a, b, c, d, e, f, g]

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
