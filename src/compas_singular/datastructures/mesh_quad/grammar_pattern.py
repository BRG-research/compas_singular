from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from math import pi

from compas.datastructures import mesh_substitute_vertex_in_faces
# from compas.datastructures import mesh_unweld_vertices
from compas.datastructures import network_disconnected_nodes
from compas.datastructures import mesh_smooth_centroid
from compas.geometry import centroid_points
# from compas.geometry import project_point_line
# from compas.topology import shortest_path
# from compas.topology import connected_components
from compas.topology import breadth_first_paths
from compas.utilities import geometric_key
from compas.utilities import pairwise

from compas_singular.geometry import closest_point_on_polyline
from compas_singular.utilities import sublist_from_to_items_in_closed_list
from compas_singular.utilities import list_split

# from ..mesh import Mesh
from ..network import Network


__all__ = [
    'add_and_delete_strips',
    'add_strip',
    'add_strips',
    'delete_strip',
    'delete_strips',
    'split_strip',
    'split_strips',
    'strip_polyedge_update',
    'strips_to_split_to_prevent_boundary_collapse',
    'collateral_strip_deletions',
    'total_boundary_deletions'
]


def add_and_delete_strips(mesh, strips_to_add=[], strips_to_delete=[], preserve_boundaries=False):
    """Add and delete strips.

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    strips_to_add : list
        A list of polyedges to add strips.
    strips_to_delete : list
        A list of strip keys to delete.
    preserve_boundaries : bool
        A boolean whether to preserve boundaries that would be collapsed by refining strips without adding singularities.

    Returns
    -------
    new_skeys : list
        The key of the new strips.
    """

    new_skeys = add_strips(mesh, strips_to_add)
    delete_strips(mesh, strips_to_delete, preserve_boundaries)

    return new_skeys


def add_strip(mesh, polyedge):
    """Add a strip along a mesh polyedge.

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    polyedge : list
        List of vertex keys forming path.

    Returns
    -------
    new_skey, left_polyedge, right_polyedge : tuple
        The key of the new strip, the new strip vertices on the left, the new strip vertices on the right.

    """

    kinks_xyz = [mesh.vertex_coordinates(vkey) for vkey in mesh.boundary_kinks(pi / 12)]

    # close or open status
    closed = polyedge[0] == polyedge[-1]

    # store transversal strips to update later
    update = {mesh.edge_strip(edge): i for i,
              edge in enumerate(pairwise(polyedge))}
    transverse_strips = set(update.keys())

    # list faces on the left and right of the polyedge
    left_faces = [mesh.halfedge[u][v] for u, v in pairwise(polyedge)]
    right_faces = [mesh.halfedge[v][u] for u, v in pairwise(polyedge)]

    # add extremities for looping on data
    if closed:
        left_faces = [left_faces[-1]] + left_faces + [left_faces[0]]
        right_faces = [right_faces[-1]] + right_faces + [right_faces[0]]
    else:
        left_faces = [None] + left_faces + [None]
        right_faces = [None] + right_faces + [None]

    # remove duplicat extremity
    if closed:
        polyedge.pop()

    # duplicate polyedge
    left_polyedge = [mesh.add_vertex(
        attr_dict=mesh.vertex[vkey]) for vkey in polyedge]
    right_polyedge = [mesh.add_vertex(
        attr_dict=mesh.vertex[vkey]) for vkey in polyedge]

    # store changes to apply all at once later
    to_substitute = {vkey: [] for vkey in polyedge}

    all_left_faces = []
    all_right_faces = []
    # collect all faces to update along polyedge with corresponding new vertex
    for i, vkey in enumerate(polyedge):
        vertex_faces = mesh.vertex_faces(vkey, ordered=True, include_none=True)
        # on the left
        faces = sublist_from_to_items_in_closed_list(
            vertex_faces, left_faces[i], left_faces[i + 1])
        all_left_faces += faces
        to_substitute[vkey].append((left_polyedge[i], faces))
        # on the right
        faces = sublist_from_to_items_in_closed_list(
            vertex_faces, right_faces[i + 1], right_faces[i])
        all_right_faces += faces
        to_substitute[vkey].append((right_polyedge[i], faces))

    all_left_faces = list(set(all_left_faces))
    all_right_faces = list(set(all_right_faces))
    left_strips = list(set([skey for fkey in all_left_faces if fkey is not None for skey in mesh.face_strips(
        fkey) if skey not in transverse_strips]))
    right_strips = list(set([skey for fkey in all_right_faces if fkey is not None for skey in mesh.face_strips(
        fkey) if skey not in transverse_strips]))

    # apply changes
    for key, substitutions in to_substitute.items():
        for substitution in substitutions:
            new_key, faces = substitution
            mesh_substitute_vertex_in_faces(
                mesh, key, new_key, [face for face in faces if face is not None])

    # delete old vertices
    for vkey in polyedge:
        mesh.delete_vertex(vkey)

    # add strip faces
    if closed:
        polyedge.append(polyedge[0])
        left_polyedge.append(left_polyedge[0])
        right_polyedge.append(right_polyedge[0])
    for i in range(len(polyedge) - 1):
        mesh.add_face([right_polyedge[i], right_polyedge[i + 1],
                       left_polyedge[i + 1], left_polyedge[i]])

    # update transverse strip data
    for skey, i in update.items():
        mesh.attributes['strips'][skey] = mesh.collect_strip(
            *list(pairwise(left_polyedge))[i])

    # add new strip data
    new_skey = list(mesh.strips())[-1] + 1
    mesh.attributes['strips'][new_skey] = mesh.collect_strip(
        left_polyedge[0], right_polyedge[0])

    # update adjacent strips
    for i in range(len(polyedge)):
        old, left, right = polyedge[i], left_polyedge[i], right_polyedge[i]
        mesh.substitute_vertex_in_strips(old, left, left_strips)
        mesh.substitute_vertex_in_strips(old, right, right_strips)

    func_1(mesh, kinks_xyz, 20, 0.5)

    return new_skey, left_polyedge, right_polyedge


def func_1(mesh, fix_xyz, kmax, damping):
    # geometrical processing: smooth to widen the strip with constraints at
    # kinks and along boundaries

    def callback(k, args):

        mesh, fixed, split_boundaries, split_boundaries_geom = args

        for vkey in mesh.vertices_on_boundaries():
            if vkey not in fixed:
                for i, boundary in enumerate(split_boundaries):
                    if vkey in boundary:
                        xyz, dist = closest_point_on_polyline(split_boundaries_geom[i], mesh.vertex_coordinates(vkey))
                        attr = mesh.vertex[vkey]
                        attr['x'], attr['y'], attr['z'] = xyz
                        break

    fix_map = {geometric_key(xyz): [] for xyz in fix_xyz}
    for vkey in mesh.vertices():
        geom_key = geometric_key(mesh.vertex_coordinates(vkey))
        if geom_key in fix_map:
            fix_map[geom_key].append(vkey)

    fixed = []
    for vertices in fix_map.values():
        boundary_vertices = [vkey for vkey in vertices if mesh.is_vertex_on_boundary(vkey)]
        if len(boundary_vertices) == 0:
            print('not adapted to fixed non-boundary vertices')
        elif len(boundary_vertices) == 1:
            fixed += boundary_vertices
        else:
            corner_vertices = [vkey for vkey in boundary_vertices if mesh.vertex_degree(vkey) == 2]
            if len(corner_vertices) == 1:
                fixed += corner_vertices
            else:
                pass
                # print('not generalised yet')

    split_boundaries = []
    for boundary in mesh.boundaries():
        boundary.append(boundary[0])
        indices = [boundary.index(vkey) for vkey in fixed if vkey in boundary]
        split_boundaries += list_split(boundary, indices)
    split_boundaries_geom = {i: [mesh.vertex_coordinates(vkey) for vkey in boundary] for i, boundary in enumerate(split_boundaries)}

    callback_args = mesh, fixed, split_boundaries, split_boundaries_geom
    mesh_smooth_centroid(mesh, fixed, kmax=kmax, damping=damping, callback=callback, callback_args=callback_args)


def add_strips(mesh, polyedges):
    """Add strips along mesh polyedges.

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    polyedges : list
        List of polyedges as lists of vertex keys forming path.

    Returns
    -------
    new_skeys : list
        The list of new strip keys.

    """

    new_skeys = []

    while len(polyedges) > 0:
        polyedge = polyedges.pop()
        new_skey, left_polyedge, right_polyedge = add_strip(mesh, polyedge)
        new_skeys.append(new_skey)
        vertex_modifications = {vkey: [left_polyedge[i], right_polyedge[i]] for i, vkey in enumerate(polyedge)}
        polyedges = [strip_polyedge_update(mesh, polyedge, vertex_modifications) for polyedge in polyedges]

    return new_skeys


def delete_strip(mesh, skey, preserve_boundaries=False):
    """Delete a strip.

    Parameters
    ----------
    mesh : QuadMesh
        A quad mesh.
    skey : hashable
        A strip key.
    preserve_boundaries : bool
        A boolean whether to preserve boundaries that would be collapsed by refining strips without adding singularities.

    Returns
    -------
    skey_to_skeys : dict, None
        If strip splits were applied to preserve boundaries, a dictionary of the initial strip key to the refining strip keys. None otherwise.

    """

    if skey not in list(mesh.strips()):
        return 0

    # if preserve_boundaries:
    #     skey_to_skeys = split_strips(mesh, boundary_strip_preserve(mesh, [skey]))

    old_boundary_vertices = list(mesh.vertices_on_boundaries())

    # get strip data
    strip_edges = mesh.strip_edges(skey)
    strip_faces = mesh.strip_faces(skey)

    # collateral strip deletions
    collateral_deleted_strips = []
    # print('strip_faces: ', strip_faces)
    for skey_2 in mesh.strips():
        if skey_2 == skey:
            continue
        # print('strip_faces_2: ', mesh.strip_faces(skey_2), [mesh.strip_faces(skey_2) in strip_faces])
        if all([fkey in strip_faces for fkey in mesh.strip_faces(skey_2)]):
            collateral_deleted_strips.append(skey_2)
    # print('collateral_deleted_strips: ', collateral_deleted_strips)

    # build network between vertices of the edges of the strip to delete to
    # get the disconnect parts of vertices to merge
    vertices = set([i for edge in strip_edges for i in edge])
    # maps between old and new indices
    old_to_new = {vkey: i for i, vkey in enumerate(vertices)}
    new_to_old = {i: vkey for i, vkey in enumerate(vertices)}
    # network
    vertex_coordinates = {i: mesh.vertex_coordinates(vkey) for i, vkey in enumerate(vertices)}
    edges = [(old_to_new[u], old_to_new[v]) for u, v in strip_edges]
    network = Network.from_nodes_and_edges(vertex_coordinates, edges)
    # disconnected parts
    parts = network_disconnected_nodes(network)

    # delete strip faces
    for fkey in strip_faces:
        mesh.delete_face_in_strips(fkey)
    for fkey in strip_faces:
        mesh.delete_face(fkey)

    old_vkeys_to_new_vkeys = {}

    # merge strip edge vertices that are connected
    for part in parts:

        # move back from network vertices to mesh vertices
        vertices = [new_to_old[vkey] for vkey in part]

        # skip adding a vertex if all vertices of the part are disconnected
        if any(mesh.is_vertex_connected(vkey) for vkey in vertices):

            # get position based on disconnected vertices that used to be on
            # the boundary if any
            if any(not mesh.is_vertex_connected(vkey) for vkey in vertices):
                points = [mesh.vertex_coordinates(
                    vkey) for vkey in vertices if not mesh.is_vertex_connected(vkey)]
            # or based on old boundary vertices if any
            elif any(vkey in old_boundary_vertices for vkey in vertices):
                points = [mesh.vertex_coordinates(
                    vkey) for vkey in vertices if vkey in old_boundary_vertices]
            else:
                points = [mesh.vertex_coordinates(vkey) for vkey in vertices]

            # new vertex
            x, y, z = centroid_points(points)
            new_vkey = mesh.add_vertex(attr_dict={'x': x, 'y': y, 'z': z})
            old_vkeys_to_new_vkeys.update({old_vkey: new_vkey for old_vkey in vertices})

            # replace the old vertices
            for old_vkey in vertices:
                mesh.substitute_vertex_in_strips(old_vkey, new_vkey)
                mesh_substitute_vertex_in_faces(
                    mesh, old_vkey, new_vkey, mesh.vertex_faces(old_vkey))

        # delete the old vertices
        for old_vkey in vertices:
            mesh.delete_vertex(old_vkey)

    # delete data of deleted strip and collateral deleted strips
    del mesh.attributes['strips'][skey]
    for skey_2 in collateral_deleted_strips:
        del mesh.attributes['strips'][skey_2]
    # print(old_vkeys_to_new_vkeys)
    # print(mesh.attributes['face_pole'])
    if 'face_pole' in mesh.attributes:
        for fkey, pole in mesh.attributes['face_pole'].items():
            if fkey in mesh.attributes['face_pole']:
                # print(fkey, pole, mesh.attributes['face_pole'])
                if pole == mesh.attributes['face_pole'][fkey]:
                    if pole in old_vkeys_to_new_vkeys:
                        mesh.attributes['face_pole'][fkey] = old_vkeys_to_new_vkeys[pole]

    return old_vkeys_to_new_vkeys


def delete_strips(mesh, skeys, preserve_boundaries=False):
    """Delete strips.

    Parameters
    ----------
    mesh : QuadMesh
        A quad mesh.
    skey : set
        Strip keys.
    preserve_boundaries : bool
        A boolean whether to preserve boundaries that would be collapsed by refining strips without adding singularities.

    Returns
    -------
    skey_to_skeys : dict, None
        If strip splits were applied to preserve boundaries, a dictionary of the initial strip key to the refining strip keys. None otherwise.

    """

    if preserve_boundaries:
        skey_to_skeys = split_strips(mesh, strips_to_split_to_prevent_boundary_collapse(mesh, skeys))

    for skey in skeys:
        delete_strip(mesh, skey)

    if preserve_boundaries:
        return skey_to_skeys


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
            return {}

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


def split_strip(mesh, skey, n=2):
    """Refine a strip in n strips.

    Parameters
    ----------
    mesh : QuadMesh
        A quad mesh.
    skey : hashable
        A strip key.
    n : int
        The refinement value.
        Default value is two

    Returns
    -------
    list
        The index of the existing strip and the n - 1 new strips.

    """

    return [skey] + [add_strip(mesh, mesh.strip_side_polyedges(skey)[0])[0] for i in range(n - 1)]


def split_strips(mesh, skey_to_n):
    """Refine strips in n strips each.

    Parameters
    ----------
    mesh : QuadMesh
        A quad mesh.
    skey_to_n : dict
        Dictionary of strip keys to refine pointing to refinement value.

    Returns
    -------
    dict
        A dictionary of keys of strips to split pointing to the refining strip keys.

    """

    return {skey: split_strip(mesh, skey, n) for skey, n in skey_to_n.items()}


def strip_polyedge_update(mesh, polyedge, vertex_modifications):
    """Update a polyedge in mesh that has been modified.

    Parameters
    ----------
    mesh : QuadMesh
        A quad mesh.
    polyedge : list
        A polyedge as a list of (old) vertex keys.
    vertex_modifications : dict
         A dictionary showing the vertex modifications, old vertex keys pointing to the new vertex keys.

    Returns
    -------
    shortest_polyedge: list
        The updated polyedge as a list of vertex keys.

    """

    closed = polyedge[0] == polyedge[-1]

    if closed:
        polyedge = polyedge[:-1]

    # update polyedge with candidate vertices
    polyedge_modifications = {vkey: (vertex_modifications[vkey] if vkey in vertex_modifications else [vkey]) for vkey in polyedge}
    # list all candidate vertices to form new polyedge
    candidate_vertices = tuple(set([vkey for vkeys in polyedge_modifications.values() for vkey in vkeys]))
    # adjacency restricted to candidate vertices
    adjacency = {vkey: [nbr for nbr in mesh.vertex_neighbors(vkey) if nbr in candidate_vertices] for vkey in mesh.vertices() if vkey in candidate_vertices}

    # for each combination of boundary vertex extremities, get the shortest
    # valid path through the modified vertices of the polyedges
    shortest_polyedge = None
    # start vertices on boundary
    for vkey_start in polyedge_modifications[polyedge[0]]:
        if mesh.is_vertex_on_boundary(vkey_start):
            # end vertices on boundary
            for vkey_end in polyedge_modifications[polyedge[-1]]:
                if mesh.is_vertex_on_boundary(vkey_end):
                    # iterate through all paths between start and end vertices
                    # starting by the shortest
                    for candidate_polyedge in breadth_first_paths(adjacency, vkey_start, vkey_end):
                        is_valid = True
                        # if was initailly closed, make sure that temporary end
                        # is adjacent to start
                        if closed:
                            if candidate_polyedge[0] not in mesh.vertex_neighbors(candidate_polyedge[-1]):
                                continue
                        # check that vertices in path come from the modified
                        # vertices of the polyedge in the same order
                        i = 0
                        for vkey in candidate_polyedge:
                            if vkey in polyedge_modifications[polyedge[i]]:
                                continue
                            elif vkey in polyedge_modifications[polyedge[i + 1]]:
                                i += 1
                            else:
                                is_valid = False
                                break
                        # update if shorter
                        if is_valid:
                            if shortest_polyedge is None or len(shortest_polyedge) > len(candidate_polyedge):
                                shortest_polyedge = candidate_polyedge
                            break

    if closed:
        shortest_polyedge.append(shortest_polyedge[0])

    return shortest_polyedge


def collateral_strip_deletions(mesh, skeys):
    """Return the strips that would be deleted from the deletion of other strips.
    """

    deleted_fkeys = [fkey for skey in skeys for fkey in mesh.strip_faces(skey)]
    return [skey for skey in mesh.strips() if skey not in skeys and all([fkey in deleted_fkeys for fkey in mesh.strip_faces(skey)])]


def total_boundary_deletions(mesh, skeys):
    """Return the strips that would be deleted from the deletion of other strips.
    """

    deleted_strips = list(skeys) + list(collateral_strip_deletions(mesh, skeys))
    deleted_boundaries = []
    deleted_edges = set([edge for skey in deleted_strips for edge in mesh.strip_edges(skey)])
    for boundary in mesh.boundaries():
        edges = [(u, v) for u, v in pairwise(boundary + boundary[:1])]
        if all([(u, v) in deleted_edges or (v, u) in deleted_edges for u, v in edges]):
            deleted_boundaries.append(boundary)
    return deleted_boundaries


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass

    # import compas
    # from compas_plotters.meshplotter import MeshPlotter

    # from compas_singular.datastructures.mesh_quad.mesh_quad import QuadMesh

    # #mesh = QuadMesh.from_obj(compas.get('quadmesh.obj'))

    # #adjacency = {0: {1: None, 3: None}, 1: {2: None, 0: None}, 2: {3: None, 1: None}, 3: {0: None, 2: None}}
    # # for i, path in enumerate(breadth_first_paths(adjacency, 0, 0)):
    # #    print path
    # #    if i == 1:
    # #        break
    # # add_strip(mesh, [26,22,69,67])

    # # vertices = [
    # #     [0.0, 0.0, 0.0],
    # #     [1.0, 0.0, 0.0],
    # #     [2.0, 0.0, 0.0],
    # #     [0.0, 1.0, 0.0],
    # #     [1.0, 1.0, 0.0],
    # #     [2.0, 1.0, 0.0],
    # #     [0.0, 2.0, 0.0],
    # #     [1.0, 2.0, 0.0],
    # #     [2.0, 2.0, 0.0]
    # # ]

    # # faces = [
    # #     [0, 1, 4, 3],
    # #     [1, 2, 5, 4],
    # #     [3, 4, 7, 6],
    # #     [4, 5, 8, 7]
    # # ]

    # # mesh = QuadMesh.from_vertices_and_faces(vertices, faces)
    # # add_strip_wip(mesh, [3, 4, 5])

    # # plotter = MeshPlotter(mesh, figsize=(5.0, 5.0))
    # # plotter.draw_vertices(text='key')
    # # plotter.draw_edges()
    # # plotter.draw_faces()
    # # plotter.show()

    # vertices = [
    #     [0.0, 0.0, 0.0],
    #     [1.0, 0.0, 0.0],
    #     [1.0, 1.0, 0.0],
    #     [0.0, 1.0, 0.0],
    # ]

    # faces = [
    #     [0, 1, 2, 3],
    # ]

    # mesh = QuadMesh.from_vertices_and_faces(vertices, faces)
    # mesh.collect_strips()

    # print(total_boundary_deletions(mesh, [0, 1]))
    # print(collateral_strip_deletions(mesh, [0]))
