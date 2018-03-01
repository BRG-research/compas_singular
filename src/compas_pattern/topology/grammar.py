from compas.datastructures.mesh import Mesh

from compas_pattern.datastructures.mesh import face_point
from compas_pattern.datastructures.mesh import insert_vertex_in_face
from compas_pattern.datastructures.mesh import add_vertex_from_vertices
from compas_pattern.datastructures.mesh import insert_vertices_in_halfedge

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
    'vertex_pole',
    'face_pole',
    'edge_pole',
    'face_opening',
    'flat_corner_2',
    'flat_corner_3',
    'flat_corner_33',
    'split_35'
]

def vertex_pole_old(mesh, fkey, pole):

    if len(mesh.face_vertices(fkey)) != 4:
        return None

    a = pole
    b = mesh.face_vertex_descendant(fkey, a)
    c = mesh.face_vertex_descendant(fkey, b)
    d = mesh.face_vertex_descendant(fkey, c)

    mesh.delete_face(fkey)

    fkey_1 = mesh.add_face([a, a, b, c])
    fkey_2 = mesh.add_face([a, a, c, d])

    return fkey_1, fkey_2

def vertex_pole(mesh, fkey, pole):

    if len(mesh.face_vertices(fkey)) != 4:
        return None

    a = pole
    b = mesh.face_vertex_descendant(fkey, a)
    c = mesh.face_vertex_descendant(fkey, b)
    d = mesh.face_vertex_descendant(fkey, c)

    e = add_vertex_from_vertices(mesh, [a, b], [1, 2])
    f = add_vertex_from_vertices(mesh, [b, c], [1, 2])
    g = add_vertex_from_vertices(mesh, [c, d], [2, 1])
    h = add_vertex_from_vertices(mesh, [d, a], [2, 1])

    i = add_vertex_from_vertices(mesh, [a, b, c, d], [1, 1, 2, 1])
    
    mesh.delete_face(fkey)

    fkey_1 = mesh.add_face([a, a, i, h])
    fkey_2 = mesh.add_face([a, a, e, i])
    fkey_3 = mesh.add_face([e, b, f, i])
    fkey_4 = mesh.add_face([h, i, g, d])
    fkey_5 = mesh.add_face([i, f, c, g])

    insert_vertices_in_halfedge(mesh, b, a, [e])
    insert_vertices_in_halfedge(mesh, c, b, [f])
    insert_vertices_in_halfedge(mesh, d, c, [g])
    insert_vertices_in_halfedge(mesh, a, d, [h])

    return fkey_1, fkey_2, fkey_3, fkey_4, fkey_5

def face_pole_old(mesh, fkey):

    if len(mesh.face_vertices(fkey)) != 4:
        return None

    a, b, c, d = mesh.face_vertices(fkey)

    x, y, z = mesh.face_centroid(fkey)
    e = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})

    mesh.delete_face(fkey)

    fkey_1 = mesh.add_face([a, b, e, e])
    fkey_2 = mesh.add_face([b, c, e, e])
    fkey_3 = mesh.add_face([c, d, e, e])
    fkey_4 = mesh.add_face([d, a, e, e])

    return fkey_1, fkey_2, fkey_3, fkey_4

def face_pole(mesh, fkey):

    if len(mesh.face_vertices(fkey)) != 4:
        return None

    a, b, c, d = mesh.face_vertices(fkey)


    e = add_vertex_from_vertices(mesh, [a, b], [2, 1])
    f = add_vertex_from_vertices(mesh, [a, b], [1, 2])
    g = add_vertex_from_vertices(mesh, [b, c], [2, 1])
    h = add_vertex_from_vertices(mesh, [b, c], [1, 2])
    i = add_vertex_from_vertices(mesh, [c, d], [2, 1])
    j = add_vertex_from_vertices(mesh, [c, d], [1, 2])
    k = add_vertex_from_vertices(mesh, [d, a], [2, 1])
    l = add_vertex_from_vertices(mesh, [d, a], [1, 2])

    m = add_vertex_from_vertices(mesh, [a, b, c, d], [2, 1, 1, 1])
    n = add_vertex_from_vertices(mesh, [a, b, c, d], [1, 2, 1, 1])
    o = add_vertex_from_vertices(mesh, [a, b, c, d], [1, 1, 2, 1])
    p = add_vertex_from_vertices(mesh, [a, b, c, d], [1, 1, 1, 2])

    q = add_vertex_from_vertices(mesh, [a, b, c, d], [1, 1, 1, 1])

    mesh.delete_face(fkey)

    fkey_1 = mesh.add_face([a, e, m, l])
    fkey_2 = mesh.add_face([e, f, n, m])
    fkey_3 = mesh.add_face([f, b, g, n])
    fkey_4 = mesh.add_face([l, m, p, k])
    fkey_5 = mesh.add_face([m, q, q, p])
    fkey_6 = mesh.add_face([m, n, q, q])
    fkey_7 = mesh.add_face([q, q, n, o])
    fkey_8 = mesh.add_face([n, g, h, o])
    fkey_9 = mesh.add_face([p, q, q, o])
    fkey_10 = mesh.add_face([k, p, j, d])
    fkey_11 = mesh.add_face([p, o, i, j])
    fkey_12 = mesh.add_face([o, h, c, i])

    insert_vertices_in_halfedge(mesh, b, a, [f, e])
    insert_vertices_in_halfedge(mesh, c, b, [h, g])
    insert_vertices_in_halfedge(mesh, d, c, [j, i])
    insert_vertices_in_halfedge(mesh, a, d, [l, k])

    return fkey_1, fkey_2, fkey_3, fkey_4, fkey_5, fkey_6, fkey_7, fkey_8, fkey_9, fkey_10, fkey_11, fkey_12

def edge_pole_old(mesh, fkey, edge):

    u, v = edge

    if len(mesh.face_vertices(fkey)) != 4:
        return None
    if (u, v) not in mesh.face_halfedges(fkey) and (v, u) not in mesh.face_halfedges(fkey):
        return None
    
    x, y, z = mesh.edge_midpoint(u, v)
    e = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})

    if v in mesh.halfedge[u] and mesh.halfedge[u][v] == fkey:
        a = v
    else:
        a = u

    b = mesh.face_vertex_descendant(fkey, a)
    c = mesh.face_vertex_descendant(fkey, b)
    d = mesh.face_vertex_descendant(fkey, c)

    x, y, z = mesh.edge_point(d, a, t = .75)
    f = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})

    x, y, z = mesh.edge_point(b, c, t = .25)
    g = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})

    x, y, z = mesh.edge_point(b, c, t = .75)
    h = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})

    x, y, z = mesh.edge_point(d, a, t = .25)
    i = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})

    mesh.delete_face(fkey)

    fkey_1 = mesh.add_face([f, a, b, g])
    fkey_2 = mesh.add_face([e, e, f, g])
    fkey_3 = mesh.add_face([e, e, g, h])
    fkey_4 = mesh.add_face([e, e, h, i])
    fkey_5 = mesh.add_face([d, i, h, c])

    if b in mesh.halfedge[c] and mesh.halfedge[c][b] is not None:
        fkey = mesh.halfedge[c][b]
        insert_vertices_in_face(mesh, fkey, c, [h, g])
    if d in mesh.halfedge[a] and mesh.halfedge[a][d] is not None:
        fkey = mesh.halfedge[a][d]
        insert_vertices_in_face(mesh, fkey, a, [f, e, i])

    return fkey_1, fkey_2, fkey_3, fkey_4, fkey_5

def edge_pole(mesh, fkey, edge):

    u, v = edge

    if len(mesh.face_vertices(fkey)) != 4:
        return None
    if (u, v) not in mesh.face_halfedges(fkey) and (v, u) not in mesh.face_halfedges(fkey):
        return None

    if v in mesh.halfedge[u] and mesh.halfedge[u][v] == fkey:
        a = u
    else:
        a = v

    b = mesh.face_vertex_descendant(fkey, a)
    c = mesh.face_vertex_descendant(fkey, b)
    d = mesh.face_vertex_descendant(fkey, c)


    e = add_vertex_from_vertices(mesh, [a, b], [2, 1])
    f = add_vertex_from_vertices(mesh, [a, b], [1, 1])
    g = add_vertex_from_vertices(mesh, [a, b], [1, 2])
    h = add_vertex_from_vertices(mesh, [b, c], [1, 2])
    i = add_vertex_from_vertices(mesh, [c, d], [2, 1])
    j = add_vertex_from_vertices(mesh, [c, d], [1, 2])
    k = add_vertex_from_vertices(mesh, [d, a], [2, 1])

    l = add_vertex_from_vertices(mesh, [a, b, c, d], [1, 1, 1, 2])
    m = add_vertex_from_vertices(mesh, [a, b, c, d], [1, 1, 2, 1])
    
    mesh.delete_face(fkey)

    fkey_1 = mesh.add_face([a, e, l, k])
    fkey_2 = mesh.add_face([e, f, f, l])
    fkey_3 = mesh.add_face([l, f, f, m])
    fkey_4 = mesh.add_face([f, f, g, m])
    fkey_5 = mesh.add_face([g, b, h, m])
    fkey_6 = mesh.add_face([k, l, j, d])
    fkey_7 = mesh.add_face([l, m, i, j])
    fkey_8 = mesh.add_face([m, h, c, i])

    insert_vertices_in_halfedge(mesh, b, a, [g, f, e])
    insert_vertices_in_halfedge(mesh, c, b, [h])
    insert_vertices_in_halfedge(mesh, d, c, [j, i])
    insert_vertices_in_halfedge(mesh, a, d, [k])

    return fkey_1, fkey_2, fkey_3, fkey_4, fkey_5, fkey_6, fkey_7, fkey_8


def face_opening(mesh, fkey):

    if len(mesh.face_vertices(fkey)) != 4:
        return None

    a, b, c, d = mesh.face_vertices(fkey)

    x, y, z = face_point(mesh, [a, b, c, d], [2, 1, 1, 1])
    e = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})

    x, y, z = face_point(mesh, [a, b, c, d], [1, 2, 1, 1])
    f = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})

    x, y, z = face_point(mesh, [a, b, c, d], [1, 1, 2, 1])
    g = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})
    
    x, y, z = face_point(mesh, [a, b, c, d], [1, 1, 1, 2])
    h = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})

    mesh.delete_face(fkey)

    fkey_1 = mesh.add_face([a, b, f, e])
    fkey_2 = mesh.add_face([b, c, g, f])
    fkey_3 = mesh.add_face([c, d, h, g])
    fkey_4 = mesh.add_face([d, a, e, h])

    return fkey_1, fkey_2, fkey_3, fkey_4

def flat_corner_2(mesh, fkey, corner):

    if len(mesh.face_vertices(fkey)) != 4:
        return None
    if corner not in mesh.face_vertices(fkey):
        return None

    a = corner
    b = mesh.face_vertex_descendant(fkey, a)
    c = mesh.face_vertex_descendant(fkey, b)
    d = mesh.face_vertex_descendant(fkey, c)

    x, y, z = mesh.face_centroid(fkey)
    e = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})

    mesh.delete_face(fkey)

    fkey_1 = mesh.add_face([a, b, c, e])
    fkey_2 = mesh.add_face([a, e, c, d])

    return fkey_1, fkey_2

def flat_corner_3(mesh, fkey, corner):

    if len(mesh.face_vertices(fkey)) != 4:
        return None
    if corner not in mesh.face_vertices(fkey):
        return None

    a = corner
    b = mesh.face_vertex_descendant(fkey, a)
    c = mesh.face_vertex_descendant(fkey, b)
    d = mesh.face_vertex_descendant(fkey, c)

    x, y, z = mesh.edge_midpoint(b, c)
    e = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})

    x, y, z = mesh.edge_midpoint(c, d)
    f = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})

    x, y, z = mesh.face_centroid(fkey)
    g = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})

    mesh.delete_face(fkey)

    fkey_1 = mesh.add_face([a, b, e, g])
    fkey_2 = mesh.add_face([e, c, f, g])
    fkey_3 = mesh.add_face([d, a, g, f])

    if b in mesh.halfedge[c] and mesh.halfedge[c][b] is not None:
        fkey = mesh.halfedge[c][b]
        insert_vertex_in_face(mesh, fkey, c, e)
    if c in mesh.halfedge[d] and mesh.halfedge[d][c] is not None:
        fkey = mesh.halfedge[d][c]
        insert_vertex_in_face(mesh, fkey, d, f)

    return fkey_1, fkey_2, fkey_3

def flat_corner_33(mesh, fkey, corner):

    if len(mesh.face_vertices(fkey)) != 4:
        return None
    if corner not in mesh.face_vertices(fkey):
        return None

    a = corner
    b = mesh.face_vertex_descendant(fkey, a)
    c = mesh.face_vertex_descendant(fkey, b)
    d = mesh.face_vertex_descendant(fkey, c)

    x, y, z = mesh.edge_midpoint(d, a)
    e = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})

    x, y, z = mesh.edge_midpoint(a, b)
    f = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})

    x, y, z = mesh.edge_midpoint(b, c)
    g = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})

    x, y, z = mesh.edge_midpoint(c, d)
    h = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})

    x, y, z = face_point(mesh, [a, b, c, d], [1, 1, 1, 2])
    i = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})

    x, y, z = face_point(mesh, [a, b, c, d], [1, 2, 1, 1])
    j = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})

    x, y, z = mesh.face_centroid(fkey)
    k = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})

    mesh.delete_face(fkey)

    fkey_1 = mesh.add_face([a, f, j, k])
    fkey_2 = mesh.add_face([f, b, g, j])
    fkey_3 = mesh.add_face([j, g, c , k])
    fkey_4 = mesh.add_face([a, k, i, e])
    fkey_5 = mesh.add_face([k, c, h, i])
    fkey_6 = mesh.add_face([e, i, h, d])

    u, v = b, a
    if v in mesh.halfedge[u] and mesh.halfedge[u][v] is not None:
        fkey = mesh.halfedge[u][v]
        insert_vertex_in_face(mesh, fkey, u, f)
    u, v = c, b
    if v in mesh.halfedge[u] and mesh.halfedge[u][v] is not None:
        fkey = mesh.halfedge[u][v]
        insert_vertex_in_face(mesh, fkey, u, g)
    u, v = d, c
    if v in mesh.halfedge[u] and mesh.halfedge[u][v] is not None:
        fkey = mesh.halfedge[u][v]
        insert_vertex_in_face(mesh, fkey, u, h)
    u, v = a, d
    if v in mesh.halfedge[u] and mesh.halfedge[u][v] is not None:
        fkey = mesh.halfedge[u][v]
        insert_vertex_in_face(mesh, fkey, u, e)

    return fkey_1, fkey_2, fkey_3, fkey_4, fkey_5, fkey_6

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas

