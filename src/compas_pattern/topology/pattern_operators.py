from compas.datastructures.mesh import Mesh

from compas_pattern.datastructures.mesh import insert_vertices_in_face

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
    'conway_dual',
    'conway_join',
    'conway_ambo',
    'conway_kis',
    'conway_needle',
    'conway_gyro',
]

# Reference:
# Wikipedia. Conway polyhedron notation.
# https://en.wikipedia.org/wiki/Conway_polyhedron_notation

def conway_dual(mesh):
    # dual mesh

    old_vertices = list(mesh.vertices())

    old_face_to_new_vertices = {}
    
    for fkey in mesh.faces():
        x, y, z = mesh.face_centroid(fkey)
        vkey = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})
        old_face_to_new_vertices[fkey] = vkey

    new_faces = []
    for vkey in old_vertices:
        face_vertices = [old_face_to_new_vertices[fkey] for fkey in mesh.vertex_faces(vkey, ordered = True)]
        if mesh.is_vertex_on_boundary(vkey):
            nbrs = mesh.vertex_neighbours(vkey, ordered = True)
            x, y, z = mesh.edge_midpoint(vkey, nbrs[0])
            face_vertices.insert(0, mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z}))
            x, y, z = mesh.edge_midpoint(vkey, nbrs[-1])
            face_vertices.append(mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z}))
            if len(mesh.vertex_neighbours(vkey)) == 2:
                face_vertices.append(vkey)
        new_faces.append(face_vertices)

    old_faces = list(mesh.faces())
    for fkey in old_faces:
        mesh.delete_face(fkey)

    for face_vertices in new_faces:
        mesh.add_face(face_vertices)

    unused_vertices = [vkey for vkey in mesh.vertices() if len(mesh.vertex_neighbours(vkey)) == 0]
    for vkey in unused_vertices:
        del mesh.vertex[vkey]

    return mesh

def conway_join(mesh):
    # diagonal mesh

    old_face_to_new_vertices = {}
    
    for fkey in mesh.faces():
        x, y, z = mesh.face_centroid(fkey)
        vkey = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})
        old_face_to_new_vertices[fkey] = vkey

    new_faces = []
    for u, v in mesh.edges():
        new_face = [u, v]
        if v in mesh.halfedge[u] and mesh.halfedge[u][v] is not None:
            fkey_1 = mesh.halfedge[u][v]
            vkey_1 = old_face_to_new_vertices[fkey_1]
            new_face.append(vkey_1)
        if u in mesh.halfedge[v] and mesh.halfedge[v][u] is not None:
            fkey_2 = mesh.halfedge[v][u]
            vkey_2 = old_face_to_new_vertices[fkey_2]
            new_face.insert(1, vkey_2)
        new_faces.append(new_face)

    old_faces = list(mesh.faces())
    for fkey in old_faces:
        mesh.delete_face(fkey)

    for face_vertices in new_faces:
        mesh.add_face(face_vertices)

    unused_vertices = [vkey for vkey in mesh.vertices() if len(mesh.vertex_neighbours(vkey)) == 0]
    for vkey in unused_vertices:
        del mesh.vertex[vkey]

    return mesh

def conway_ambo(mesh):
    # dual of diagonal mesh

    old_vertices = list(mesh.vertices())

    old_edge_to_new_vertices = {}
    for u, v in mesh.edges():
        x, y, z = mesh.edge_midpoint(u, v)
        vkey = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})
        old_edge_to_new_vertices[(u, v)] = vkey
        old_edge_to_new_vertices[(v, u)] = vkey

    new_faces = []

    for fkey in mesh.faces():
        face_vertices = []
        for u, v in mesh.face_halfedges(fkey):
            face_vertices.append(old_edge_to_new_vertices[(u, v)])
        new_faces.append(face_vertices)

    for vkey in old_vertices:
        nbrs = mesh.vertex_neighbours(vkey, ordered = True)
        if len(nbrs) == 2 and not mesh.is_vertex_on_boundary(vkey):
            continue
        else:
            face_vertices = [old_edge_to_new_vertices[(vkey, nbr)] for nbr in mesh.vertex_neighbours(vkey, ordered = True)]
            if len(face_vertices) == 2:
                face_vertices.append(vkey)
            face_vertices = list(reversed(face_vertices))
            new_faces.append(face_vertices)

    old_faces = list(mesh.faces())
    for fkey in old_faces:
        mesh.delete_face(fkey)

    for face_vertices in new_faces:
        mesh.add_face(face_vertices)

    unused_vertices = [vkey for vkey in mesh.vertices() if len(mesh.vertex_neighbours(vkey)) == 0]
    for vkey in unused_vertices:
        del mesh.vertex[vkey]

    return mesh

def conway_kis(mesh):
    # mesh plus diagonals
    new_faces = []

    for fkey in mesh.faces():
        x, y, z = mesh.face_centroid(fkey)
        g = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})
        for u, v in mesh.face_halfedges(fkey):
            new_faces.append([u, v, g])

    old_faces = list(mesh.faces())
    for fkey in old_faces:
        mesh.delete_face(fkey)

    for face_vertices in new_faces:
        mesh.add_face(face_vertices)

    unused_vertices = [vkey for vkey in mesh.vertices() if len(mesh.vertex_neighbours(vkey)) == 0]
    for vkey in unused_vertices:
        del mesh.vertex[vkey]

    return mesh

def conway_needle(mesh):
    # mesh plus diagonals of dual
    old_face_to_new_vertices = {}
    
    for fkey in mesh.faces():
        x, y, z = mesh.face_centroid(fkey)
        vkey = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})
        old_face_to_new_vertices[fkey] = vkey

    new_faces = []
    for u, v in mesh.edges():
        if mesh.is_edge_on_boundary(u, v):
            x, y, z = mesh.edge_midpoint(u, v)
            vkey = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})
        if mesh.halfedge[u][v] is None:
            fkey_2 = mesh.halfedge[v][u]
            vkey_1 = vkey
            vkey_2 = old_face_to_new_vertices[fkey_2]
        elif mesh.halfedge[v][u] is  None:
            fkey_1 = mesh.halfedge[u][v]
            vkey_1 = old_face_to_new_vertices[fkey_1]
            vkey_2 = vkey
        else:
            fkey_1 = mesh.halfedge[u][v]
            fkey_2 = mesh.halfedge[v][u]
            vkey_1 = old_face_to_new_vertices[fkey_1]
            vkey_2 = old_face_to_new_vertices[fkey_2]
        new_faces.append([v, vkey_1, vkey_2])
        new_faces.append([u, vkey_2, vkey_1])

    old_faces = list(mesh.faces())
    for fkey in old_faces:
        mesh.delete_face(fkey)

    for face_vertices in new_faces:
        mesh.add_face(face_vertices)

    unused_vertices = [vkey for vkey in mesh.vertices() if len(mesh.vertex_neighbours(vkey)) == 0]
    for vkey in unused_vertices:
        del mesh.vertex[vkey]

    return mesh

def conway_gyro(mesh):
    # Cairo pentagonal pattern

    orientation = 'left'
    
    if orientation != 'left' and orientation != 'right':
        return mesh

    old_faces_vertices = {}
    for fkey in mesh.faces():
        old_faces_vertices[fkey] = mesh.face_vertices(fkey)[:]

    old_edges = list(mesh.edges())
    for u, v in old_edges:
        x, y, z = mesh.edge_point(u, v, .33)
        a = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})
        x, y, z = mesh.edge_point(u, v, .67)
        b = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})
        if v in mesh.halfedge[u] and mesh.halfedge[u][v] is not None:
            fkey = mesh.halfedge[u][v]
            insert_vertices_in_face(mesh, fkey, u, [a, b])
        if u in mesh.halfedge[v] and mesh.halfedge[v][u] is not None:
            fkey = mesh.halfedge[v][u]
            insert_vertices_in_face(mesh, fkey, v, [b, a])

    new_faces = []
    for fkey in mesh.faces():
        x, y, z = mesh.face_centroid(fkey)
        g = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})
        old_face_vertices = old_faces_vertices[fkey]
        for vkey in old_face_vertices:
            if orientation == 'left':
                a = vkey
                b = mesh.face_vertex_descendant(fkey, a)
                c = g
                e = mesh.face_vertex_ancestor(fkey, a)
                d = mesh.face_vertex_ancestor(fkey, e)
            elif orientation == 'right':
                a = vkey
                b = mesh.face_vertex_descendant(fkey, a)
                c = mesh.face_vertex_descendant(fkey, b)
                d = g
                e = mesh.face_vertex_ancestor(fkey, a)
            new_faces.append([a, b, c, d, e])

    old_faces = list(mesh.faces())
    for fkey in old_faces:
        mesh.delete_face(fkey)

    for face_vertices in new_faces:
        mesh.add_face(face_vertices)

    unused_vertices = [vkey for vkey in mesh.vertices() if len(mesh.vertex_neighbours(vkey)) == 0]
    for vkey in unused_vertices:
        del mesh.vertex[vkey]
        
    return mesh

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
