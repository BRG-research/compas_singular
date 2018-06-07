from compas.datastructures.mesh import Mesh

from compas_pattern.datastructures.pseudo_quad_mesh import PseudoQuadMesh

from compas_pattern.datastructures.mesh import face_point
from compas_pattern.datastructures.mesh import insert_vertex_in_face
from compas_pattern.datastructures.mesh import add_vertex_from_vertices
from compas_pattern.datastructures.mesh import insert_vertices_in_halfedge

from compas_pattern.topology.polyline_extraction import mesh_boundaries

from compas_pattern.topology.global_propagation import face_propagation

from compas.geometry import distance_point_point
from compas.geometry import subtract_vectors
from compas.geometry import dot_vectors

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
    'vertex_pole',
    'face_pole',
    'edge_pole',
    'face_opening',
    'close_opening',
    'flat_corner_2',
    'flat_corner_3',
    'flat_corner_33',
    'split_35',
    'split_35_diag',
    'split_26',
    'simple_split',
    'double_split',
    'insert_pole',
    'insert_partial_pole',
    'pseudo_quad_split',
    'singular_boundary_1',
    'remove_tri',
    'rotate_vertex',
    'clear_faces',
    'add_handle',
    'close_handle',
]

def vertex_pole(mesh, fkey, pole):

    if len(mesh.face_vertices(fkey)) != 4:
        return None
    if pole not in mesh.face_vertices(fkey):
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

    e = add_vertex_from_vertices(mesh, [a, b, c, d], [2, 1, 1, 1])
    f = add_vertex_from_vertices(mesh, [a, b, c, d], [1, 2, 1, 1])
    g = add_vertex_from_vertices(mesh, [a, b, c, d], [1, 1, 2, 1])    
    h = add_vertex_from_vertices(mesh, [a, b, c, d], [1, 1, 1, 2])

    mesh.delete_face(fkey)

    fkey_1 = mesh.add_face([a, b, f, e])
    fkey_2 = mesh.add_face([b, c, g, f])
    fkey_3 = mesh.add_face([c, d, h, g])
    fkey_4 = mesh.add_face([d, a, e, h])

    return fkey_1, fkey_2, fkey_3, fkey_4

def close_opening(mesh, vkeys):
    # vkeys of boundary component
    # sorted and oriented towards opening

    if vkeys[0] == vkeys[-1]:
        del vkeys[-1]

    if len(vkeys) == 4:
        return mesh.add_face(vkeys)
    
    else:
        g = add_vertex_from_vertices(mesh, vkeys, [1] * len(vkeys))
        new_vkeys = []
        for i in range(len(vkeys)):
            u = vkeys[i - 1]
            v = vkeys[i]
            a = add_vertex_from_vertices(mesh, [u, v], [1, 1])
            new_vkeys.append(a)
            insert_vertices_in_halfedge(mesh, v, u, [a])
        return [mesh.add_face([new_vkeys[i - 1], vkeys[i - 1], new_vkeys[i], g]) for i in range(len(vkeys))]

def flat_corner_2(mesh, fkey, corner):

    if len(mesh.face_vertices(fkey)) != 4:
        return None
    if corner not in mesh.face_vertices(fkey):
        return None

    a = corner
    b = mesh.face_vertex_descendant(fkey, a)
    c = mesh.face_vertex_descendant(fkey, b)
    d = mesh.face_vertex_descendant(fkey, c)

    e = add_vertex_from_vertices(mesh, [a, b, c, d], [1, 1, 1, 1])
    
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

    e = add_vertex_from_vertices(mesh, [b, c], [1, 1])
    f = add_vertex_from_vertices(mesh, [c, d], [1, 1])
    g = add_vertex_from_vertices(mesh, [a, b, c, d], [1, 1, 1, 1])
    
    mesh.delete_face(fkey)

    fkey_1 = mesh.add_face([a, b, e, g])
    fkey_2 = mesh.add_face([e, c, f, g])
    fkey_3 = mesh.add_face([d, a, g, f])

    insert_vertices_in_halfedge(mesh, c, b, [e])
    insert_vertices_in_halfedge(mesh, d, c, [f])

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

    e = add_vertex_from_vertices(mesh, [d, a], [1, 1])
    f = add_vertex_from_vertices(mesh, [a, b], [1, 1])
    g = add_vertex_from_vertices(mesh, [b, c], [1, 1])
    h = add_vertex_from_vertices(mesh, [c, d], [1, 1])

    i = add_vertex_from_vertices(mesh, [a, b, c, d], [1, 1, 1, 2])
    j = add_vertex_from_vertices(mesh, [a, b, c, d], [1, 2, 1, 1])
    k = add_vertex_from_vertices(mesh, [a, b, c, d], [1, 1, 1, 1])

    mesh.delete_face(fkey)

    fkey_1 = mesh.add_face([a, f, j, k])
    fkey_2 = mesh.add_face([f, b, g, j])
    fkey_3 = mesh.add_face([j, g, c , k])
    fkey_4 = mesh.add_face([a, k, i, e])
    fkey_5 = mesh.add_face([k, c, h, i])
    fkey_6 = mesh.add_face([e, i, h, d])

    insert_vertices_in_halfedge(mesh, b, a, [f])
    insert_vertices_in_halfedge(mesh, c, b, [g])
    insert_vertices_in_halfedge(mesh, d, c, [h])
    insert_vertices_in_halfedge(mesh, a, d, [e])

    return fkey_1, fkey_2, fkey_3, fkey_4, fkey_5, fkey_6

def split_35(mesh, fkey, edge):

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
    h = add_vertex_from_vertices(mesh, [b, c], [1, 1])
    i = add_vertex_from_vertices(mesh, [b, c], [1, 2])
    j = add_vertex_from_vertices(mesh, [c, d], [1, 1])
    k = add_vertex_from_vertices(mesh, [d, a], [2, 1])
    l = add_vertex_from_vertices(mesh, [d, a], [1, 1])
    m = add_vertex_from_vertices(mesh, [a, b, c, d], [3, 2, 1, 2])
    n = add_vertex_from_vertices(mesh, [a, b, c, d], [2, 2, 1, 1])
    o = add_vertex_from_vertices(mesh, [a, b, c, d], [2, 3, 2, 1])
    p = add_vertex_from_vertices(mesh, [a, b, c, d], [1, 1, 2, 2])

    mesh.delete_face(fkey)

    fkey_1 = mesh.add_face([a, e, m, l])
    fkey_2 = mesh.add_face([e, f, n, m])
    fkey_3 = mesh.add_face([f, g, o, n])
    fkey_4 = mesh.add_face([g, b, h, o])
    fkey_5 = mesh.add_face([l, m, p, k])
    fkey_6 = mesh.add_face([m, n, o, p])
    fkey_7 = mesh.add_face([o, h, i, p])
    fkey_8 = mesh.add_face([k, p, j, d])
    fkey_9 = mesh.add_face([p, i, c, j])

    insert_vertices_in_halfedge(mesh, b, a, [g, f, e])
    insert_vertices_in_halfedge(mesh, c, b, [i, h])
    insert_vertices_in_halfedge(mesh, d, c, [j])
    insert_vertices_in_halfedge(mesh, a, d, [l, k])

    return fkey_1, fkey_2, fkey_3, fkey_4, fkey_5, fkey_6, fkey_7, fkey_8, fkey_9

def split_35_diag(mesh, fkey, corner):

    if len(mesh.face_vertices(fkey)) != 4:
        return None
    if corner not in mesh.face_vertices(fkey):
        return None

    a = corner
    b = mesh.face_vertex_descendant(fkey, a)
    c = mesh.face_vertex_descendant(fkey, b)
    d = mesh.face_vertex_descendant(fkey, c)

    e = add_vertex_from_vertices(mesh, [a, b], [2, 1])
    f = add_vertex_from_vertices(mesh, [a, b], [1, 2])
    g = add_vertex_from_vertices(mesh, [b, c], [1, 2])
    h = add_vertex_from_vertices(mesh, [c, d], [2, 1])
    i = add_vertex_from_vertices(mesh, [d, a], [2, 1])
    j = add_vertex_from_vertices(mesh, [d, a], [1, 2])
    k = add_vertex_from_vertices(mesh, [a, c], [2, 1])
    l = add_vertex_from_vertices(mesh, [a, c], [1, 2])

    mesh.delete_face(fkey)

    fkey_1 = mesh.add_face([a, e, k, j])
    fkey_2 = mesh.add_face([e, f, l, k])
    fkey_3 = mesh.add_face([f, b, g, l])
    fkey_4 = mesh.add_face([j, k, l, i])
    fkey_5 = mesh.add_face([i, l, h, d])
    fkey_6 = mesh.add_face([l, g, c, h])

    insert_vertices_in_halfedge(mesh, b, a, [f, e])
    insert_vertices_in_halfedge(mesh, c, b, [g])
    insert_vertices_in_halfedge(mesh, d, c, [h])
    insert_vertices_in_halfedge(mesh, a, d, [j, i])

    return fkey_1, fkey_2, fkey_3, fkey_4, fkey_5, fkey_6

def split_26(mesh, fkey, edge):

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
    i = add_vertex_from_vertices(mesh, [c, d], [1, 1])
    j = add_vertex_from_vertices(mesh, [d, a], [2, 1])
    k = add_vertex_from_vertices(mesh, [a, b, c, d], [2, 2, 1, 1])
    l = add_vertex_from_vertices(mesh, [a, b, c, d], [1, 1, 1, 1])

    mesh.delete_face(fkey)

    fkey_1 = mesh.add_face([a, e, l, j])
    fkey_2 = mesh.add_face([e, f, k, l])
    fkey_3 = mesh.add_face([f, g, l, k])
    fkey_4 = mesh.add_face([g, b, h, l])
    fkey_5 = mesh.add_face([j, l, i, d])
    fkey_6 = mesh.add_face([l, h, c, i])

    insert_vertices_in_halfedge(mesh, b, a, [g, f, e])
    insert_vertices_in_halfedge(mesh, c, b, [h])
    insert_vertices_in_halfedge(mesh, d, c, [i])
    insert_vertices_in_halfedge(mesh, a, d, [j])

    return fkey_1, fkey_2, fkey_3, fkey_4, fkey_5, fkey_6

def simple_split(mesh, fkey, edge):

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

    e = add_vertex_from_vertices(mesh, [a, b], [1, 1])
    f = add_vertex_from_vertices(mesh, [c, d], [1, 1])

    mesh.delete_face(fkey)

    fkey_1 = mesh.add_face([a, e, f, d])
    fkey_2 = mesh.add_face([e, b, c, f])

    insert_vertices_in_halfedge(mesh, b, a, [e])
    insert_vertices_in_halfedge(mesh, d, c, [f])

    return fkey_1, fkey_2

def double_split(mesh, fkey):

    if len(mesh.face_vertices(fkey)) != 4:
        return None

    a, b, c, d = mesh.face_vertices(fkey)

    e = add_vertex_from_vertices(mesh, [a, b], [1, 1])
    f = add_vertex_from_vertices(mesh, [b, c], [1, 1])
    g = add_vertex_from_vertices(mesh, [c, d], [1, 1])
    h = add_vertex_from_vertices(mesh, [d, a], [1, 1])
    i = add_vertex_from_vertices(mesh, [a, b, c, d], [1, 1, 1, 1])

    mesh.delete_face(fkey)

    fkey_1 = mesh.add_face([a, e, i, h])
    fkey_2 = mesh.add_face([e, b, f, i])
    fkey_3 = mesh.add_face([h, i, g, d])
    fkey_4 = mesh.add_face([i, f, c, g])

    insert_vertices_in_halfedge(mesh, b, a, [e])
    insert_vertices_in_halfedge(mesh, c, b, [f])
    insert_vertices_in_halfedge(mesh, d, c, [g])
    insert_vertices_in_halfedge(mesh, a, d, [h])

    return fkey_1, fkey_2, fkey_3, fkey_4

def insert_pole(mesh, fkey, pole):

    if len(mesh.face_vertices(fkey)) != 4:
        return None
    if pole not in mesh.face_vertices(fkey):
        return None

    a = pole
    b = mesh.face_vertex_descendant(fkey, a)
    c = mesh.face_vertex_descendant(fkey, b)
    d = mesh.face_vertex_descendant(fkey, c)

    mesh.delete_face(fkey)

    fkey_1 = mesh.add_face([a, a, b, c])
    fkey_2 = mesh.add_face([a, a, c, d])

    return fkey_1, fkey_2

def insert_partial_pole(mesh, fkey, pole, edge):

    u, v = edge
    
    if len(mesh.face_vertices(fkey)) != 4:
        return None
    if pole not in mesh.face_vertices(fkey):
        return None
    if (u, v) not in mesh.face_halfedges(fkey) and (v, u) not in mesh.face_halfedges(fkey):
        return None

    if v not in mesh.halfedge[u] or mesh.halfedge[u][v] != fkey:
        u, v = v, u

    a = pole
    b = mesh.face_vertex_descendant(fkey, a)
    c = mesh.face_vertex_descendant(fkey, b)
    d = mesh.face_vertex_descendant(fkey, c)

    if u != b and u != c:
        return None

    mesh.delete_face(fkey)

    e = add_vertex_from_vertices(mesh, [u, v], [1, 1])

    if u == b:
        fkey_1 = mesh.add_face([a, a, b, e])
        fkey_2 = mesh.add_face([a, e, c, d])

    if u == c:
        fkey_1 = mesh.add_face([a, b, c, e])
        fkey_2 = mesh.add_face([a, a, e, d])

    insert_vertices_in_halfedge(mesh, v, u, [e])

    return fkey_1, fkey_2

def pseudo_quad_split(mesh, fkey):

    face_vertices = mesh.face_vertices(fkey)
    if len(face_vertices) != 4:
        return None

    pole = None
    for i in range(len(face_vertices) - 1):
        if face_vertices[i - 1] == face_vertices[i]:
            pole = face_vertices[i]
    if pole is None:
        return None

    face_vertices.remove(pole)
    idx = face_vertices.index(pole)
    a = pole
    b = mesh.face_vertex_descendant(fkey, a)
    c = mesh.face_vertex_descendant(fkey, b)

    mesh.delete_face(fkey)

    d = add_vertex_from_vertices(mesh, [a, b], [1, 1])
    e = add_vertex_from_vertices(mesh, [b, c], [1, 1])
    f = add_vertex_from_vertices(mesh, [c, a], [1, 1])
    g = add_vertex_from_vertices(mesh, [a, b, c], [1, 1, 1])

    fkey_1 = mesh.add_face([a, d, g, f])
    fkey_2 = mesh.add_face([b, e, g, d])
    fkey_3 = mesh.add_face([c, f, g, e])

    insert_vertices_in_halfedge(mesh, b, a, [d])
    insert_vertices_in_halfedge(mesh, c, b, [e])
    insert_vertices_in_halfedge(mesh, a, c, [f])

    return fkey_1, fkey_2, fkey_3
    
def singular_boundary_1(mesh, edge, vkey):

    u, v = edge
    if vkey != u and vkey != v:
        return None

    if mesh.is_edge_on_boundary(u, v):
        return None
    if len(mesh.face_vertices(mesh.halfedge[u][v])) != 4 or len(mesh.face_vertices(mesh.halfedge[v][u])) != 4:
        return None

    if vkey == u:
        b = u
        e = v
    else:
        b = v
        e = u

    fkey_1 = mesh.halfedge[b][e]
    fkey_2 = mesh.halfedge[e][b]

    f = mesh.face_vertex_descendant(fkey_1, e)
    a = mesh.face_vertex_descendant(fkey_1, f)
    c = mesh.face_vertex_descendant(fkey_2, b)
    d = mesh.face_vertex_descendant(fkey_2, c)

    mesh.delete_face(fkey_1)
    mesh.delete_face(fkey_2)

    g = add_vertex_from_vertices(mesh, [d, e], [1, 1])
    h = add_vertex_from_vertices(mesh, [e, f], [1, 1])

    fkey_1 = mesh.add_face([a, b, h, f])
    fkey_2 = mesh.add_face([b, g, e, h])
    fkey_3 = mesh.add_face([b, c, d, g])

    insert_vertices_in_halfedge(mesh, e, d, [g])
    insert_vertices_in_halfedge(mesh, f, e, [h])

    return fkey_1, fkey_2, fkey_3

def singular_boundary_2(mesh, edge, vkey):

    u, v = edge
    if vkey != u and vkey != v:
        return None

    if mesh.is_edge_on_boundary(u, v):
        return None
    if len(mesh.face_vertices(mesh.halfedge[u][v])) != 4 or len(mesh.face_vertices(mesh.halfedge[v][u])) != 4:
        return None

    if vkey == u:
        b = u
        e = v
    else:
        b = v
        e = u

    fkey_1 = mesh.halfedge[b][e]
    fkey_2 = mesh.halfedge[e][b]

    f = mesh.face_vertex_descendant(fkey_1, e)
    a = mesh.face_vertex_descendant(fkey_1, f)
    c = mesh.face_vertex_descendant(fkey_2, b)
    d = mesh.face_vertex_descendant(fkey_2, c)

    mesh.delete_face(fkey_1)
    mesh.delete_face(fkey_2)

    g = add_vertex_from_vertices(mesh, [d, e], [2, 1])
    h = add_vertex_from_vertices(mesh, [d, e], [1, 2])
    i = add_vertex_from_vertices(mesh, [e, f], [2, 1])
    j = add_vertex_from_vertices(mesh, [e, f], [1, 2])

    fkey_1 = mesh.add_face([a, b, j, f])
    fkey_2 = mesh.add_face([b, e, i, j])
    fkey_3 = mesh.add_face([b, g, h, e])
    fkey_4 = mesh.add_face([b, c, d, g])

    insert_vertices_in_halfedge(mesh, e, d, [h, g])
    insert_vertices_in_halfedge(mesh, f, e, [j, i])

    return fkey_1, fkey_2, fkey_3

def remove_tri(mesh, fkey_tri, fkey_quad, pole, t = .5):

    if len(mesh.face_vertices(fkey_tri)) != 3 or len(mesh.face_vertices(fkey_quad)) != 4:
        return None

    if fkey_tri not in mesh.face_neighbours(fkey_quad):
        return None

    if pole not in mesh.face_vertices(fkey_tri) or pole not in mesh.face_vertices(fkey_quad):
        return None

    nbr = mesh.face_vertex_descendant(fkey_quad, pole)

    if nbr not in mesh.face_vertices(fkey_tri):
        d = pole
        e = nbr
        a = mesh.face_vertex_descendant(fkey_quad, e)
        b = mesh.face_vertex_descendant(fkey_quad, a)
        c = mesh.face_vertex_descendant(fkey_tri, b)

        mesh.delete_face(fkey_tri)
        mesh.delete_face(fkey_quad)

        f = add_vertex_from_vertices(mesh, [d, e], [1 - t, t])

        fkey_tri = mesh.add_face([a, b, f, e])
        fkey_quad = mesh.add_face([b, c, d, f])

        insert_vertices_in_halfedge(mesh, e, d, [f])

    else:
        b = pole
        d = nbr
        e = mesh.face_vertex_descendant(fkey_quad, d)
        a = mesh.face_vertex_descendant(fkey_quad, e)
        c = mesh.face_vertex_descendant(fkey_tri, b)

        mesh.delete_face(fkey_tri)
        mesh.delete_face(fkey_quad)

        f = add_vertex_from_vertices(mesh, [b, a], [1 - t, t])

        fkey_tri = mesh.add_face([a, f, d, e])
        fkey_quad = mesh.add_face([b, c, d, f])

        insert_vertices_in_halfedge(mesh, b, a, [f])

    return fkey_tri, fkey_quad

def rotate_vertex(mesh, vkey):

    if vkey not in mesh.vertices():
        return None
    if vkey in mesh.vertices_on_boundary():
        return None

    face_vertices = {}
    for nbr in mesh.vertex_neighbours(vkey, True):
        fkey_0 = mesh.halfedge[vkey][nbr]
        fkey_1 = mesh.halfedge[nbr][vkey]
        ukey = mesh.face_vertex_descendant(fkey_0, nbr)
        wkey = mesh.face_vertex_ancestor(fkey_1, nbr)
        face_vertices[fkey_0] = [ukey, vkey, wkey, nbr]

    for fkey, vertices in face_vertices.items():
        mesh.delete_face(fkey)
        mesh.add_face(vertices, fkey = fkey)

    return list(face_vertices.keys())

def clear_faces(mesh, fkeys, vkeys):
    # groups of fkeys must be a topological disc
    # vkeys must be four vertices part of the fkeys boundary

    vertices = [mesh.vertex_coordinates(vkey) for vkey in mesh.vertices()]
    face_vertices = [mesh.face_vertices(fkey) for fkey in fkeys]

    faces_mesh = PseudoQuadMesh.from_vertices_and_faces(vertices, face_vertices)
    faces_boundary_vertices = mesh_boundaries(faces_mesh)[0]
    faces_boundary_vertices = list(reversed(faces_boundary_vertices[:-1]))

    for fkey in fkeys:
        mesh.delete_face(fkey)

    # orientation? reverse boundary vertices?
    fkey = mesh.add_face(faces_boundary_vertices)

    new_fkeys = face_propagation(mesh, fkey, vkeys)

    return new_fkeys

def add_handle(mesh, fkey_1, fkey_2):
    # add a handle between two faces by first adding openings
    # add from two openings directly?

    # check orientation: is the normal of face i pointing towards face j?
    v_12 = subtract_vectors(mesh.face_centroid(fkey_2), mesh.face_centroid(fkey_1))
    orientation_1 = dot_vectors(v_12, mesh.face_normal(fkey_1))
    v_21 = subtract_vectors(mesh.face_centroid(fkey_1), mesh.face_centroid(fkey_2))
    orientation_2 = dot_vectors(v_21, mesh.face_normal(fkey_2))
    # if both orientations are not the same, stop
    if orientation_1 * orientation_2 < 0:
        return None

    vertices = [vkey for vkey in mesh.vertices()]

    # add firtst opening
    faces_1 = face_opening(mesh, fkey_1)
    # find newly added vertices
    vertices_1 = [vkey for vkey in mesh.vertices() if vkey not in vertices]

    # add second opening
    faces_2 = face_opening(mesh, fkey_2)
    # find newly added vertices
    vertices_2 = [vkey for vkey in mesh.vertices() if vkey not in vertices and vkey not in vertices_1]

    # sort the vertices along the new boundary components
    # first one
    sorted_vertices_1 = [vertices_1.pop()]
    count = 4
    while len(vertices_1) > 0 and count > 0:
        count -= 1
        for vkey in vertices_1:
            if vkey in mesh.halfedge[sorted_vertices_1[-1]] and mesh.halfedge[sorted_vertices_1[-1]][vkey] is not None:
                sorted_vertices_1.append(vkey)
                vertices_1.remove(vkey)
                break

    # second one
    sorted_vertices_2 = [vertices_2.pop()]
    count = 4
    while len(vertices_2) > 0 and count > 0:
        count -= 1
        for vkey in vertices_2:
            if vkey in mesh.halfedge[sorted_vertices_2[-1]] and mesh.halfedge[sorted_vertices_2[-1]][vkey] is not None:
                sorted_vertices_2.append(vkey)
                vertices_2.remove(vkey)
                break        

    # match the facing boundary vertices so as to reduce the total distance
    min_dist = -1
    sorted_vertices = []
    for i in range(4):
        a, b, c, d = sorted_vertices_1
        e, f, g, h = [sorted_vertices_2[j - i] for j in range(4)]
        d1 = distance_point_point(mesh.vertex_coordinates(a), mesh.vertex_coordinates(e))
        d2 = distance_point_point(mesh.vertex_coordinates(b), mesh.vertex_coordinates(h))
        d3 = distance_point_point(mesh.vertex_coordinates(c), mesh.vertex_coordinates(g))
        d4 = distance_point_point(mesh.vertex_coordinates(d), mesh.vertex_coordinates(f))
        dist = d1 + d2 + d3 + d4
        if min_dist < 0 or dist < min_dist:
            min_dist = dist
            sorted_vertices = [a, b, c, d, e, f, g, h]

    # add the new faces that close the holes as a handle
    a, b, c, d, e, f, g, h = sorted_vertices
    fkey_1 = mesh.add_face([a, d, f, e])
    fkey_2 = mesh.add_face([d, c, g, f])
    fkey_3 = mesh.add_face([c, b, h, g])
    fkey_4 = mesh.add_face([b, a, e, h])

    return faces_1 + faces_2 + (fkey_1, fkey_2, fkey_3, fkey_4)
    
def close_handle(mesh, fkeys):
    # remove handle and close openings
    # fkeys: closed face strip

    if fkeys[0] == fkeys[-1]:
        del fkeys[-1]

    vertices = []
    key_to_index = {}
    for i, vkey in enumerate(mesh.vertices()):
        vertices.append(mesh.vertex_coordinates(vkey))
        key_to_index[vkey] = i
    faces = [[key_to_index[vkey] for vkey in mesh.face_vertices(fkey)] for fkey in fkeys]
    strip_mesh = Mesh.from_vertices_and_faces(vertices, faces)
    
    boundaries = mesh_boundaries(strip_mesh)

    for fkey in fkeys:
        mesh.delete_face(fkey)
    new_fkeys = []
    for bdry in boundaries:
        new_fkeys += close_opening(mesh, list(reversed(bdry)))

    return new_fkeys

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas

    vertices = [[0,0,0],[1,0,0],[1,1,0],[0,1,0],[2,.5,0]]
    faces = [[0,1,2,3],[1,4,2]]

    mesh = PseudoQuadMesh.from_vertices_and_faces(vertices, faces)

    #remove_tri(mesh, 1, 0, 2)
    clear_faces(mesh, [0, 1], [0, 1, 2, 3])

    for fkey in mesh.faces():
        print mesh.face_vertices(fkey)

    print mesh
