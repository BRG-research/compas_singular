from compas.datastructures.mesh import Mesh

from compas_pattern.topology.polyline_extraction import dual_edge_polylines
from compas_pattern.topology.polyline_extraction import quad_mesh_polylines
from compas_pattern.topology.polyline_extraction import mesh_boundaries

from compas_pattern.topology.joining_welding import weld_mesh

from compas_pattern.topology.joining_welding import unweld_mesh_along_edge_path

from compas_pattern.topology.grammar import simple_split
from compas_pattern.topology.global_propagation import mesh_propagation

from compas.geometry import scale_vector
from compas.geometry import sum_vectors

from compas_pattern.datastructures.mesh import delete_face

from compas.geometry import offset_polyline

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
    'face_strip_collapse',
    'multiple_strip_collapse',
    'face_strip_subdivide',
    'face_strips_merge',
    'face_strip_insert',
]


def face_strip_collapse(cls, mesh, u0, v0):
    """Collapse a face strip in a quad mesh.

    Parameters
    ----------
    mesh : Mesh
        A quad mesh.
    u0: int
        Key of edge start vertex.
    v0: int
        Key of edge end vertex.

    Returns
    -------
    mesh : mesh, None
        The modified quad mesh.
        None if mesh is not a quad mesh or if (u0,v0) is not an edge.

    """

    # checks
    if not mesh.is_quadmesh():
        return None
    if v0 not in mesh.halfedge[u0] and u0 not in mesh.halfedge[v0]:
        return None

    # get edges in the face strip
    edge_groups, max_group = dual_edge_polylines(mesh)
    group_number = edge_groups[(u0, v0)]
    edges_to_collapse = [edge for edge, group in edge_groups.items() if group == group_number]
    
    # delete faces in the face strip
    for u, v in edges_to_collapse:
        if v in mesh.halfedge[u]:
            fkey = mesh.halfedge[u][v]
            if fkey is not None:
                delete_face(mesh, fkey)

    edges_to_collapse = []
    for edge, group in edge_groups.items():
        u, v = edge
        if group == group_number and [v, u] not in edges_to_collapse:
            edges_to_collapse.append([u, v])

    to_cull = []
    # merge vertices of collapsed edges
    boundary_vertices = mesh.vertices_on_boundary()
    vertex_conversion = {}
    for u, v in edges_to_collapse:
        # if only one edge vertex on boundary, set as new location
        if u in boundary_vertices and v not in boundary_vertices:
            x, y, z = mesh.vertex_coordinates(v)
        elif v in boundary_vertices and u not in boundary_vertices:
            x, y, z = mesh.vertex_coordinates(u)
        # or to edge midpoint otherwise
        else:
            x, y, z = mesh.edge_midpoint(u, v)
        w = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})
        # update adjacent face vertices
        for vkey in [u, v]:
            attr = mesh.vertex[vkey]
            attr['x'] = x
            attr['y'] = y
            attr['z'] = z
            for fkey in mesh.vertex_faces(vkey):
                face_vertices = mesh.face_vertices(fkey)[:]
                idx = face_vertices.index(vkey)
                face_vertices[idx] = w
                delete_face(mesh, fkey)
                mesh.add_face(face_vertices, fkey)
        # store data for vertex change
        vertex_conversion[u] = w
        vertex_conversion[v] = w

    for vkey in mesh.vertices():
        if vkey not in vertex_conversion:
            vertex_conversion[vkey] = vkey
    # new_edge_groups
    new_edge_groups = {}
    for edge, group in edge_groups.items():
        u0, v0 = edge
        new_edge_groups[(vertex_conversion[u0], vertex_conversion[v0])] = group
        
    ## clean mesh
    #vertices, face_vertices = weld_mesh(mesh)
    #mesh = cls.from_vertices_and_faces(vertices, face_vertices)
    
    #mesh.cull_vertices()@
    #vertices = list(mesh.vertices())
    # print len(list(mesh.vertices()))
    #for vkey in vertices:
    #    if len(mesh.vertex_neighbours(vkey)) == 0:
    #        print -1
    #        del mesh.vertex[vkey]

    #print mesh 
    # print list(mesh.vertices())
    return new_edge_groups

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

    edge_groups, max_group = dual_edge_polylines(mesh)
    boundaries = mesh_boundaries(mesh)

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

def face_strip_subdivide(cls, mesh, u, v):
    """Subdivide a face strip in a quad mesh.

    Parameters
    ----------
    mesh : Mesh
        A quad mesh.
    u: int
        Key of edge start vertex.
    v: int
        Key of edge end vertex.

    Returns
    -------
    mesh : mesh, None
        The modified quad mesh.
        None if mesh is not a quad mesh or if (u,v) is not an edge.

    """

    # checks
    if not mesh.is_quadmesh():
        for fkey in mesh.faces():
            face_vertices = mesh.face_vertices(fkey)
        return None
    if (v not in mesh.halfedge[u] or mesh.halfedge[u][v] is None) and (u not in mesh.halfedge[v] or mesh.halfedge[v][u] is None):
        return None

    if v in mesh.halfedge[u] and mesh.halfedge[u][v] is not None:
        fkey = mesh.halfedge[u][v]
    else:
        fkey = mesh.halfedge[v][u]

    regular_vertices = list(mesh.vertices())
    simple_split(mesh, fkey, (u, v))
    mesh_propagation(mesh, regular_vertices)

    return 0

def face_strips_merge(cls, mesh, u, v):
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
    polylines = quad_mesh_polylines(mesh)
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

def face_strip_insert_2(cls, mesh, vertex_path, factor = .33):

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

def face_strip_insert(cls, mesh, vertex_path, pole_extremities, factor = .33):

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
    for vkey in [vkey for vkeys in duplicated_vertices.values() for vkey in vkeys]:
        #if mesh.is_vertex_on_boundary(vkey):
        #    continue
        if len(mesh.vertex_neighbors(vkey)) == 0:
            continue
        centroids = [mesh.face_centroid(fkey) for fkey in mesh.vertex_faces(vkey)]
        areas = [mesh.face_area(fkey) for fkey in mesh.vertex_faces(vkey)]
        x, y, z = sum_vectors([scale_vector(centroid, area / sum(areas)) for centroid, area in zip(centroids, areas)])
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
