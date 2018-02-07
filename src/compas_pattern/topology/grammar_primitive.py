from compas.datastructures.mesh import Mesh

from compas_pattern.datastructures.mesh import add_vertex_to_face

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
    'primitive_1',
    'primitive_2',
    'primitive_3',
    'primitive_4',
    'primitive_5',
]

def primitive_1(mesh, fkey, b, d):
    """One triangle into a quad by adding an edge midpoint.

    face(s):    
    [a, b, d] -> [a, b, c, d]

    neighbour(s):
    [*, d, b, *] -> [*, d, c, b, *]

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    fkey: int
        Key of tri face.
    b: int
        Key of face vertex.
    d: int
        Key of face vertex.

    Returns
    -------
    c : int, None
        The new vertex.
        None if the quad face is not a quad or if (b, d) does not point to the face.

    Raises
    ------
    -

    """

    # check validity of rule
    if len(mesh.face_vertices(fkey)) != 3:
        return None
    if d not in mesh.halfedge[b] or mesh.halfedge[b][d] is None or mesh.halfedge[b][d] != fkey:
        return None

    a = mesh.face_vertex_descendant(fkey, d)

    # new vertices
    x, y, z = mesh.edge_midpoint(b, d)
    c = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})

    # new face vertices
    face_vertices = mesh.face_vertices(fkey)[:]
    i = face_vertices.index(d)
    face_vertices.insert(i, c)

    # delete old faces
    mesh.delete_face(fkey)

    # create new faces
    mesh.add_face([a, b, c, d], fkey)

    # update adjacent faces
    if b in mesh.halfedge[d] and mesh.halfedge[d][b] is not None:
        fkey_1 = mesh.halfedge[d][b]
        add_vertex_to_face(mesh, fkey_1, d, c)

    return c

def primitive_2(mesh, fkey, a):
    """One quad into two triangles by adding a diagonal edge from vertex.

    face(s):    
    [a, b, c, d] -> [a, b, c] + [a, c, d]

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    fkey: int
        Key of tri face.
    a: int
        Key of face vertex.

    Returns
    -------
    c : int, None
        The diaognally opposite vertex.
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

def primitive_3(mesh, a, c):
    """Two triangles into a quad by removing an edge.

    face(s):    
    [a, b, c] + [a, c, d] -> [a, b, c, d]

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    a: int
        Key of vertex.
    c: int
        Key of vertex.

    Returns
    -------
    fkey : int, None
        The new face.
        None if (a, c) is not and edge or if not adjacent to triangles.

    Raises
    ------
    -

    """

    # check validity of rule
    if c not in mesh.halfedge[a] or a not in mesh.halfedge[c]:
        return None
    if len(mesh.face_vertices(mesh.halfedge[a][c])) != 3 or len(mesh.face_vertices(mesh.halfedge[c][a])) != 3:
        return None

    fkey_0 = mesh.halfedge[c][a]
    fkey_1 = mesh.halfedge[a][c]

    b = mesh.face_vertex_descendant(fkey_0, a)
    d = mesh.face_vertex_descendant(fkey_1, c)

    # delete old faces
    mesh.delete_face(fkey_0)
    mesh.delete_face(fkey_1)

    # create new faces
    fkey = mesh.add_face([a, b, c, d])

    return fkey

def primitive_4(mesh, fkey, a, b, c):
    """One quad into a quad and a triangle by adding an edge between edge midpoint and vertex.

    face(s):    
    [a, b, c, d] -> [a, e, c, d] + [e, b, c]

    neighbour(s):
    [*, b, a, *] -> [*, b, e, a, *]

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    fkey: int
        Key of quad face.
    b: int
        Key of face vertex.

    Returns
    -------
    e : int, None
        The new vertex.
        None if the quad face is not a quad or if [a, b, c] nor [c, b, a] is a subset of the face vertices.

    Raises
    ------
    -

    """

    # check validity of rule
    if len(mesh.face_vertices(fkey)) != 4:
        return None
    if (mesh.face_vertex_descendant(fkey, a) != b or mesh.face_vertex_descendant(fkey, b) != c) and (mesh.face_vertex_ancestor(fkey, a) != b or mesh.face_vertex_ancestor(fkey, b) != c):
        return None

    # if statement because of cycle
    flip = False
    if mesh.face_vertex_descendant(fkey, a) != b:
        flip = True

    if not flip:
        d = mesh.face_vertex_descendant(fkey, c)
    else:
        d = mesh.face_vertex_ancestor(fkey, c)
    
    # new vertices
    x, y, z = mesh.edge_midpoint(a, b)
    e = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})

    # delete old faces
    mesh.delete_face(fkey)

    # create new faces
    if not flip:
        mesh.add_face([a, e, c, d], fkey)
        mesh.add_face([e, b, c])
    else:
        mesh.add_face(list(reversed([a, e, c, d])), fkey)
        mesh.add_face(list(reversed([e, b, c])))

    # update adjacent faces
    if not flip:
        if a in mesh.halfedge[b] and mesh.halfedge[b][a] is not None:
            fkey_1 = mesh.halfedge[b][a]
            add_vertex_to_face(mesh, fkey_1, b, e)
    else:
        if b in mesh.halfedge[a] and mesh.halfedge[a][b] is not None:
            fkey_1 = mesh.halfedge[a][b]
            add_vertex_to_face(mesh, fkey_1, a, e)

    return e

def primitive_5(mesh, fkey_quad, fkey_tri, e):
    """One quad and one triangle into two quads by moving an edge from a vertex to an edge midpoint.

    face(s):
    [a, e, c, d] + [e, b, c] -> [a, e, f, d] + [e, b, c, f]

    neighbour(s):
    [*, d, c, *] -> [*, d, f, c, *]

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    e: int
        Key of vertex.
    c: int
        Key of vertex.

    Returns
    -------
    f : int, None
        The new vertex.
        None if fkey_quad not a quad face or fkey_tri not a tri face or e not on fkey_quad or e not on fkey_tri.

    Raises
    ------
    -

    """

    # check validity of rule
    if len(mesh.face_vertices(fkey_quad)) != 4:
            return None
    if len(mesh.face_vertices(fkey_tri)) != 3:
            return None
    if e not in mesh.face_vertices(fkey_quad):
        return None
    if e not in mesh.face_vertices(fkey_tri):
        return None

    opp = mesh.face_vertex_descendant(fkey_quad, e)

    if opp in mesh.face_vertices(fkey_tri):
        c = opp
        d = mesh.face_vertex_descendant(fkey_quad, c)
        a = mesh.face_vertex_descendant(fkey_quad, d)
        b = mesh.face_vertex_descendant(fkey_tri, e)
    else:
        a = opp
        d = mesh.face_vertex_descendant(fkey_quad, a)
        c = mesh.face_vertex_descendant(fkey_quad, d)
        b = mesh.face_vertex_descendant(fkey_tri, c)

    # new vertices
    x, y, z = mesh.edge_midpoint(c, d)
    f = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})

    # delete old faces
    mesh.delete_face(fkey_quad)
    mesh.delete_face(fkey_tri)

    # create new faces
    mesh.add_face([a, e, f, d], fkey_quad)
    mesh.add_face([e, b, c, f], fkey_tri)

    # update adjacent faces
    if c in mesh.halfedge[d] and mesh.halfedge[d][c] is not None:
        fkey = mesh.halfedge[d][c]
        add_vertex_to_face(mesh, fkey, d, f)

    return f

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
