from compas.datastructures.mesh import Mesh

from compas.topology import mesh_flip_cycles

from compas_pattern.datastructures.mesh import add_vertex_to_face

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
    'quad_quad_1',
    'quad_quad_2',
    'quad_quad_3',
    'quad_tri_1',
    'tri_quad_1',
    'penta_quad_1',
    'hexa_quad_1',
    'poly_poly_1',
    'mix_quad_1',
    'quad_mix_1',
]

# naming convention: input_output_number
# ex: mix_quad_1: rule number one with mixed face type input and quad face type output

def quad_quad_1(mesh, fkey, halfedge):
    """One quad to two quads with new edge from edge midpoint to opposite edge midpoint.
    
    [a, b, c, d] -> [a, b, f, e] + [c, d, e, f]

    [*, c, b, *] -> [*, c, f, b, *]
    [*, a, d, *] -> [*, a, e, d, *]

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    fkey: int
        Key of quad face.
    halfedge: tuple
        One of the two face halfedges to split (ukey, vkey)

    Returns
    -------
    (e, f) : tuple, None
        The new edge.
        None if the quad face is not a quad or if the halfedge does not point to the face.

    Raises
    ------
    -

    """

    ukey, vkey = halfedge

    # check validity of rule
    if len(mesh.face_vertices(fkey)) != 4:
        return None
    if vkey not in mesh.halfedge[ukey] or mesh.halfedge[ukey][vkey] != fkey :
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

    # delete old face
    mesh.delete_face(fkey)

    # create new faces
    # [a, b, c, d] -> [a, b, f, e] + [c, d, e, f]
    mesh.add_face([a, b, f, e])
    mesh.add_face([c, d, e, f])

    # update adjacent faces
    # [*, c, b, *] -> [*, c, f, b, *]
    if b in mesh.halfedge[c] and mesh.halfedge[c][b] is not None:
        fkey_1 = mesh.halfedge[c][b]
        add_vertex_to_face(mesh, fkey_1, c, f)
    # [*, a, d, *] -> [*, a, e, d, *]
    if d in mesh.halfedge[a] and mesh.halfedge[a][d] is not None:
        fkey_2 = mesh.halfedge[a][d]
        add_vertex_to_face(mesh, fkey_2, a, e)


    return (e, f)

def quad_quad_2(mesh, fkey, vkey):
    """One quad to two quads with two new edges along the diagonal corresponding.
    
    [a, b, c, d] -> [a, b, c, e] + [a, e, c, d]

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    fkey: int
        Key of quad face.
    vkey: int
        Key of one of the vertices corresponding to the diagonal split.

    Returns
    -------
    e : int, None
        The key of the new vertex at the face centroid.
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
    # [a, b, c, d] -> [a, b, c, e] + [a, e, c, d]
    mesh.add_face([a, b, c, e])
    mesh.add_face([a, e, c, d])

    return e

def quad_quad_3(mesh, fkey, vkey):
    """One quad tot three quads with three edges from the face centroid to one one vertex and two edge midpoints.

    [a, b, c, d] -> [a, b, e, g] + [e, c, f, g] + [a, g, f, d]

    [*, c, b, *] -> [*, c, e, b, *]
    [*, d, c, *] -> [*, d, f, c, *]

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    fkey: int
        Key of quad face.
    vkey: int
        Key of a vertex of quad face at the extremity of one of the three new edges.

    Returns
    -------
    g : int, None
        The key of the new centroid vertex.
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

    # itemise vertices
    a = vkey
    b = mesh.face_vertex_descendant(fkey, a)
    c = mesh.face_vertex_descendant(fkey, b)
    d = mesh.face_vertex_descendant(fkey, c)

    # create new vertices
    x, y, z = mesh.edge_midpoint(b, c)
    e = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})
    x, y, z = mesh.edge_midpoint(c, d)
    f = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})
    x, y, z = mesh.face_centroid(fkey)
    g = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})

    # delete old face
    mesh.delete_face(fkey)

    # create new faces
    # [a, b, c, d] -> [a, b, e, g] + [e, c, f, g] + [a, g, f, d]
    mesh.add_face([a, b, e, g])
    mesh.add_face([e, c, f, g])
    mesh.add_face([a, g, f, d])

    # update adjacent faces
    # [*, c, b, *] -> [*, c, e, b, *]
    if b in mesh.halfedge[c] and mesh.halfedge[c][b] is not None:
        fkey_1 = mesh.halfedge[c][b]
        add_vertex_to_face(mesh, fkey_1, c, e)
    # [*, d, c, *] -> [*, d, f, c, *]
    if c in mesh.halfedge[d] and mesh.halfedge[d][c] is not None:
        fkey_2 = mesh.halfedge[d][c]
        add_vertex_to_face(mesh, fkey_2, d, f)

    return g

def quad_tri_1(mesh, fkey, vkey):
    """One quad to two tri with new edge along diagonal.
    
    [a, b, c, d] -> [a, b, c] + [a, c, d]

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    fkey: int
        Key of quad face.
    vkey: int
        Key of a vertex of quad face at one extremity of the new edge.

    Returns
    -------
    c : int, None
        The key of the second vertex of the new edge.
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

def tri_quad_1(mesh, fkey):
    """One tri to three quads split with three new edges from the face centroid to the edge midpoints.

    [a, b, c] -> [a, e, g, d], [f, c, d, g] and [f, c, d, g]

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
    g : int, None
        The key of the new vertex at the face centroid.
        None if the tri face is not a tri.

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

    # create new faces
    # [a, b, c] -> [a, e, g, d], [f, c, d, g] and [f, c, d, g]
    mesh.add_face([a, e, g, d])
    mesh.add_face([f, c, d, g])
    mesh.add_face([e, b, f, g])

    # update adjacent faces
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

def penta_quad_1(mesh, fkey, vkey):
    """One penta to two quads with new edge from a vertex to the opposite edge midpoint.
    
    [a, b, c, d, e] -> [a, b, f, e] + [c, d, e, f]

    [*, c, b, *] -> [*, c, f, b, *]

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    fkey: int
        Key of quad face.
    vkey: int
        Key of the pre-existing vertex of the new edge.

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

    # create new faces
    # [a, b, c, d, e] -> [a, b, f, e] + [c, d, e, f]
    mesh.add_face([a, b, f, e])
    mesh.add_face([c, d, e, f])

    # update adjacent face
    # [*, c, b, *] -> [*, c, f, b, *]
    if b in mesh.halfedge[c] and mesh.halfedge[c][b] is not None:
        fkey_1 = mesh.halfedge[c][b]
        add_vertex_to_face(mesh, fkey_1, c, f)

    return f

def hexa_quad_1(mesh, fkey, vkey):
    """One hexa to two quads with new edge from a vertex to opposite vertex.
    
    [a, b, f, c, d, e] -> [a, b, f, e] + [c, d, e, f]

    [*, c, b, *] -> [*, c, f, b, *]

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    fkey: int
        Key of quad face.
    vkey: int
        Key of one of the vertices of the new edge.

    Returns
    -------
    f : int, None
        The key of the other vertex of the new edge.
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

    # create new faces
    # [a, b, f, c, d, e] -> [a, b, f, e] + [c, d, e, f]
    mesh.add_face([a, b, f, e])
    mesh.add_face([c, d, e, f])

    return f

def poly_poly_1(mesh, fkey, vkey):
    """One N-gon to a quad and a N-1-gon with a new edge from a vertex to point on opposite edge.
    
    [*, a, b, c, d] -> [c, d, e, f] + [*, a, b, f]

    [*, c, b, *] -> [*, c, f, b, *]

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    fkey: int
        Key of quad face.
    vkey: int
        Key of one of the vertices of the new edge.

    Returns
    -------
    f : int, None
        The key of the new vertex of the new edge.
        None if the vertex is not adjacent to the face.

    Raises
    ------
    -

    """

    # check validity of rule
    if vkey not in mesh.face_vertices(fkey):
        return None

    e = vkey
    d = mesh.face_vertex_ancestor(fkey, e)
    c = mesh.face_vertex_ancestor(fkey, d)
    b = mesh.face_vertex_ancestor(fkey, c)
    a = mesh.face_vertex_ancestor(fkey, b)
    
    face_vertices = mesh.face_vertices(fkey)[:]

    # create new vertex
    idx = face_vertices.index(e)
    length_ea = 0
    count = len(face_vertices)
    while count > 0:
        count -= 1
        length_ea += mesh.edge_length(face_vertices[idx], face_vertices[idx + 1 - len(face_vertices)])
        if face_vertices[idx + 1 - len(face_vertices)] == a:
            break
    length_ed = mesh.edge_length(e, d)
    if length_ea + length_ed == 0:
        t = .5
    else:
        t = length_ea / (length_ea + length_ed)
    x, y, z = mesh.edge_point(b, c, t = t)
    f = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})

    face_vertices.remove(c)
    face_vertices.remove(d)
    idx = face_vertices.index(e)
    face_vertices.insert(idx, f)

    # delete old face
    mesh.delete_face(fkey)

    # create new faces
    # [*, a, b, c, d] -> [c, d, e, f] + [*, a, b, f]
    mesh.add_face(face_vertices, fkey)
    mesh.add_face([c, d, e, f])

    # update adjacent face
    # [*, c, b, *] -> [*, c, f, b, *]
    if b in mesh.halfedge[c] and mesh.halfedge[c][b] is not None:
        fkey_1 = mesh.halfedge[c][b]
        add_vertex_to_face(mesh, fkey_1, c, f)

    return f

def mix_quad_1(mesh, fkey_tri, fkey_quad, vkey):
    """One quad and one tri to two quads by moving one extremity of the shared edge to a new vertex on an adjacent edge midpoint of the quad.
    
    [a, b, c] + [c, d, e, a] -> [a, b, c, f] + [c, d, e, f]

    [*, a, e, *] -> [*, a, f, e, *]

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    fkey_tri: int
        Key of tri face.
    fkey_quad: int
        Key of quad face adjacent to tri face.
    vkey: int
        Key of vertex adjacent to tri face and quad face.

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
    # [a, b, c] + [c, d, e, a] -> [a, b, c, f] + [c, d, e, f]
    mesh.add_face([a, b, c, f], fkey_tri)
    mesh.add_face([c, d, e, f], fkey_quad)

    # update adjacent face
    # [*, a, e, *] -> [*, a, f, e, *]
    if e in mesh.halfedge[a] and mesh.halfedge[a][e] is not None:
        fkey_1 = mesh.halfedge[a][e]
        add_vertex_to_face(mesh, fkey_1, a, f)

    # reflip cycles in faces
    if flip:
        mesh_flip_cycles(mesh)

    return f

def quad_mix_1(mesh, fkey, vkey, ukey):
    """One quad to a quad and a tri with a new edge from a vertex to the edge midpoint opposite from the two vertices.
    
    [a, b, c, d] -> [a, b, e] + [a, e, c, d]

    [*, c, b, *] -> [*, c, e, b, *]

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    fkey: int
        Key of quad face.
    vkey: int
        Key of the initial vertex of the new edge.
    ukey: int
        Key of adjacent vertex of the edge opposite to the new vertex.

    Returns
    -------
    e : int, None
        The key of the new vertex of the new edge.
        None if the quad face is not a quad and if the two vertices are not an edge of the face.

    Raises
    ------
    -

    """

    # check validity of rule
    if len(mesh.face_vertices(fkey)) != 4:
        return None
    if (vkey not in mesh.halfedge[ukey] or mesh.halfedge[ukey][vkey] != fkey) and (ukey not in mesh.halfedge[vkey] or mesh.halfedge[vkey][ukey] != fkey):
        return None

    # flip cyles in faces dpeending on position of vkey
    flip = False
    if ukey in mesh.halfedge[vkey] and mesh.halfedge[vkey][ukey] == fkey:
        flip = True
        mesh_flip_cycles(mesh)

    d = ukey
    a = vkey
    b = mesh.face_vertex_descendant(fkey, a)
    c = mesh.face_vertex_descendant(fkey, b)

    # create new vertex
    x, y, z = mesh.edge_midpoint(b, c)
    e = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})

    # delete old face
    mesh.delete_face(fkey)

    # create new faces
    # [a, b, c, d] -> [a, b, e] + [a, e, c, d]
    mesh.add_face([a, e, c, d], fkey)
    mesh.add_face([a, b, e])

    # update adjacent face
    # [*, c, b, *] -> [*, c, e, b, *]
    if b in mesh.halfedge[c] and mesh.halfedge[c][b] is not None:
        fkey_1 = mesh.halfedge[c][b]
        add_vertex_to_face(mesh, fkey_1, c, e)

    # reflip cycles in faces
    if flip:
        mesh_flip_cycles(mesh)

    return e

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas

    vertices = [[0,0,0], [0,0,0], [0,0,0], [0,0,0], [0,0,0], [0,0,0], [0,0,0], [0,0,0], [0,0,0]]
    face_vertices = [[0, 1, 2, 3, 4, 5, 6], [1, 7, 8, 2]]

    mesh = Mesh.from_vertices_and_faces(vertices, face_vertices)

    poly_poly_1(mesh, 0, 4)
    for fkey in mesh.faces():
        print mesh.face_vertices(fkey)
