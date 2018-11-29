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

    """

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
    strip_1 = [(edge_vkeys[0], new_vkey) for edge_vkeys, new_vkey in new_vertices.items()]
    strip_2 = [(new_vkey, edge_vkeys[1]) for edge_vkeys, new_vkey in new_vertices.items()]
    mesh.strip.update({max_skey + 1: strip_1, max_skey + 2: strip_2})
    
    # delete strip
    del mesh.strip[skey]

def multiple_strip_collapse(cls, mesh, edges_to_collapse):
    """Collapse a multiple strips in a quad mesh.

    Parameters
    ----------
    mesh : Mesh
        A quad mesh.
    edges: list
        List of edges as tuples (u, v).

    Returns
    -------
    mesh : mesh, None
        The modified quad mesh.
        None if mesh is not a quad mesh or if edges are invalid or ifcollapses all edges of a boundary.

    """

    max_group = mesh.collect_strip_edge_attribute()
    edge_groups = mesh.edges_to_strips_dict()
    boundaries = mesh.polyedge_boundaries()

    # remove edges with redundant strips
    strips_to_collapse = {}
    for u, v in edges_to_collapse:
        group = edge_groups[(u, v)]
        if group not in strips_to_collapse:
            strips_to_collapse[group] = [(u, v)]
        else:
            strips_to_collapse[group].append((u, v))
    edges_to_collapse = [edges[0] for group, edges in strips_to_collapse.items()]

    # all edges which will be collapsed
    all_edges_to_collapse = [edge for edge, group in edge_groups.items() if group in strips_to_collapse.keys()]

    # subdivide boundaries if would be collapsed
    for boundary in boundaries:
        boundary_edges = [(boundary[i], boundary[i + 1]) for i in range(len(boundary) - 1)]
        to_collapse = [edge for edge in all_edges_to_collapse if edge in boundary_edges or edge[::-1] in boundary_edges]
        delta = len(boundary) - len(to_collapse)
        # need one remaining edge
        if delta < 1:
            return None
        count = 10
        while delta < 3 and count > 0:
            count -= 1
            for edge in boundary_edges:
                # missing: if edges in same strip?
                if edge not in to_collapse and edge[::-1] not in to_collapse:
                    u, v = edge
                    face_strip_subdivide(cls, mesh, u, v)
                    delta += 1

    # collapse all strips
    for strip in strips_to_collapse:
        modified = False
        for edge, group in edge_groups.items():
            if group == strip:
                u, v = edge
                # update edge groups
                edge_groups = face_strip_collapse(cls, mesh, u, v)
                modified = True
                if edge_groups is None:
                    print '!'
                break
        if not modified:
            print '!!'

    return mesh

def face_strips_merge(mesh, u, v):
    """Merge two parallel face strips in a quad mesh. The polyedge inbetween is composed of regular vertices only.

    Parameters
    ----------
    mesh : Mesh
        A quad mesh.
    u: int
        Start vertex key of an edge of the polyedge.
    v: int
        End vertex key of an edge of the polyedge.

    Returns
    -------
    mesh : mesh, None
        The modified quad mesh.
        None if mesh is not a quad mesh or if (u, v) is on boundary or if (u,v) is not on a polyedge with only regular vertices.

    """

    # check
    if not mesh.is_quadmesh():
        return None
    if mesh.is_edge_on_boundary(u, v):
        return None

    # get polyedge
    polylines = mesh.collect_quad_polyedges()
    for polyline in polylines:
        for i in range(len(polyline) - 1):
            if (u == polyline[i] and v == polyline[i + 1]) or (v == polyline[i] and u == polyline[i + 1]):
                polyedge = polyline

    # check
    for vkey in polyedge:
        if (mesh.is_vertex_on_boundary(vkey) and len(mesh.vertex_neighbors(vkey)) != 3) or (not mesh.is_vertex_on_boundary(vkey) and len(mesh.vertex_neighbors(vkey)) != 4): 
            return None


    # store faces of new face strip
    faces = []

    for i in range(len(polyedge) - 1):
        
        # per edge
        u, v = polyedge[i], polyedge[i + 1]
        
        # get adajcent faces
        fkey_1 = mesh.halfedge[u][v]
        fkey_2 = mesh.halfedge[v][u]

        # collect vertices of new face
        a = mesh.face_vertex_descendant(fkey_1, v)
        b = mesh.face_vertex_descendant(fkey_1, a)
        c = mesh.face_vertex_descendant(fkey_2, u)
        d = mesh.face_vertex_descendant(fkey_2, c)

        # delete old faces
        mesh.delete_face(fkey_1)
        mesh.delete_face(fkey_2)

        # add new face
        fkey = mesh.add_face([a, b, c, d])
        faces.append(fkey)

    return faces

def face_strip_insert_2(mesh, vertex_path, factor = .33):

    # check if vertex_path is a loop
    if vertex_path[0] == vertex_path[-1]:
        loop = True
    else:
        loop = False

    edge_path = [[vertex_path[i], vertex_path[i + 1]] for i in range(len(vertex_path) - 1)]
    if loop:
        del edge_path[-1]

    # duplicate the vertices along the edge_path by unwelding the mesh
    duplicates = unweld_mesh_along_edge_path(mesh, edge_path)

    duplicate_list = [i for uv in duplicates for i in uv]

    # move the duplicated vertices towards the centroid of the adjacent faces
    for uv in duplicates:
        for vkey in uv:
            # if was on boundary before unwelding, move along boundary edge
            on_boundary = False
            for nbr in mesh.vertex_neighbors(vkey):
                if mesh.is_edge_on_boundary(vkey, nbr) and nbr not in duplicate_list:
                    x, y, z = mesh.edge_point(vkey, nbr, factor)
                    on_boundary = True
            if not on_boundary:
                centroids = [mesh.face_centroid(fkey) for fkey in mesh.vertex_faces(vkey)]
                areas = [mesh.face_area(fkey) for fkey in mesh.vertex_faces(vkey)]
                #if len(centroids) != 0:
                x, y, z = sum_vectors([scale_vector(centroid, area / sum(areas)) for centroid, area in zip(centroids, areas)])
                attr = mesh.vertex[vkey]
                # factor related to the width of the new face strip compared to the adjacent ones
                attr['x'] += factor * (x - attr['x'])
                attr['y'] += factor * (y - attr['y'])
                attr['z'] += factor * (z - attr['z'])

    # add new face strip
    for i in range(len(duplicates) - 1):
        a = duplicates[i][1]
        b = duplicates[i][0]
        c = duplicates[i + 1][0]
        d = duplicates[i + 1][1]
        mesh.add_face([a, b, c, d])
    # close if loop
    if loop:
        a = duplicates[-1][1]
        b = duplicates[i-1][0]
        c = duplicates[0][0]
        d = duplicates[0][1]
        mesh.add_face([a, b, c, d])


    return 0

def face_strip_insert(mesh, vertex_path, pole_extremities, factor = .33):

    # duplicate twice vertices on vertex path
    duplicated_vertices = {}
    for vkey in vertex_path:
        # if closed vertex path, end already included
        if vkey in duplicated_vertices:
            continue
        x, y, z = mesh.vertex_coordinates(vkey)
        vkey_1 = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})
        vkey_2 = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})
        duplicated_vertices[vkey] = [vkey_1, vkey_2]

    new_faces = []

    # move along edge path
    for i in range(0, len(vertex_path) - 1):
        
        u = vertex_path[i]
        v = vertex_path[i + 1]

        if v in mesh.halfedge[u]:
            fkey_left = mesh.halfedge[u][v]
        else:
            fkey_left = None
        if u in mesh.halfedge[v]:
            fkey_right = mesh.halfedge[v][u]
        else:
            fkey_right = None

        # update faces adjacent to vertex path
        if fkey_left is not None:
            face_vertices = [duplicated_vertices[vkey][0] if vkey in duplicated_vertices else vkey for vkey in mesh.face_vertices(fkey_left)]
            mesh.delete_face(fkey_left)
            mesh.add_face(face_vertices, fkey_left)
        if fkey_right is not None:
            face_vertices = [duplicated_vertices[vkey][1] if vkey in duplicated_vertices else vkey for vkey in mesh.face_vertices(fkey_right)]
            mesh.delete_face(fkey_right)
            mesh.add_face(face_vertices, fkey_right)
        
        # add strip
        face_vertices = [duplicated_vertices[u][1], duplicated_vertices[v][1], duplicated_vertices[v][0], duplicated_vertices[u][0]]
        new_faces.append(mesh.add_face(face_vertices))

    # delete old vertices
    # remove end if closed vertex path
    if vertex_path[0] == vertex_path[-1]:
        culled_verted_vertex_path = vertex_path[:-1]
    else:
        culled_verted_vertex_path = vertex_path
    for vkey in culled_verted_vertex_path:
        if len(mesh.vertex_faces(vkey)) > 0:
            faces = [mesh.halfedge[vkey][a] for a in mesh.vertex_neighbors(vkey) if mesh.halfedge[vkey][a] is not None]
            count = len(faces) * 2
            while len(faces) > 0 and count > 0:
                for fkey in faces:
                    for fkey_2 in [fkey_3 for vkey_2 in mesh.face_vertices(fkey) for fkey_3 in mesh.vertex_faces(vkey_2)]:
                        if duplicated_vertices[vkey][0] in mesh.face_vertices(fkey_2):
                            duplicate = duplicated_vertices[vkey][0]
                            face_vertices = [duplicate if key == vkey else key for key in mesh.face_vertices(fkey)]
                            mesh.delete_face(fkey)
                            mesh.add_face(face_vertices, fkey)
                            faces.remove(fkey)
                            break
                        if duplicated_vertices[vkey][1] in mesh.face_vertices(fkey_2):
                            duplicate = duplicated_vertices[vkey][1]
                            face_vertices = [duplicate if key == vkey else key for key in mesh.face_vertices(fkey)]
                            mesh.delete_face(fkey)
                            mesh.add_face(face_vertices, fkey)
                            faces.remove(fkey)
                            break
                    if fkey not in faces:
                        break
        mesh.delete_vertex(vkey)

    # transform pole extemities
    for vkey, is_pole in zip([vertex_path[0], vertex_path[-1]], pole_extremities):
        if is_pole:
            u, v = duplicated_vertices[vkey]
            for fkey in mesh.vertex_faces(v):
                if fkey is not None:
                    new_face_vertices = [u if vkey_2 == v else vkey_2 for vkey_2 in mesh.face_vertices(fkey)]
                    mesh.delete_face(fkey)
                    mesh.add_face(new_face_vertices, fkey)
            duplicated_vertices[vkey].remove(v)
            mesh.delete_vertex(v)

    # move duplicated superimposed vertices towards neighbours' centroid
    moves = {}
    for vkey in [vkey for vkeys in duplicated_vertices.values() for vkey in vkeys]:
        #if mesh.is_vertex_on_boundary(vkey):
        #    continue
        xyz = scale_vector(sum_vectors([mesh.vertex_coordinates(nbr) for nbr in mesh.vertex_neighbors(vkey)]), 1. / len(mesh.vertex_neighbors(vkey)))
        moves[vkey] = xyz
    for vkey, xyz in moves.items():
        x, y, z = xyz
        attr = mesh.vertex[vkey]
        attr['x'] += factor * (x - attr['x'])
        attr['y'] += factor * (y - attr['y'])
        attr['z'] += factor * (z - attr['z'])

    return new_faces

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

