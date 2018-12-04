from compas_pattern.datastructures.mesh import Mesh
from compas.datastructures.network import Network

from compas_pattern.topology.joining_welding import mesh_unweld_edges
from compas_pattern.topology.joining_welding import network_disconnected_vertices

from compas.geometry.algorithms.smoothing import mesh_smooth_centroid

#from compas_pattern.topology.grammar_high_level import simple_split
#from compas_pattern.topology.global_propagation import mesh_propagation

from compas.geometry import scale_vector
from compas.geometry import sum_vectors
from compas.geometry import centroid_points

from compas.geometry import offset_polyline

from compas.utilities import pairwise

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
    'add_strip',
    'delete_strip',
    'split_strip',
    'add_handle',
    'delete_handle',
    'face_strip_collapse',
    'multiple_strip_collapse',
    'face_strip_subdivide',
    'face_strips_merge',
    'face_strip_insert',
]

def add_strip(mesh, polyedge):
    """Add a strip along a polyedge.

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    polyedge : list
        List of vertex keys forming path.

    Returns
    -------

    """

    strip_faces = []
    new_polyedge = []
    for i in range(len(polyedge) - 2):
        
        # unweld between two edges
        u, v, w = polyedge[i : i + 3]
        v2 = mesh_unweld_edges(mesh, [(u,v), (v,w)])[v]
        new_polyedge.append(v2)

        # remove last face from strip
        if i == 0:
            strip_faces += [mesh.add_face([v, u, v2]), mesh.add_face([v, w, w])]

        elif i == len(polyedge) - 2:
            mesh.delete_face(strip_faces[-1])
            strip_faces += [mesh.add_face([v, u, u2, v2]), mesh.add_face([v, w, w])]

        else:
            mesh.delete_face(strip_faces[-1])
            u2 = new_polyedge[-2]
            strip_faces += [mesh.add_face([v, u, u2, v2]), mesh.add_face([v, v2, w])]

    fixed_vertices = list(mesh.vertices())
    for vkey in list(set(polyedge + new_polyedge)):
            fixed_vertices.remove(vkey)

    if mesh.is_vertex_on_boundary(polyedge[0]):
        mesh_unweld_edges(mesh, [(polyedge[0],polyedge[1])])
        
    mesh_smooth_centroid(mesh, fixed = fixed_vertices, kmax = 5)

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


    # edges_to_collapse = [edge for edge, strip in edges_to_strips.items() if strip in strips_to_collapse]

    # # refine boundaries to avoid collapse
    # to_subdivide = []
    # for boundary in mesh_boundaries(mesh):
    #     boundary_edges = [(boundary[i], boundary[i + 1]) for i in range(len(boundary) - 1)]
    #     boundary_edges_to_collapse = [edge for edge in edges_to_collapse if edge in boundary_edges or edge[::-1] in boundary_edges]
    #     if len(boundary_edges) - len(boundary_edges_to_collapse) < 3:
    #         for edge in boundary_edges:
    #             if edge not in boundary_edges_to_collapse and edge[::-1] not in boundary_edges_to_collapse:
    #                 if edge not in to_subdivide and edge[::-1] not in to_subdivide:
    #                     to_subdivide.append(edge)
    # # refine pole points to avoid collapse
    # poles = {u: [] for u, v in mesh.edges() if u == v}
    # for u, v in edges_to_collapse:
    #     for pole in poles:
    #         if pole in mesh.halfedge[u] and pole in mesh.halfedge[v]:
    #             poles[pole].append((u, v))
    # for pole, pole_edges_to_collapse in poles.items():
    #     vertex_faces = list(set(mesh.vertex_faces(pole)))
    #     if not mesh.is_vertex_on_boundary(pole):
    #         if len(vertex_faces) - len(pole_edges_to_collapse) < 3:
    #             for fkey in vertex_faces:
    #                 face_vertices = copy.copy(mesh.face_vertices(fkey))
    #                 face_vertices.remove(pole)
    #                 face_vertices.remove(pole)
    #                 u, v = face_vertices
    #                 if (u, v) not in pole_edges_to_collapse and (v, u) not in pole_edges_to_collapse:
    #                     if (u, v) not in to_subdivide and (v, u) not in to_subdivide:
    #                         to_subdivide.append((u, v))


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

def clear_faces(mesh, fkeys, vkeys):
    # groups of fkeys must be a topological disc
    # vkeys must be four vertices part of the fkeys boundary

    vertices = [mesh.vertex_coordinates(vkey) for vkey in mesh.vertices()]
    face_vertices = [mesh.face_vertices(fkey) for fkey in fkeys]

    faces_mesh = PseudoQuadMesh.from_vertices_and_faces(vertices, face_vertices)
    faces_boundary_vertices = mesh.polyedge_boundaries()[0]
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
    faces_1 = add_opening(mesh, fkey_1)
    # find newly added vertices
    vertices_1 = [vkey for vkey in mesh.vertices() if vkey not in vertices]

    # add second opening
    faces_2 = add_opening(mesh, fkey_2)
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
    
    boundaries = strip_mesh.polyedge_boundaries(strip_mesh)

    for fkey in fkeys:
        mesh.delete_face(fkey)
    new_fkeys = []
    for bdry in boundaries:
        new_fkeys += close_opening(mesh, list(reversed(bdry)))

    return new_fkeys

def close_handle_2(mesh, edge_path_1, edge_path_2):
    # two closed edge paths

    # unweld
    unweld_mesh_along_edge_path(mesh, edge_path_1)
    unweld_mesh_along_edge_path(mesh, edge_path_2)

    # explode
    parts = mesh_disjointed_parts(mesh)
    meshes = unjoin_mesh_parts(mesh, parts)

    # find parts with the topolog of a strip: two boundary components and an EUler characteristic of 0
    # if there are several, select the topologically smallest one (lowest number of faces)
    index = -1
    size = -1
    for i, submesh in enumerate(meshes):
        B = len(mesh.polyedge_boundaries())
        X = submesh.mesh_euler()
        if B == 2 and X == 0:
            n = submesh.number_of_faces()
            if index < 0 or n < size:
                index = i
                size = n

    # collect the boundaries of the strip, oriented towards the outside of the strip
    vertices = []
    key_to_index = {}
    for i, vkey in enumerate(mesh.vertices()):
        vertices.append(mesh.vertex_coordinates(vkey))
        key_to_index[vkey] = i
    faces = [[key_to_index[vkey] for vkey in mesh.face_vertices(fkey)] for fkey in parts[index]]
    strip_mesh = Mesh.from_vertices_and_faces(vertices, faces)
    
    boundaries = strip_mesh.polyedge_boundaries()

    # remove faces of the selected band
    for fkey in parts[index]:
        mesh.delete_face(fkey)

    # close the two boundaries
    new_fkeys = []
    for bdry in boundaries:
        new_fkeys += close_opening(mesh, list(reversed(bdry)))
        
    return new_fkeys
    
# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
    from compas.plotters import MeshPlotter

    #mesh = Mesh.from_obj(compas.get('quadmesh.obj'))

    #add_strip(mesh, [26,22,69,67])

    #plotter = MeshPlotter(mesh)
    #plotter.draw_vertices(text='key')
    #plotter.draw_edges()
    #plotter.draw_faces()
    #plotter.show()

