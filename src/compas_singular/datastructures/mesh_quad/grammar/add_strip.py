from compas.topology import breadth_first_paths
from compas.datastructures import mesh_substitute_vertex_in_faces
from compas.utilities import pairwise

# from ..grammar_pattern import strip_polyedge_update


__all__ = [
]


def add_strips(mesh, polyedges, callback=None, callback_args=None):
    to_add = polyedges[:]
    while len(to_add) > 0:
        polyedge = to_add.pop()
        add_strip(mesh, polyedge)
        # update polyedges
        if callback:
            if callable(callback):
                callback(mesh, callback_args)


def add_strip(mesh, polyedge):
    full_updated_polyedge = []
    # store data
    left_polyedge = []
    right_polyedge = []
    new_faces = []

    # exception if closed
    is_closed = polyedge[0] == polyedge[-1]
    if is_closed:
        polyedge.pop()

    k = -1
    count = len(polyedge) * 2
    while count and len(polyedge) > 0:
        k += 1
        count -= 1

        # select u, v, w if not closed
        if not is_closed:
            # u
            if len(new_faces) != 0:
                u1, u2 = left_polyedge[-1], right_polyedge[-1]
            else:
                u1, u2 = None, None
            # v
            v = polyedge.pop(0)
            full_updated_polyedge.append(v)
            # w
            if len(polyedge) != 0:
                w = polyedge[0]
            else:
                w = None

        # select u, v, w if closed
        else:
            # u
            if len(new_faces) != 0:
                u1, u2 = left_polyedge[-1], right_polyedge[-1]
            else:
                u1 = polyedge[-1]  # artificial u1
            # v
            v = polyedge.pop(0)
            full_updated_polyedge.append(v)
            # w
            if len(polyedge) != 0:
                w = polyedge[0]
            else:
                w = left_polyedge[0]

        # add new vertices
        faces = sort_faces(mesh, u1, v, w)
        v1, v2 = mesh.add_vertex(attr_dict=mesh.vertex[v]), mesh.add_vertex(attr_dict=mesh.vertex[v])

        if type(faces[0]) == list:
            faces_1, faces_2 = faces
        else:
            # exception necessary for U-turns
            if faces[0] in mesh.vertex_faces(left_polyedge[-2]):
                faces_1 = faces
                faces_2 = []
            else:
                faces_1 = []
                faces_2 = faces
        mesh_substitute_vertex_in_faces(mesh, v, v1, faces_1)
        mesh_substitute_vertex_in_faces(mesh, v, v2, faces_2)
        mesh.delete_vertex(v)
        left_polyedge.append(v1)
        right_polyedge.append(v2)

        # add new faces, different if at the start, end or main part of the polyedge
        if len(new_faces) == 0:
            if not is_closed:
                new_faces.append(mesh.add_face([v1, w, v2]))
            else:
                new_faces.append(mesh.add_face([v1, v2, u1]))
                new_faces.append(mesh.add_face([v1, w, v2]))
        elif len(polyedge) == 0:
            if not is_closed:
                u1, u2 = left_polyedge[-2], right_polyedge[-2]
                face = new_faces.pop()
                mesh.delete_face(face)
                new_faces.append(mesh.add_face([u1, v1, v2, u2]))
            else:
                u1, u2 = left_polyedge[-2], right_polyedge[-2]
                face = new_faces.pop()
                mesh.delete_face(face)
                new_faces.append(mesh.add_face([v1, u1, u2, v2]))
                face = new_faces.pop(0)
                mesh.delete_face(face)
                u1, u2 = left_polyedge[0], right_polyedge[0]
                new_faces.append(mesh.add_face([v1, u1, u2, v2]))

                mesh_substitute_vertex_in_faces(mesh, v, v1)
                mesh_substitute_vertex_in_faces(mesh, v, v2)
        else:
            face = new_faces.pop()
            mesh.delete_face(face)
            new_faces.append(mesh.add_face([u1, v1, v2, u2]))
            new_faces.append(mesh.add_face([v1, w, v2]))

        # update
        updated_polyedge = []
        via_vkeys = [v1, v2]
        for i, vkey in enumerate(polyedge):
            if vkey != v:
                updated_polyedge.append(vkey)
            else:
                from_vkey = polyedge[i - 1]
                to_vkey = polyedge[i + 1]
                updated_polyedge += polyedge_from_to_via_vertices(mesh, from_vkey, to_vkey, via_vkeys)[1:-1]
        polyedge = updated_polyedge

    # include pseudo closed polyedges

    old_vkeys_to_new_vkeys = {u0: (u1, u2) for u0, u1, u2 in zip(full_updated_polyedge, left_polyedge, right_polyedge)}

    # for fkey in mesh.faces():
    #    print(mesh.face_vertices(fkey))
    n = update_strip_data(mesh, full_updated_polyedge, old_vkeys_to_new_vkeys)
    # print(left_polyedge, right_polyedge)
    return n, old_vkeys_to_new_vkeys


def add_element_start(mesh, u, v):
    pass


def add_element_main(mesh, u, v):
    pass


def add_element_end(mesh, u, v):
    pass


def update_strip_data(mesh, full_updated_polyedge, old_vkeys_to_new_vkeys):
    # orthogonal strips
    orth_to_update = {}
    # orth_skeys = []
    for old_u, old_v in pairwise(full_updated_polyedge):
        new_u = old_vkeys_to_new_vkeys[old_u][0]
        new_v = old_vkeys_to_new_vkeys[old_v][0]
        skey = mesh.edge_strip((old_u, old_v))
        edges = mesh.collect_strip(new_u, new_v)
        orth_to_update[skey] = edges
    for skey, edges in orth_to_update.items():
        mesh.attributes['strips'][skey] = edges

    # parallel strips
    paral_to_update = {}
    for skey, edges in mesh.attributes['strips'].items():
        if skey not in orth_to_update:
            for u, v in edges:
                if u in old_vkeys_to_new_vkeys:
                    u, v = v, u
                elif v in old_vkeys_to_new_vkeys:
                    u, v = u, v
                else:
                    continue
                new_v = [vkey for vkey in old_vkeys_to_new_vkeys[v] if vkey in mesh.halfedge[u]][0]
                new_edges = mesh.collect_strip(u, new_v)
                paral_to_update[skey] = new_edges
                break
    for skey, edges in paral_to_update.items():
        mesh.attributes['strips'][skey] = edges

    # self strip
    n = max(mesh.attributes['strips']) + 1
    strip_edges = [tuple(old_vkeys_to_new_vkeys[vkey]) for vkey in full_updated_polyedge]
    mesh.attributes['strips'][n] = strip_edges

    return n


def update_polyedge(polyedge, old_vkey_to_new_vkey):

    return [old_vkey_to_new_vkey.get(vkey, vkey) for vkey in polyedge]


def sort_faces(mesh, u, v, w):

    sorted_faces = [[], []]
    k = 0
    vertex_faces = mesh.vertex_faces(v, ordered=True, include_none=True)
    f0 = mesh.halfedge[w][v] if w is not None else None
    i0 = vertex_faces.index(f0)
    vertex_faces = vertex_faces[i0:] + vertex_faces[:i0]

    for face in vertex_faces:

        if face is not None:
            sorted_faces[k].append(face)

        if u is None:
            if face is None:
                k = 1 - k
        elif face == mesh.halfedge[v][u]:
            k = 1 - k

    # indeterminate exception if u == w
    if u == w:
        return [face for faces in sorted_faces for face in faces]
    else:
        return sorted_faces


def adjacency_from_to_via_vertices(mesh, from_vkey, to_vkey, via_vkeys):
    # get mesh adjacency constraiend to from_vkey and via_keys, via_keys and via_keys, and via_vkeys and to_vkey

    all_vkeys = set([from_vkey, to_vkey] + via_vkeys)
    adjacency = {}
    for vkey, nbrs in mesh.adjacency.items():
        if vkey not in all_vkeys:
            continue
        else:
            sub_adj = {}
            for nbr, face in nbrs.items():
                if nbr not in all_vkeys or (vkey == from_vkey and nbr == to_vkey) or (vkey == to_vkey and nbr == from_vkey):
                    continue
                else:
                    sub_adj.update({nbr: face})
            adjacency.update({vkey: sub_adj})
    return adjacency


def polyedge_from_to_via_vertices(mesh, from_vkey, to_vkey, via_vkeys):
    # return shortest polyedge from_vkey to_vkey via_vkeys

    adjacency = adjacency_from_to_via_vertices(mesh, from_vkey, to_vkey, via_vkeys)
    return next(breadth_first_paths(adjacency, from_vkey, to_vkey))


def is_polyedge_valid_for_strip_addition(mesh, polyedge):
    if len(polyedge) > 2:
        if polyedge[0] == polyedge[-1] or (mesh.is_vertex_on_boundary(polyedge[0]) and mesh.is_vertex_on_boundary(polyedge[-1])):
            return True
    return False

# ==============================================================================
# Main
# ==============================================================================


if __name__ == '__main__':
    pass

    # import compas
    # from compas_singular.datastructures.mesh_quad_coarse.mesh_quad_coarse import CoarseQuadMesh
    # from compas.datastructures import mesh_smooth_centroid
    # from compas_singular.datastructures.mesh.operations import mesh_move_by
    # from compas.datastructures import meshes_join
    # from compas_plotters.meshplotter import MeshPlotter

    # mesh = CoarseQuadMesh.from_obj(compas.get('faces.obj'))
    # mesh.collect_strips()
    # #polyedge = [0, 1, 2, 8, 14, 13, 12, 6, 0]
    # #polyedge = [7, 8, 9, 15, 21, 20, 19, 13, 7]
    # polyedge = [0, 1, 7, 6, 0]
    # output = add_strip(mesh, polyedge)
    # print(output)
    # mesh_smooth_centroid(mesh, kmax=10, fixed=mesh.vertices_on_boundary())
    # plotter = MeshPlotter(mesh, figsize=(5, 5))
    # plotter.draw_vertices(radius=0.2, text='key')
    # plotter.draw_edges()
    # plotter.draw_faces()
    # plotter.show()

    # # plotter = MeshPlotter(mesh, figsize = (5, 5))
    # # plotter.draw_vertices(radius = 0.25, text='key')
    # # plotter.draw_edges()
    # # plotter.draw_faces(text='key')
    # # plotter.show()

    # # polyedges = [
    # # 	[6, 7, 8, 9, 10, 11],
    # # 	[0, 1, 2, 3, 4, 5],
    # # 	[30, 31, 32, 33, 34, 35],
    # # 	[24, 25, 26, 32],
    # # 	[14, 15, 21, 20, 14],
    # # 	[6, 7, 8, 14, 13, 7, 1],
    # # 	# [2, 8, 2],
    # # 	[1, 2, 8, 2, 3],
    # # 	# [2, 8, 14, 8, 2],
    # # 	[0, 1, 2, 8, 2, 3, 4, 5],
    # # ]

    # # # from compas.utilities import window
    # # # for u, v, w in window(polyedges[0], n=3):
    # # # 	 print(sort_faces(mesh, u, v, w))

    # meshes = []
    # for i, polyedge in enumerate(polyedges):
    # 	print(polyedge)
    # 	mesh2 = mesh.copy()
    # 	add_strip(mesh2, polyedge)
    # 	#mesh_smooth_centroid(mesh2, fixed=[vkey for vkey in mesh.vertices_on_boundary() if len(mesh.vertex_neighbors(vkey)) == 2], kmax=1)
    # 	mesh_smooth_centroid(mesh2, kmax=20)
    # 	mesh_move_by(mesh2, [i * 10.0, 0.0, 0.0])
    # 	meshes.append(mesh2)

    # mesh = meshes_join(meshes)

    # plotter = MeshPlotter(mesh, figsize=(20, 20))
    # plotter.draw_vertices()#radius=0.1, text='key')
    # plotter.draw_edges()
    # plotter.draw_faces()
    # plotter.show()

    # #print(polyedge_from_to_via_vertices(mesh, 6, 8, [12, 13, 14]))

    # vertices = [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [0.0, 1.0, 0.0], [0.5, 0.5, 0.0]]
    # faces = [[0, 1, 2, 4] , [2, 3, 0, 4]]
    # mesh = CoarseQuadMesh.from_vertices_and_faces(vertices, faces)
    # polyedge = [2, 4, 0]
    # add_strip(mesh, polyedge)
    # for fkey in mesh.faces():
    # 	print(mesh.face_vertices(fkey))
    # mesh_smooth_centroid(mesh, kmax=10)
    # plotter = MeshPlotter(mesh, figsize=(20, 20))
    # plotter.draw_vertices(radius=0.001, text='key')
    # plotter.draw_edges()
    # plotter.draw_faces()
    # plotter.show()

    # vertices = [[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [0.0, 1.0, 0.0]]
    # faces = [[0, 1, 2, 3]]
    # mesh = CoarseQuadMesh.from_vertices_and_faces(vertices, faces)
    # mesh.collect_strips()
    # polyedge = [0, 1, 2, 3, 0]
    # add_strip(mesh, polyedge)
    # print(mesh.attributes['strips'])
    # print('boundary: ', mesh.vertices_on_boundary())
    # mesh_smooth_centroid(mesh, kmax=2, fixed=mesh.vertices_on_boundary())
    # plotter = MeshPlotter(mesh, figsize=(20, 20))
    # plotter.draw_vertices(radius=0.01, text='key')
    # plotter.draw_edges()
    # plotter.draw_faces()
    # plotter.show()
