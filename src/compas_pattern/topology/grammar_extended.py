from compas.datastructures.mesh import Mesh

from compas_pattern.topology.grammar_primitive import insert_vertex
from compas_pattern.topology.grammar_primitive import split_quad
from compas_pattern.topology.grammar_primitive import remove_edge

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
    'flat_corner_2',
    'extended_22122333',
    'extended_21443',
    'extended_212144321443',
    'extended_121443',
]

def flat_corner_2(mesh, fkey, corner):
    opposite_corner = split_quad(mesh, fkey, corner)
    mid_face = insert_vertex(mesh, (corner, opposite_corner))
    return mid_face

def vertex_pole(mesh, fkey, pole):
    opposite_corner = split_quad(mesh, fkey, pole)
    return opposite_corner

def vertex_partial_pole(mesh, fkey, pole, edge):
    opposite_corner = split_quad(mesh, fkey, pole)
    edge_midpoint = insert_vertex(mesh, edge)
    midpoint_edge = split_quad(mesh, )


def extended_21(mesh, fkey, a):

    b = mesh.face_vertex_descendant(fkey, a)
    c = mesh.face_vertex_descendant(fkey, b)
    d = mesh.face_vertex_descendant(fkey, c)

    c = primitive_2(mesh, fkey, a)
    fkey_1 = mesh.halfedge[a][c]
    e = primitive_1(mesh, fkey_1, a, c)

    return a, b, c, d, e

def extended_22122333(mesh, fkey_1, fkey_2, b):

    if mesh.face_vertex_descendant(fkey_1, b) not in mesh.face_vertices(fkey_2):
        fkey_1, fkey_2 = fkey_2, fkey_1

    e = mesh.face_vertex_descendant(fkey_1, b)
    f = mesh.face_vertex_descendant(fkey_1, e)
    a = mesh.face_vertex_descendant(fkey_1, f)
    c = mesh.face_vertex_descendant(fkey_2, b)
    d = mesh.face_vertex_descendant(fkey_2, c)

    primitive_2(mesh, fkey_1, b)
    primitive_2(mesh, fkey_2, b)

    fkey_3 = mesh.halfedge[b][e]
    fkey_4 = mesh.halfedge[e][b]

    g = primitive_1(mesh, fkey_3, b, e)

    primitive_2(mesh, fkey_3, g)
    primitive_2(mesh, fkey_4, g)

    primitive_3(mesh, f, b)
    primitive_3(mesh, d, b)
    primitive_3(mesh, g, e)

    return a, b, c, d, e, f, g


def extended_21443(mesh, fkey, a):
    
    a, b, c, d, g = extended_21(mesh, fkey, a)

    fkey_1 = mesh.halfedge[g][c]

    e = primitive_4(mesh, fkey_1, d, c, g)

    fkey_2 = mesh.halfedge[c][g]

    f = primitive_4(mesh, fkey_2, b, c, g)

    fkey_3 = primitive_3(mesh, g, c)

    return a, b, c, d, e, f, g

def extended_212144321443(mesh, fkey, a):

    a, b, c, d, g = extended_21(mesh, fkey, a)

    fkey_1 = mesh.halfedge[g][c]

    g, c, d, a, k, j, e = extended_21443(mesh, fkey_1, g)

    fkey_2 = mesh.halfedge[c][g]

    g, a, b, c, i, h, f = extended_21443(mesh, fkey_2, g)

    return a, b, c, d, e, f, g, h, i, j, k

def extended_121443(mesh, fkey):

    a, b, c = mesh.face_vertices(mesh, fkey)

    f = primitive_1(mesh, fkey, a, b)

    f, b, c, a, e = extended_21(mesh, fkey, f)





# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
