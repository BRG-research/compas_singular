from compas.datastructures.mesh import Mesh

from compas_pattern.datastructures.mesh import add_vertex_to_face

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
    'tri_to_quads',
    'penta_to_quads',
    'hexa_to_quads',
]


def tri_to_quads(mesh, fkey):
    """Convert a tri face into quad faces by centroid split.

    [a, b, c] -> [a, e, g, d], [f, c, d, g] and [f, c, d, g]
    plus adjacent
    [*, b, a, *] -> [*, b, e, a, *]
    [*, c, b, *] -> [*, c, f, b, *]
    [*, a, c, *] -> [*, a, d, c, *]

    Parameters
    ----------
    mesh : Mesh
        A mesh.

    fkey: int
        Key of the face to change.

    Returns
    -------
    mesh : Mesh, None
        The modified mesh.
        None if the face is not a tri.

    Raises
    ------
    -

    """
    
    # return None if the face is not a tri or if the vertex is not on the boundary
    if len(mesh.face_vertices(fkey)) != 3:
        return None

    a, b, c = mesh.face_vertices(fkey)

    # create new vertices
    x, y, z = mesh.edge_midpoint(c, a)
    d = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})
    x, y, z = mesh.edge_midpoint(a, b)
    e = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})
    x, y, z = mesh.edge_midpoint(b, c)
    f = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})
    x, y, z = mesh.face_centroid(fkey)
    g = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})

    # delete old face
    mesh.delete_face(fkey)

    # create new face
    mesh.add_face([a, e, g, d])
    mesh.add_face([f, c, d, g])
    mesh.add_face([e, b, f, g])

    # update adjacent face
    # [*, b, a, *] -> [*, b, e, a, *]
    if a in mesh.halfedge[b] and mesh.halfedge[b][a] is not None:
        fkey_1 = mesh.halfedge[b][a]
        add_vertex_to_face(mesh, fkey_1, b, e)
    # [*, c, b, *] -> [*, c, f, b, *]
    if b in mesh.halfedge[c] and mesh.halfedge[c][b] is not None:
        fkey_2 = mesh.halfedge[c][b]
        add_vertex_to_face(mesh, fkey_2, c, f)
    # [*, a, c, *] -> [*, a, d, c, *]
    if c in mesh.halfedge[a] and mesh.halfedge[a][c] is not None:
        fkey_3 = mesh.halfedge[a][c]
        add_vertex_to_face(mesh, fkey_3, a, d)

    return f

def penta_to_quads(mesh, fkey, vkey):
    """Convert a penta face into two quads with a new edge from a vertex to the opposite edge midpoint.
    
    [a, b, c, d, e] -> [a, b, f, e] + [c, d, e, f]
    plus update of one neighbour face:
    [*, c, b, *] -> [*, c, f, b, *]

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    fkey: int
        Key of quad face.
    vkey: int
        Key of the first vertex of the new edge.

    Returns
    -------
    f : int, None
        The key of the new vertex of the new edge.
        None if the penta face is not a penta or if the vertex is not adjacent to the face.

    Raises
    ------
    -

    """

    # check validity of rule
    if len(mesh.face_vertices(fkey)) != 5:
        return None
    if vkey not in mesh.face_vertices(fkey):
        return None

    e = vkey
    a = mesh.face_vertex_descendant(fkey, e)
    b = mesh.face_vertex_descendant(fkey, a)
    c = mesh.face_vertex_descendant(fkey, b)
    d = mesh.face_vertex_descendant(fkey, c)

    # create new vertex
    x, y, z = mesh.edge_midpoint(b, c)
    f = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})

    # delete old face
    mesh.delete_face(fkey)

    # create new face
    mesh.add_face([a, b, f, e])
    mesh.add_face([c, d, e, f])

    # update adjacent face
    # [*, c, b, *] -> [*, c, f, b, *]
    if b in mesh.halfedge[c] and mesh.halfedge[c][b] is not None:
        fkey_1 = mesh.halfedge[c][b]
        add_vertex_to_face(mesh, fkey_1, c, f)

    return f

def hexa_to_quads(mesh, fkey, vkey):
    """Convert an hexa face into two quads with a new edge from a vertex to the opposite vertex.
    
    [a, b, f, c, d, e] -> [a, b, f, e] + [c, d, e, f]
    plus update of one neighbour face:
    [*, c, b, *] -> [*, c, f, b, *]

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    fkey: int
        Key of quad face.
    vkey: int
        Key of the first vertex of the new edge.

    Returns
    -------
    f : int, None
        The key of the opposite vertex of the new edge.
        None if the hex face is not a penta or if the vertex is not adjacent to the face.

    Raises
    ------
    -

    """

    # check validity of rule
    if len(mesh.face_vertices(fkey)) != 6:
        return None
    if vkey not in mesh.face_vertices(fkey):
        return None

    e = vkey
    a = mesh.face_vertex_descendant(fkey, e)
    b = mesh.face_vertex_descendant(fkey, a)
    f = mesh.face_vertex_descendant(fkey, b)
    c = mesh.face_vertex_descendant(fkey, f)
    d = mesh.face_vertex_descendant(fkey, c)

    # delete old face
    mesh.delete_face(fkey)

    # create new face
    mesh.add_face([a, b, f, e])
    mesh.add_face([c, d, e, f])

    # update adjacent face
    # [*, c, b, *] -> [*, c, f, b, *]
    if b in mesh.halfedge[c] and mesh.halfedge[c][b] is not None:
        fkey_1 = mesh.halfedge[c][b]
        add_vertex_to_face(mesh, fkey_1, c, f)

    return f

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas

