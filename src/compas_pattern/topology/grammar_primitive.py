from compas.datastructures.mesh import Mesh

from compas_pattern.datastructures.mesh import insert_vertex_in_face

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
    'insert_vertex',
    'split_quad',
    'remove_edge',
]

def insert_vertex(mesh, edge):
    """Insert vertex on an edge.

    face(s):    
    [*, u, v, *] -> [*, u, a, v, *]
    [*, v, u, *] -> [*, v, a, u, *]

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    edge: tuple
        Edge vertex keys.

    Returns
    -------
    a : int, None
        The new vertex.
        None if the edges is not an edge of the mesh.

    Raises
    ------
    -

    """

    u, v = edge

    # check validity of rule
    edges = list(mesh.edges())
    if (u, v) not in edges and (v, u) not in edges:
        return None

    # new vertex
    x, y, z = mesh.edge_midpoint(u, v)
    a = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})

    # update adjacent faces
    if v in mesh.halfedge[u] and mesh.halfedge[u][v] is not None:
        fkey = mesh.halfedge[u][v]
        insert_vertex_in_face(mesh, fkey, u, a)
    if u in mesh.halfedge[v] and mesh.halfedge[v][u] is not None:
        fkey = mesh.halfedge[v][u]
        insert_vertex_in_face(mesh, fkey, v, a)

    return a

def insert_edge(mesh, edge):
    """Insert edge and split face.

    face(s):    
    [*, u, *, v, *] -> [*, u, v *] + [*, v, u, *]

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    fkey: int
        Key of quad face.
    a: int
        Key of quad face vertex.

    Returns
    -------
    c : int, None
        The diagonally opposite vertex.
        None if the quad face is not a quad or if a is not on the face.

    Raises
    ------
    -

    """

    # check validity of rule
    if len(mesh.face_vertices(fkey)) != 4:
        return None
    if a not in mesh.face_vertices(fkey):
        return None

    b = mesh.face_vertex_descendant(fkey, a)
    c = mesh.face_vertex_descendant(fkey, b)
    d = mesh.face_vertex_descendant(fkey, c)
    
    # delete old faces
    mesh.delete_face(fkey)

    # create new faces
    mesh.add_face([a, b, c])
    mesh.add_face([a, c, d])

    return c

def remove_edge(mesh, edge):
    """Remove and edge by merging adjacent faces.

    face(s):    
    [*, u, v, *] + [*, v, u, *] -> [*, u, *, v, *]

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
        None if edge is on boundary.

    Raises
    ------
    -

    """

    u, v = edge

    # check validity of rule
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

