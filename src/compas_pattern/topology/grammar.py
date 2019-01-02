from compas_pattern.datastructures.mesh import Mesh
from compas_pattern.datastructures.network import Network

from compas.datastructures.mesh.operations import mesh_unweld_vertices
from compas_pattern.topology.joining_welding import mesh_unweld_edges

from compas.topology import connected_components
from compas_pattern.topology.joining_welding import network_disconnected_vertices

from compas.geometry.algorithms.smoothing import mesh_smooth_centroid

from compas.geometry import centroid_points
from compas.geometry import distance_point_point

from compas.utilities import pairwise

from compas_pattern.utilities.lists import sublist_from_to_items_in_closed_list

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
    'add_strip',
    'add_strips',
    'strips_to_split_to_preserve_boundaries_before_deleting_strips',
    'delete_strip',
    'delete_strips',
    'split_strip',
    'split_strips',
    'add_opening',
    'add_handle'
]

def edit_strips(mesh, polyedges_to_add = [], strips_to_delete = []):
    """Add and delete strips.

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    polyedges_to_add : list
        A list of polyedges to add strips.
    strips_to_delete : list
        A list of strip keys to delete.

    Returns
    -------
    new_skeys : list
        The key of the new strips.
    """

    new_skeys = add_strips(mesh, polyedges_to_add)

    strips_to_split = strips_to_split_to_preserve_boundaries_before_deleting_strips(mesh, strips_to_delete)
    split_strips(mesh, strips_to_split.keys())
    delete_strips(mesh, strips_to_delete)

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
    max_skey + 1, left_polyedge, right_polyedge : tuple
        The key of the new strip, the new strip vertices on the left, the new strip vertices on the right.

    """

    # close or open status
    closed = polyedge[0] == polyedge[-1]

    # store transversal strips to update later
    update = {mesh.edge_strip(edge): i for i, edge in enumerate(pairwise(polyedge))}
    transverse_strips = set(update.keys())

    # list faces on the left and right of the polyedge
    left_faces = [mesh.halfedge[u][v] for u, v in pairwise(polyedge)]
    right_faces = [mesh.halfedge[v][u] for u, v in pairwise(polyedge)]
    
    # add extremities for looping on data
    if closed:
        left_faces = [left_faces[-1]] + left_faces + [left_faces[0]]
        right_faces = [right_faces[-1]] + right_faces +  [right_faces[0]]
    else:
        left_faces = [None] + left_faces + [None]
        right_faces = [None] + right_faces + [None]

    # remove duplicat extremity
    if closed:
        polyedge.pop()

    # duplicate polyedge
    left_polyedge = [mesh.add_vertex(attr_dict = mesh.vertex[vkey]) for vkey in polyedge]
    right_polyedge = [mesh.add_vertex(attr_dict = mesh.vertex[vkey]) for vkey in polyedge]

    # store changes to apply all at once later
    to_substitute = {vkey: [] for vkey in polyedge}

    all_left_faces = []
    all_right_faces = []
    # collect all faces to update along polyedge with corresponding new vertex
    for i, vkey in enumerate(polyedge):
        vertex_faces = mesh.vertex_faces(vkey, ordered = True, include_none = True)
        # on the left
        faces = sublist_from_to_items_in_closed_list(vertex_faces, left_faces[i], left_faces[i + 1])
        all_left_faces += faces
        to_substitute[vkey].append((left_polyedge[i], faces))
        # on the right
        faces = sublist_from_to_items_in_closed_list(vertex_faces, right_faces[i + 1], right_faces[i])
        all_right_faces += faces
        to_substitute[vkey].append((right_polyedge[i], faces))

    all_left_faces = list(set(all_left_faces))
    all_right_faces = list(set(all_right_faces))
    left_strips = list(set([skey for fkey in all_left_faces if fkey is not None for skey in mesh.face_strips(fkey) if skey not in transverse_strips]))
    right_strips = list(set([skey for fkey in all_right_faces if fkey is not None for skey in mesh.face_strips(fkey) if skey not in transverse_strips]))

    # apply changes
    for key, substitutions in to_substitute.items():
        for substitution in substitutions:
            new_key, faces = substitution
            mesh.substitute_vertex_in_faces(key, new_key, [face for face in faces if face is not None])

    # delete old vertices
    for vkey in polyedge:
        mesh.delete_vertex(vkey)

    # add strip faces
    if closed:
        polyedge.append(polyedge[0])
        left_polyedge.append(left_polyedge[0])
        right_polyedge.append(right_polyedge[0])
    for i in range(len(polyedge) - 1):
        mesh.add_face([right_polyedge[i], right_polyedge[i + 1], left_polyedge[i + 1], left_polyedge[i]])

    # geometrical processing: smooth to widen the strip
    fixed = [vkey for vkey in mesh.vertices() if vkey not in left_polyedge and vkey not in right_polyedge]
    mesh_smooth_centroid(mesh, fixed, kmax = 3)
    
    # update transverse strip data
    for skey, i in update.items():
        mesh.strip[skey] = mesh.collect_strip(*list(pairwise(left_polyedge))[i])

    # add new strip data
    max_skey = list(mesh.strips())[-1]
    mesh.strip[max_skey + 1] = mesh.collect_strip(left_polyedge[0], right_polyedge[0])

    # update adjacent strips
    for i in range(len(polyedge)):
        old, left, right = polyedge[i], left_polyedge[i], right_polyedge[i]
        mesh.substitute_vertex_in_strips(old, left, left_strips)
        mesh.substitute_vertex_in_strips(old, right, right_strips)

    return max_skey + 1, left_polyedge, right_polyedge

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
    
        added_polyedge = polyedges.pop()
        new_skey, left_polyedge, right_polyedge = add_strip(mesh, added_polyedge)
        new_skeys.append(new_skey)
    
        # update polyedges
        new_polyedges = []
        for update_polyedge in polyedges:
        
            closed = update_polyedge[0] == update_polyedge[-1]
            if closed:
                update_polyedge.pop()
        
            new_polyedge = []
            for vkey in update_polyedge:
        
                if vkey not in added_polyedge:
                    new_polyedge.append(vkey)
        
                else:
                    idx = added_polyedge.index(vkey)
                    left_vkey = left_polyedge[idx]
                    right_vkey = right_polyedge[idx]
                    # find order
                    if left_vkey in mesh.halfedge[new_polyedge[-1]]:
                        new_polyedge += [left_vkey, right_vkey]
                    elif right_vkey in mesh.halfedge[new_polyedge[-1]]:
                        new_polyedge += [right_vkey, left_vkey]
                    else:
                        print 'missing vertices when updating polyedges to add'
                        new_polyedge.append(None)
            if closed:
                new_polyedge.append(new_polyedge[0])

            new_polyedges.append(new_polyedge)
        
        polyedges = new_polyedges

    return new_skeys

def strips_to_split_to_preserve_boundaries_before_deleting_strips(mesh, skeys):
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
        A dictionary of strip keys pointing to the number of splits to apply.

    """

    to_split = {}
    for boundary in mesh.boundaries():
        non_deleted_strips = [mesh.edge_strip((u, v)) for u, v in pairwise(boundary + boundary[:1]) if mesh.edge_strip((u, v)) not in skeys]
        
        if len(non_deleted_strips) == 0:
            return None
        
        elif len(non_deleted_strips) == 1:
            skey = non_deleted_strips[0]
            if skey in to_split:
                if to_split[skey] == 2:
                    break
                if to_split[skey] == 1:
                    to_split[skey] = 2
            else:
                to_split[skey] = 2
        
        elif len(non_deleted_strips) == 2:
            for skey in non_deleted_strips:
                if skey in to_split:
                    break
            to_split.update({skey: 1 for skey in non_deleted_strips})

    return to_split

def delete_strip(mesh, skey):
    """Delete a strip.

    Parameters
    ----------
    mesh : QuadMesh
        A quad mesh.
    skey : hashable
        A strip key.

    """

    if skey not in list(mesh.strips()):
        return 0

    old_boundary_vertices = list(mesh.vertices_on_boundary())

    # get strip data
    strip_edges = mesh.strip_edges(skey)
    strip_faces = mesh.strip_faces(skey)


    # build network between vertices of the edges of the strip to delete to get the disconnect parts of vertices to merge
    vertices = set([i for edge in strip_edges for i in edge])
    # maps between old and new indices
    old_to_new = {vkey: i for i, vkey in enumerate(vertices)}
    new_to_old = {i: vkey for i, vkey in enumerate(vertices)}
    # network
    vertex_coordinates = [mesh.vertex_coordinates(vkey) for vkey in vertices]
    edges = [(old_to_new[u], old_to_new[v]) for u, v in strip_edges]
    network = Network.from_vertices_and_edges(vertex_coordinates, edges)
    # disconnected parts
    parts = network_disconnected_vertices(network)

    # delete strip faces
    for fkey in strip_faces:
        mesh.delete_face_in_strips(fkey)
    for fkey in strip_faces:
        mesh.delete_face(fkey)

    # merge strip edge vertices that are connected
    for part in parts:
        
        # move back from network vertices to mesh vertices
        vertices = [new_to_old[vkey] for vkey in part]
        
        # skip adding a vertex if all vertices of the part are disconnected
        if any(mesh.is_vertex_connected(vkey) for vkey in vertices):

            # get position based on disconnected vertices that used to be on the boundary if any
            if any(not mesh.is_vertex_connected(vkey) for vkey in vertices):
                points = [mesh.vertex_coordinates(vkey) for vkey in vertices if not mesh.is_vertex_connected(vkey)]
            # or based on old boundary vertices if any
            elif any(vkey in old_boundary_vertices for vkey in vertices):
                points = [mesh.vertex_coordinates(vkey) for vkey in vertices if vkey in old_boundary_vertices]
            else:
                points = [mesh.vertex_coordinates(vkey) for vkey in vertices]

            # new vertex
            x, y, z = centroid_points(points)
            new_vkey = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})
            
            # replace the old vertices
            for old_vkey in vertices:
                mesh.substitute_vertex_in_strips(old_vkey, new_vkey)
                mesh.substitute_vertex_in_faces(old_vkey, new_vkey, mesh.vertex_faces(old_vkey))
        
        # delete the old vertices
        for old_vkey in vertices:
            mesh.delete_vertex(old_vkey)

    del mesh.strip[skey]

def delete_strips(mesh, skeys):
    """Delete strips.

    Parameters
    ----------
    mesh : QuadMesh
        A quad mesh.
    skey : set
        Strip keys.

    """

    for skey in skeys:
        delete_strip(mesh, skey)

def split_strip(mesh, skey):
    """Split a strip in two.

    Parameters
    ----------
    mesh : QuadMesh
        A quad mesh.
    skey : hashable
        A strip key.

    Returns
    -------
    max_skey + 1, max_skey + 2 : tuple
        The indices of the new strips.

    """

    if skey not in list(mesh.strips()):
        return 0

    strip_edges = mesh.strip_edges(skey)
    strip_faces = mesh.strip_faces(skey)

    # add new vertices for each strip edge
    new_vertices = {edge: mesh.add_vertex(attr_dict = {i: xyz for i, xyz in zip(['x', 'y', 'z'], mesh.edge_midpoint(*edge))}) for edge in strip_edges}

    # store changes and updates to make
    change = {}
    update = {}
    for u, v in strip_edges:
        if mesh.halfedge[u][v] is not None:
            # get faces to change
            fkey = mesh.halfedge[u][v]
            w, x = mesh.face_opposite_edge(u, v)
            y = new_vertices[(u, v)]
            z = new_vertices[(x, w)]
            change[fkey] = [[u, y, z, x], [y, v, w, z]]
            # get transversal strip to update
            strips = [skey_2 for skey_2 in mesh.face_strips(fkey) if skey_2 != skey]
            # check in case self-crossing strip
            if len(strips) != 0:
                skey_2 = strips[0]
                update[skey_2] = (v, w)

    # replace old faces by new ones
    for fkey, new_faces in change.items():
        mesh.delete_face(fkey)
        for new_face in new_faces:
            mesh.add_face(new_face)

    # update transversal strips
    for skey_2, edge in update.items():
        mesh.strip[skey_2] = mesh.collect_strip(*edge)
    
    # add strips
    max_skey = list(mesh.strips())[-1]
    uv, w = new_vertices.items()[0]
    mesh.strip[max_skey + 1] = mesh.collect_strip(uv[0], w)
    mesh.strip[max_skey + 2] = mesh.collect_strip(w, uv[1])
    
    # delete strip
    del mesh.strip[skey]

    return max_skey + 1, max_skey + 2

def split_strips(mesh, skeys):
    """Split strips.

    Parameters
    ----------
    mesh : QuadMesh
        A quad mesh.
    skey : set
        Strip keys.

    """

    for skey in skeys:
        split_strip(mesh, skey)

# def clear_faces(mesh, fkeys, vkeys):
#     # groups of fkeys must be a topological disc
#     # vkeys must be four vertices part of the fkeys boundary

#     vertices = [mesh.vertex_coordinates(vkey) for vkey in mesh.vertices()]
#     face_vertices = [mesh.face_vertices(fkey) for fkey in fkeys]

#     faces_mesh = PseudoQuadMesh.from_vertices_and_faces(vertices, face_vertices)
#     faces_boundary_vertices = mesh.polyedge_boundaries()[0]
#     faces_boundary_vertices = list(reversed(faces_boundary_vertices[:-1]))

#     for fkey in fkeys:
#         mesh.delete_face(fkey)

#     # orientation? reverse boundary vertices?
#     fkey = mesh.add_face(faces_boundary_vertices)

#     new_fkeys = face_propagation(mesh, fkey, vkeys)

#     return new_fkeys

def add_opening(mesh, fkey):
    """Add an opening to a mesh face.

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    fkey : hashable
        A face key.

    Returns
    -------
    list
        List of new vertex keys around the opening oriented towards the outside.

    """

    initial_vertices = mesh.face_vertices(fkey)

    new_vertices = [mesh.add_vertex(attr_dict = {i: xyz for i, xyz in zip(['x', 'y', 'z'], centroid_points([mesh.face_centroid(fkey), mesh.vertex_coordinates(vkey)]))}) for vkey in initial_vertices]

    mesh.delete_face(fkey)

    new_faces = [mesh.add_face([initial_vertices[i - 1], initial_vertices[i], new_vertices[i], new_vertices[i - 1]]) for i in range(len(initial_vertices))]

    return new_vertices

def add_handle(mesh, fkey_1, fkey_2, extremity = False):
    """Add a handle between two quad mesh faces.

    Parameters
    ----------
    mesh : QuadMesh
        A quad mesh.
    fkey_1 : hashable
        A face key.
    fkey_2 : hashable
        A face key.
    extremity : bool
        Add rings of faces at the extremitites. Default is False.

    Returns
    -------
    list
        List of new face keys around the opening

    """

    if extremity:
        # add two openings
        new_vertices_1 = add_opening(mesh, fkey_1)
        new_vertices_2 = add_opening(mesh, fkey_2)
    else:
        new_vertices_1 = list(reversed(mesh.face_vertices(fkey_1)))
        new_vertices_2 = list(reversed(mesh.face_vertices(fkey_2)))
        mesh.delete_face(fkey_1)
        mesh.delete_face(fkey_2)

    # get offset between new openings as to minimise the twist of the handle
    offset_distance = {k: sum([distance_point_point(mesh.vertex_coordinates(new_vertices_1[(i - 1) % 4]), mesh.vertex_coordinates(new_vertices_2[(- i - k) % 4])) for i in range(4)]) for k in range(4)}
    k = min(offset_distance, key = offset_distance.get)
    
    # add handle
    return [mesh.add_face([new_vertices_1[(i - 1) % 4], new_vertices_1[i], new_vertices_2[(- i - 1 - k) % 4], new_vertices_2[(- i - k) % 4]]) for i in range(4)]


# def close_opening(mesh, polyedge):
#     return 0

# def close_handle(mesh, fkeys):
#     # remove handle and close openings
#     # fkeys: closed face strip

#     if fkeys[0] == fkeys[-1]:
#         del fkeys[-1]

#     vertices = []
#     key_to_index = {}
#     for i, vkey in enumerate(mesh.vertices()):
#         vertices.append(mesh.vertex_coordinates(vkey))
#         key_to_index[vkey] = i
#     faces = [[key_to_index[vkey] for vkey in mesh.face_vertices(fkey)] for fkey in fkeys]
#     strip_mesh = Mesh.from_vertices_and_faces(vertices, faces)
    
#     boundaries = strip_mesh.polyedge_boundaries(strip_mesh)

#     for fkey in fkeys:
#         mesh.delete_face(fkey)
#     new_fkeys = []
#     for bdry in boundaries:
#         new_fkeys += close_opening(mesh, list(reversed(bdry)))

#     return new_fkeys

# def close_handle_2(mesh, edge_path_1, edge_path_2):
#     # two closed edge paths

#     # unweld
#     unweld_mesh_along_edge_path(mesh, edge_path_1)
#     unweld_mesh_along_edge_path(mesh, edge_path_2)

#     # explode
#     parts = mesh_disjointed_parts(mesh)
#     meshes = unjoin_mesh_parts(mesh, parts)

#     # find parts with the topolog of a strip: two boundary components and an EUler characteristic of 0
#     # if there are several, select the topologically smallest one (lowest number of faces)
#     index = -1
#     size = -1
#     for i, submesh in enumerate(meshes):
#         B = len(mesh.polyedge_boundaries())
#         X = submesh.mesh_euler()
#         if B == 2 and X == 0:
#             n = submesh.number_of_faces()
#             if index < 0 or n < size:
#                 index = i
#                 size = n

#     # collect the boundaries of the strip, oriented towards the outside of the strip
#     vertices = []
#     key_to_index = {}
#     for i, vkey in enumerate(mesh.vertices()):
#         vertices.append(mesh.vertex_coordinates(vkey))
#         key_to_index[vkey] = i
#     faces = [[key_to_index[vkey] for vkey in mesh.face_vertices(fkey)] for fkey in parts[index]]
#     strip_mesh = Mesh.from_vertices_and_faces(vertices, faces)
    
#     boundaries = strip_mesh.polyedge_boundaries()

#     # remove faces of the selected band
#     for fkey in parts[index]:
#         mesh.delete_face(fkey)

#     # close the two boundaries
#     new_fkeys = []
#     for bdry in boundaries:
#         new_fkeys += close_opening(mesh, list(reversed(bdry)))
        
#     return new_fkeys
    
# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
    from compas.plotters import MeshPlotter

    from compas_pattern.datastructures.mesh_quad import QuadMesh

    mesh = QuadMesh.from_obj(compas.get('quadmesh.obj'))
    mesh.collect_strips()

    # add_strip(mesh, [26,22,69,67])

    # plotter = MeshPlotter(mesh)
    # plotter.draw_vertices(text='key')
    # plotter.draw_edges()
    # plotter.draw_faces()
    # plotter.show()

