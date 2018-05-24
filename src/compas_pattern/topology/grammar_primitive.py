from compas.datastructures.mesh import Mesh

from compas_pattern.datastructures.mesh import insert_vertices_in_halfedge
from compas_pattern.datastructures.mesh import insert_vertex_in_face
from compas_pattern.datastructures.mesh import add_vertex_from_vertices

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
    'primitive_add_vertex',
    'primitive_delete_vertex',
    'primitive_add_edge',
    'primitive_delete_edge',
]

def primitive_add_vertex(mesh, edge):
    """Add a vertex on an edge adjacent to triangles.

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    edge: tuple
        Edge vertex keys.

    Returns
    -------
    x : int
        The new vertex.

    Raises
    ------
    -

    """

    u, v = edge

    # new vertex
    x = add_vertex_from_vertices(mesh, [u, v], [1, 1])

    # update adjacent faces
    insert_vertices_in_halfedge(mesh, u, v, [x])
    insert_vertices_in_halfedge(mesh, v, u, [x])

    return x

def primitive_delete_vertex(mesh, vkey):
    """Delete a two-valent vertex.

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    edge: tuple
        Edge vertex keys.

    Returns
    -------
    edge : tuple
        The new edge.

    Raises
    ------
    -

    """

    edge = mesh.vertex_neighbours(vkey)

    vertex_faces = mesh.vertex_faces(vkey)
    for fkey in vertex_faces:
        face_vertices = mesh.face_vertices(fkey)[:]
        face_vertices.remove(vkey)
        mesh.delete_face(fkey)
        mesh.add_face(face_vertices, fkey)

    return edge

def primitive_add_edge(mesh, fkey, diagonal):
    """Add a diagonal edge to a quad face.

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    fkey : int
        Quad face key.
    vertices: tuple
        Diagonal vertex keys.

    Returns
    -------
    (u, v): tuple
        The new edge.

    Raises
    ------
    -

    """

    a = diagonal[0]
    b = mesh.face_vertex_descendant(fkey, a)
    c = mesh.face_vertex_descendant(fkey, b) # = diagonal[1]
    d = mesh.face_vertex_descendant(fkey, c)
    
    # delete old faces
    mesh.delete_face(fkey)

    # create new faces
    mesh.add_face([a, b, c])
    mesh.add_face([a, c, d])

    return diagonal

def primitive_delete_edge(mesh, edge):
    """Remove an edge adjacent to two triangular faces.

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    edge: tuple
        Edge vertex keys.

    Returns
    -------
    fkey : int
        The new face.

    Raises
    ------
    -

    """

    u, v = edge

    fkey_0 = mesh.halfedge[u][v]
    fkey_vertices_0 = mesh.face_vertices(fkey_0)
    idx = fkey_vertices_0.index(v)
    part_0 = fkey_vertices_0[idx :] + fkey_vertices_0[: idx]
    part_0 = part_0[1 : -1]

    fkey_1 = mesh.halfedge[v][u]
    fkey_vertices_1 = mesh.face_vertices(fkey_1)
    idx = fkey_vertices_1.index(u)
    part_1 = fkey_vertices_1[idx :] + fkey_vertices_1[: idx]
    part_1 = part_1[1 : -1]

    # delete old faces
    mesh.delete_face(fkey_0)
    mesh.delete_face(fkey_1)

    # create new faces
    new_face_vertices = [u] + part_1 + [v] + part_0
    fkey = mesh.add_face(new_face_vertices)

    return fkey

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas

    vertices = [[0,0,0],[1,0,0],[1,1,0],[0,1,0],[.5,.5,0]]
    faces = [[0,1,2,4],[0,4,2,3]]
    mesh = Mesh.from_vertices_and_faces(vertices, faces)

    print mesh

    #primitive_insert_edge(mesh, (0,2))
    #primitive_insert_vertex(mesh, (2,3))
    #primitive_remove_edge(mesh, (0,2))
    primitive_delete_vertex(mesh, 4)

    print mesh
    for fkey in mesh.faces():
        print mesh.face_vertices(fkey)
