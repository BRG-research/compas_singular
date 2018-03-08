from compas.datastructures.mesh import Mesh

from compas_pattern.topology.grammar_primitive import primitive_insert_vertex
from compas_pattern.topology.grammar_primitive import primitive_insert_edge
from compas_pattern.topology.grammar_primitive import primitive_remove_edge

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
    'extended_21',
]

def extended_flat_corner_2(mesh, fkey, a):

    if len(mesh.face_vertices(fkey)) != 4:
        return None

    b = mesh.face_vertex_descendant(fkey, a)
    c = mesh.face_vertex_descendant(fkey, b)
    d = mesh.face_vertex_descendant(fkey, c)

    primitive_insert_edge(mesh, (a, c))
    e = primitive_insert_vertex(mesh, (a, c))
    
    return a, b, c, d, e

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas

    vertices = [[0,0,0],[1,0,0],[1,1,0],[0,1,0]]
    faces = [[0,1,2,3]]
    mesh = Mesh.from_vertices_and_faces(vertices, faces)

    print mesh

    extended_flat_corner_2(mesh, 0, 1)

    print mesh
    for fkey in mesh.faces():
        print mesh.face_vertices(fkey)
