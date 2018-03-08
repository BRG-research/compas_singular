from compas.datastructures.mesh import Mesh

from compas_pattern.datastructures.mesh import insert_vertices_in_halfedge
from compas_pattern.datastructures.mesh import insert_vertex_in_face
from compas_pattern.datastructures.mesh import add_vertex_from_vertices

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
    'primitive_insert_vertex',
    'primitive_insert_edge',
    'primitive_remove_edge',
]

def primitive_insert_vertex(mesh, edge):
    """Insert a vertex on an edge.

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    edge: tuple
        Edge vertex keys.

    Returns
    -------
    x : int, None
        The new vertex.
        None if not an edge of the mesh.

    Raises
    ------
    -

    """

    u, v = edge

    # check validity
    if (u, v) not in list(mesh.edges()) and (v, u) not in list(mesh.edges()):
        return None

    # new vertex
    x = add_vertex_from_vertices(mesh, [u, v], [1, 1])

    # update adjacent faces
    insert_vertices_in_halfedge(mesh, u, v, [x])
    insert_vertices_in_halfedge(mesh, v, u, [x])

    return x

def primitive_insert_edge(mesh, vertices):
    """Insert an edge by splitting a face.

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    vertices: tuple
        Keys of two non-adjacent vertices from the same face.

    Returns
    -------
    (u, v): tuple, None
        The new edge.
        None if not two non-adjacent vertices from the same face.

    Raises
    ------
    -

    """

    # check validity

    # two vertices
    if len(vertices) != 2:
        return None
    u, v = vertices

    # vertices of the mesh
    mesh_vertices = list(mesh.vertices())
    if u not in mesh_vertices or v not in mesh_vertices:
        return None
    
    # non-adjacent vertices
    mesh_edges = list(mesh.edges()) 
    if (u, v) in mesh_edges or (v, u) in mesh_edges:
        return None

    # one shared face
    u_faces = mesh.vertex_faces(u)
    v_faces = mesh.vertex_faces(v)
    fkeys = [fkey for fkey in u_faces if fkey in v_faces]
    if len(fkeys) != 1:
        return None
    fkey = fkeys[0]

    # split face vertices
    face_vertices = mesh.face_vertices(fkey)
    u_idx = face_vertices.index(u)
    v_idx = face_vertices.index(v)
    min_idx = min(u_idx, v_idx)
    max_idx = max(u_idx, v_idx)
    face_vertices_1 = face_vertices[min_idx : max_idx + 1]
    face_vertices_2 = face_vertices[max_idx :] + face_vertices[: min_idx + 1 - len(face_vertices)]
    print face_vertices_1
    print face_vertices_2
    # delete old faces
    mesh.delete_face(fkey)

    # create new faces
    mesh.add_face(face_vertices_1)
    mesh.add_face(face_vertices_2)

    return (u, v)

def primitive_remove_edge(mesh, edge):
    """Remove and edge by merging two faces.

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    edge: tuple
        Edge vertex keys.

    Returns
    -------
    fkey : int, None
        The new face.
        None if not a non-boundary edge.

    Raises
    ------
    -

    """

    u, v = edge

    # check validity

    # is edge
    if (u, v) not in list(mesh.edges()) and (v, u) not in list(mesh.edges()):
        return None

    # is non-boundary
    if mesh.is_edge_on_boundary(u, v):
        return None

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

    vertices = [[0,0,0],[1,0,0],[1,1,0],[0,1,0]]
    faces = [[0,1,2,3]]
    mesh = Mesh.from_vertices_and_faces(vertices, faces)

    print mesh

    primitive_insert_edge(mesh, (0,2))
    #primitive_insert_vertex(mesh, (2,3))
    #primitive_remove_edge(mesh, (0,2))

    print mesh
    for fkey in mesh.faces():
        print mesh.face_vertices(fkey)
