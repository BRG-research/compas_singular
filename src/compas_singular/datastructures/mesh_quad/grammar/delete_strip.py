from compas.datastructures import network_disconnected_nodes
from compas.datastructures import mesh_substitute_vertex_in_faces
from compas.geometry import centroid_points
from compas.utilities import pairwise

from ...network import Network


__all__ = [
]


def delete_strips(mesh, skeys, callback=None, callback_args=None):
    for skey in skeys:
        if skey in mesh.strips():
            delete_strip(mesh, skey)
            if callback:
                if callable(callback):
                    callback(mesh, callback_args)


def delete_strip(mesh, skey, update_data=True):
    """Delete a strip.

    Parameters
    ----------
    mesh : QuadMesh
        A quad mesh.
    skey : hashable
        A strip key.
    update_data : bool, optional
        Update strip data. Default is True.

    Returns
    -------
    skey_to_skeys : dict, None
        If strip splits were applied to preserve boundaries, a dictionary of the initial strip key to the refining strip keys. None otherwise.

    """

    # build network between vertices of the edges of the strip to delete to get the disconnect parts of vertices to merge
    network = strip_edge_network(mesh, skey)
    disc_vertices = network_disconnected_nodes(network)

    # delete strip faces
    for fkey in mesh.strip_faces(skey):
        mesh.delete_face(fkey)

    old_vkeys_to_new_vkeys = {}

    # merge strip edge vertices that are connected
    for vertices in disc_vertices:

        # new vertex
        x, y, z = centroid_points([mesh.vertex_coordinates(vkey) for vkey in vertices])
        new_vkey = mesh.add_vertex(attr_dict={'x': x, 'y': y, 'z': z})
        old_vkeys_to_new_vkeys.update({old_vkey: new_vkey for old_vkey in vertices})

        # replace the old vertices
        for old_vkey in vertices:
            _ = mesh_substitute_vertex_in_faces(mesh, old_vkey, new_vkey, mesh.vertex_faces(old_vkey))

        # delete the old vertices
        for old_vkey in vertices:
            mesh.delete_vertex(old_vkey)

    # update strip data
    if update_data:
        update_strip_data(mesh, old_vkeys_to_new_vkeys)

    return old_vkeys_to_new_vkeys


def strip_edge_network(mesh, skey):
    all_strip_vertices = list(set([vkey for edge in mesh.strip_edges(skey) for vkey in edge]))
    strip_edges = [(u, v) for u, v in mesh.strip_edges(skey) if u != v]  # exception for poles
    strip_vertices = {vkey: mesh.vertex_coordinates(vkey) for vkey in all_strip_vertices}
    return Network.from_nodes_and_edges(strip_vertices, strip_edges)


def update_strip_data(mesh, old_vkeys_to_new_vkeys):
    strip_data = mesh.attributes['strips'].copy()

    for skey, edges in strip_data.items():
        new_edges = [tuple([old_vkeys_to_new_vkeys.get(vkey, vkey) for vkey in edge]) for edge in edges]

        # remove collapsed strips
        if all([u == v for u, v in new_edges]):
            del mesh.attributes['strips'][skey]
            continue

        # remove collapsed faces
        duplicates = []
        for i, edge in enumerate(new_edges):
            if i != 0:
                if edge == new_edges[i - 1]:
                    duplicates.append(i)
        for i in reversed(duplicates):
            del new_edges[i]
        mesh.attributes['strips'][skey] = new_edges

        # remove collateral collapsed strips
        if len(new_edges) < 2:
            del mesh.attributes['strips'][skey]


def strips_to_split_to_prevent_boundary_collapse(mesh, skeys):
    """Computes strips to split to preserve boundaries before deleting strips.

    Parameters
    ----------
    mesh : QuadMesh
        A quad mesh.
    skey : set
        Strip keys.

    Returns
    -------
    to_split: dict
        A dictionary of strip keys pointing to the refinement value.

    """

    to_split = {}
    for boundary in mesh.boundaries():
        non_deleted_strips = [mesh.edge_strip((u, v)) for u, v in pairwise(boundary + boundary[:1]) if mesh.edge_strip((u, v)) not in skeys]

        if len(non_deleted_strips) == 0:
            return None

        elif len(non_deleted_strips) == 1:
            skey = non_deleted_strips[0]
            if skey in to_split:
                if to_split[skey] == 3:
                    break
                if to_split[skey] == 2:
                    to_split[skey] = 3
            else:
                to_split[skey] = 3

        elif len(non_deleted_strips) == 2:
            for skey in non_deleted_strips:
                if skey in to_split:
                    break
            to_split.update({skey: 2 for skey in non_deleted_strips})

    return to_split


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass

    # import itertools as it
    # import compas
    # from compas_singular.datastructures.mesh_quad_coarse.mesh_quad_coarse import CoarseQuadMesh
    # from compas_singular.datastructures.mesh_quad_pseudo_coarse.mesh_quad_pseudo_coarse import CoarsePseudoQuadMesh
    # from compas_plotters.meshplotter import MeshPlotter

    # # mesh = CoarsePseudoQuadMesh.from_json('/Users/Robin/Desktop/debug_delete_strip.json')
    # # vertices, faces = mesh.to_vertices_and_faces()
    # # pole_coordinates = [mesh.vertex_coordinates(vkey) for vkey in [0, 3, 17, 21]]
    # # mesh = CoarsePseudoQuadMesh.from_vertices_and_faces_with_poles(vertices, faces, pole_coordinates)
    # # mesh.collect_strips()
    # # # for skey in [0, 3, 5]:
    # # # 	print(mesh.strip_edges(skey))
    # # # print(mesh.halfedge)

    # # delete_strips(mesh, [0, 3])

    # # #print(mesh.halfedge)
    # # #delete_strips(mesh, [0, 3, 5])
    # # # strips = list(mesh.strips())
    # # # for k in range(len(strips) + 1):
    # # # 	for skeys in it.combinations(strips, k):
    # # # 		try:
    # # # 			mesh2 = mesh.copy()
    # # # 			delete_strips(mesh2, list(skeys))

    # # # 		except:
    # # # 			print(skeys)
    # # # print(mesh.number_of_faces())
    # # plotter = MeshPlotter(mesh, figsize = (20, 20))
    # # plotter.draw_vertices(radius = 0.1, text='key')
    # # plotter.draw_edges()
    # # plotter.draw_faces()
    # # plotter.show()

    # mesh = CoarseQuadMesh.from_json('/Users/Robin/Desktop/debug_delete_strip_2.json')
    # mesh.collect_strips()

    # strips = list(mesh.strips())
    # print(strips)
    # for k in range(len(strips) + 1):
    #     for skeys in it.combinations(strips, k):
    #         try:
    #             mesh2 = mesh.copy()
    #             delete_strips(mesh2, list(skeys))
    #             print(mesh2.number_of_faces())
    #         except:
    #             print(skeys)

    # # plotter = MeshPlotter(mesh, figsize = (20, 20))
    # # plotter.draw_vertices(radius = 0.1, text='key')
    # # plotter.draw_edges()
    # # plotter.draw_faces()
    # # plotter.show()
