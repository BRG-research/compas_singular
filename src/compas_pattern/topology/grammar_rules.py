from compas.datastructures.mesh import Mesh

from compas.topology import mesh_flip_cycles

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
    'tri_quad_to_quad_quad',
    'quad_to_two_quads_diagonal',
    'quad_to_two_quads',
    'quad_to_tris',
]


def tri_quad_to_quad_quad(mesh, fkey_tri, fkey_quad, vkey):
    """Convert a tri face adjacent to a quad face into two quad faces with same keys by adding a new vertex.
    
    [a, b, c] + [c, d, e, a] -> [a, b, c, f] + [c, d, e, f]

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    fkey_tri: int
        Key of tri face.
    fkey_quad: int
        Key of quad face adjacent to tri face.
    vkey: int
        Key of vertex in adjacent to tri face and quad face.

    Returns
    -------
    f : int, None
        The key of the new vertex.
        None if the tri face is not a tri, if the quad face is not a quad or if not adjacent to the tri face or if the vertex is not adjacent to both faces.

    Raises
    ------
    -

    """

    # check validity of rule
    if len(mesh.face_vertices(fkey_tri)) != 3:
        return None
    if len(mesh.face_vertices(fkey_quad)) != 4:
        return None
    if fkey_quad not in mesh.face_neighbours(fkey_tri):
        return None
    if vkey not in mesh.face_vertices(fkey_tri) or vkey not in mesh.face_vertices(fkey_quad):
        return None

    # flip cyles in faces dpeending on position of vkey
    flip = False
    u = vkey
    v = mesh.face_vertex_descendant(fkey_tri, u)
    if mesh.halfedge[v][u] == fkey_quad:
        flip = True
        mesh_flip_cycles(mesh)

    # itemise vertices
    a = vkey
    b = mesh.face_vertex_descendant(fkey_tri, a)
    c = mesh.face_vertex_descendant(fkey_tri, b)
    d = mesh.face_vertex_descendant(fkey_quad, c)
    e = mesh.face_vertex_descendant(fkey_quad, d)

    # create new vertex
    x, y, z = mesh.edge_midpoint(e, a)
    f = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})

    # delete old faces
    mesh.delete_face(fkey_tri)
    mesh.delete_face(fkey_quad)

    # create new faces
    mesh.add_face([a, b, c, f], fkey_tri)
    mesh.add_face([c, d, e, f], fkey_quad)

    # reflip cycles in faces
    if flip:
        mesh_flip_cycles(mesh)

    return f


def quad_to_two_quads_diagonal(mesh, fkey, vkey):
    """Convert a quad face adjacent into two quads with a two-valency vertex along the diagonal matching the vertex key input.
    
    [a, b, c, d] -> [a, b, c, e] + [a, e, c, d]

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    fkey: int
        Key of quad face.
    vkey: int
        Key of one of the vertices matching the diagonal split.

    Returns
    -------
    e : int, None
        The key of the new vertex.
        None if the quad face is not a quad or if the vertex is not adjacent to the face.

    Raises
    ------
    -

    """

    # check validity of rule
    if len(mesh.face_vertices(fkey)) != 4:
        return None
    if vkey not in mesh.face_vertices(fkey):
        return None

    a = vkey
    b = mesh.face_vertex_descendant(fkey, a)
    c = mesh.face_vertex_descendant(fkey, b)
    d = mesh.face_vertex_descendant(fkey, c)

    # create new vertex
    x, y, z = mesh.face_centroid(fkey)
    e = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})

    # delete old faces
    mesh.delete_face(fkey)

    # create new faces
    mesh.add_face([a, b, c, e])
    mesh.add_face([a, e, c, d])

    return e

def quad_to_two_quads(mesh, fkey, ukey, vkey):
    """Convert a quad face into two quads with a new edge orthogonal to one of its edges.
    
    [a, b, c, d] -> [a, b, f, e] + [c, d, e, f]
    plus update of two neighbour faces:
    [*, c, b, *] -> [*, c, f, b, *]
    [*, a, d, *] -> [*, a, e, d, *]

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    fkey: int
        Key of quad face.
    ukey: int
        Key of the first vertex of the edge.
    vkey: int
        Key of the second vertex of the edge.

    Returns
    -------
    (e, f) : tuple, None
        The keys of the vertices of the new edge.
        None if the quad face is not a quad or if the vertices are not an edge of the face.

    Raises
    ------
    -

    """

    # check validity of rule
    if len(mesh.face_vertices(fkey)) != 4:
        return None
    if mesh.halfedge[ukey][vkey] != fkey and mesh.halfedge[vkey][ukey] != fkey:
        return None

    if mesh.halfedge[ukey][vkey] == fkey:
        d = ukey
        a = vkey
    else:
        d = vkey
        a = ukey
    b = mesh.face_vertex_descendant(fkey, a)
    c = mesh.face_vertex_descendant(fkey, b)

    # create new vertices
    x, y, z = mesh.edge_midpoint(d, a)
    e = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})
    x, y, z = mesh.edge_midpoint(b, c)
    f = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})

    # delete old faces
    mesh.delete_face(fkey)

    # create new faces
    mesh.add_face([a, b, f, e])
    mesh.add_face([c, d, e, f])

    # update adjacent faces
    # [*, c, b, *] -> [*, c, f, b, *]
    if b in mesh.halfedge[c] and mesh.halfedge[c][b] is not None:
        fkey_1 = mesh.halfedge[c][b]
        face_vertices_1 = mesh.face_vertices(fkey_1)[:]
        idx = face_vertices_1.index(b)
        face_vertices_1.insert(idx, f)
        mesh.delete_face(fkey_1)
        mesh.add_face(face_vertices_1, fkey = fkey_1)
    # [*, a, d, *] -> [*, a, e, d, *]
    if d in mesh.halfedge[a] and mesh.halfedge[a][d] is not None:
        fkey_2 = mesh.halfedge[a][d]
        face_vertices_2 = mesh.face_vertices(fkey_2)[:]
        idx = face_vertices_2.index(d)
        face_vertices_2.insert(idx, e)
        mesh.delete_face(fkey_2)
        mesh.add_face(face_vertices_2, fkey = fkey_2)


    return (e, f)

def quad_to_tris(mesh, fkey, vkey):
    """Convert a quad face into two tri faces with diagonal split starting from the vertex key.
    
    [a, b, c, d] -> [a, b, c] + [a, c, d]

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    fkey: int
        Key of quad face.
    vkey: int
        Key of a vertex of quad face.

    Returns
    -------
    c : int, None
        The key of the second vertex of the new diagonal edge.
        None if the tri face is not a quad or if the vertex is not part of the face vertices.

    Raises
    ------
    -

    """

    # check validity of rule
    if len(mesh.face_vertices(fkey)) != 4:
        return None
    if vkey not in mesh.face_vertices(fkey):
        return None

    # itemise vertices
    a = vkey
    b = mesh.face_vertex_descendant(fkey, a)
    c = mesh.face_vertex_descendant(fkey, b)
    d = mesh.face_vertex_descendant(fkey, c)

    # delete old face
    mesh.delete_face(fkey)

    # create new faces
    mesh.add_face([a, b, c])
    mesh.add_face([a, c, d])

    return c

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas

