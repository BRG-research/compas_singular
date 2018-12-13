from compas_pattern.datastructures.mesh import Mesh
from compas_pattern.datastructures.network import Network

from compas_pattern.topology.joining_welding import mesh_unweld_edges

from compas.topology import connected_components
from compas_pattern.topology.joining_welding import network_disconnected_vertices

from compas.geometry.algorithms.smoothing import mesh_smooth_centroid

from compas.geometry import centroid_points
from compas.geometry import distance_point_point

from compas.utilities import pairwise

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
    'add_strip',
    'strips_to_split_to_preserve_boundaries_before_deleting_strips',
    'delete_strip',
    'delete_strips',
    'split_strip',
    'add_opening',
    'add_handle'
]

def add_strip(mesh, polyedge):
    """Add a strip along a mesh polyedge.

    WIP!

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    polyedge : list
        List of vertex keys forming path.

    Returns
    -------

    """

    return 0

    # vertex_changes = mesh_unweld_edges(mesh, [(u, v) for u, v in pairwise(polyedge)])
    # new_vertices = [vkey for vkeys in vertex_changes.values() for vkey in vkeys]

    # components = connected_components(mesh.adjacency)




    # strip_faces = []
    # new_polyedge = []
    # for i in range(len(polyedge) - 2):
        
    #     # unweld between two edges
    #     u, v, w = polyedge[i : i + 3]
    #     v2 = mesh_unweld_edges(mesh, [(u,v), (v,w)])[v]
    #     new_polyedge.append(v2)

    #     # remove last face from strip
    #     if i == 0:
    #         strip_faces += [mesh.add_face([v, u, v2]), mesh.add_face([v, w, w])]

    #     elif i == len(polyedge) - 2:
    #         mesh.delete_face(strip_faces[-1])
    #         strip_faces += [mesh.add_face([v, u, u2, v2]), mesh.add_face([v, w, w])]

    #     else:
    #         mesh.delete_face(strip_faces[-1])
    #         u2 = new_polyedge[-2]
    #         strip_faces += [mesh.add_face([v, u, u2, v2]), mesh.add_face([v, v2, w])]

    # fixed_vertices = list(mesh.vertices())
    # for vkey in list(set(polyedge + new_polyedge)):
    #         fixed_vertices.remove(vkey)

    # if mesh.is_vertex_on_boundary(polyedge[0]):
    #     mesh_unweld_edges(mesh, [(polyedge[0],polyedge[1])])
        
    # mesh_smooth_centroid(mesh, fixed = fixed_vertices, kmax = 5)

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

def add_handle(mesh, fkey_1, fkey_2):
    """Add a handle between two quad mesh faces.

    Parameters
    ----------
    mesh : QuadMesh
        A quad mesh.
    fkey_1 : hashable
        A face key.
    fkey_2 : hashable
        A face key.

    Returns
    -------
    list
        List of new face keys around the opening

    """

    # add two openings
    new_vertices_1 = add_opening(mesh, fkey_1)
    new_vertices_2 = add_opening(mesh, fkey_2)

    # get offset between new openings as to minimise the twist of the handle
    offset_distance = {k: sum([distance_point_point(mesh.vertex_coordinates(new_vertices_1[(i - 1) % 4]), mesh.vertex_coordinates(new_vertices_2[(- i - k) % 4])) for i in range(4)]) for k in range(4)}
    k = min(offset_distance, key = offset_distance.get)
    
    # add handle
    return [mesh.add_face([new_vertices_1[(i - 1) % 4], new_vertices_1[i], new_vertices_2[(- i - 1 - k) % 4], new_vertices_2[(- i - k) % 4]]) for i in range(4)]

    
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

    mesh = Mesh.from_obj(compas.get('quadmesh.obj'))
    
    #add_strip(mesh, [26,22,69,67])

    #plotter = MeshPlotter(mesh)
    #plotter.draw_vertices(text='key')
    #plotter.draw_edges()
    #plotter.draw_faces()
    #plotter.show()

