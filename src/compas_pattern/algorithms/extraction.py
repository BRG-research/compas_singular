import operator

from math import acos
from math import asin
from math import pi

from compas.datastructures.mesh import Mesh

from compas.geometry import distance_point_point
from compas.geometry import vector_from_points
from compas.geometry import normalize_vector
from compas.geometry import scale_vector
from compas.geometry import subtract_vectors

from compas.topology import delaunay_from_points

from compas.utilities import geometric_key

from compas_pattern.datastructures.mesh import face_circle

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
    'extraction',
    'patches_to_mesh_very_old',
]

def extraction(boundary_polylines, non_boundary_polylines):
    """Constructs the mesh datastructure based on polylines forming a set of patches.

    Parameters
    ----------
    boundary_polylines : list
        List of boundary polylines as list of vertices.
    non_boundary_polylines : list
        List of non-boundary polylines as list of vertices.

    Returns
    -------
    mesh: Mesh

    Raises
    ------
    -

    """

    polylines = boundary_polylines + non_boundary_polylines

    #collect vertices and face vertices from a set of curves to generate a mesh
    #list of vertex coordinates
    extremities = []
    for polyline in polylines:
        extremities += [polyline[0], polyline[-1]]

    vertex_map = {}
    for point in extremities:
        geom_key = geometric_key(point)
        if geom_key not in vertex_map:
            vertex_map[geom_key] = point
    final_v = list(vertex_map.values())

    edges_to_polyline = {}
    for polyline in polylines:
        start = polyline[0]
        start_idx = final_v.index(start)
        end = polyline[-1]
        end_idx = final_v.index(end)
        edges_to_polyline[(start_idx, end_idx)] = polyline
        edges_to_polyline[(end_idx, start_idx)] = list(reversed(polyline))
    
    #dictionary of edges with curve guid
    edges = {nb_edges: polyline for nb_edges, polyline in enumerate(polylines)}

    #dictionary of geometric key with vertex index
    vertices = {geometric_key(point): index for index, point in enumerate(final_v)}

    #dictionary of halfedges with start and end vertices + dictionary to flip halfedges
    halfedge_info = {} # idx: (polyline, idx opposite he, start vkey, end vkey, vector, angle)
    nb_halfedges = 0
    for index, guid in edges.items():
        start = guid[0]
        end = guid[-1]
        s_xyz = geometric_key(start)
        e_xyz = geometric_key(end)
        s_idx = vertices[s_xyz]
        e_idx = vertices[e_xyz]
        s_vector = subtract_vectors(guid[0], guid[1])
        e_vector = subtract_vectors(guid[-1], guid[-2])
        # angle of start vector
        uv = s_vector
        length = (uv[0] ** 2 + uv[1] ** 2) ** .5
        costheta = uv[0] / length
        sintheta = uv[1] / length
        if asin(sintheta) != 0 :
            s_angle = asin(sintheta) / abs(asin(sintheta)) * acos(costheta)
        else:
            s_angle = acos(costheta)
        # angle of end vector
        uv = e_vector
        length = (uv[0] ** 2 + uv[1] ** 2) ** .5
        costheta = uv[0] / length
        sintheta = uv[1] / length
        if asin(sintheta) != 0 :
            e_angle = asin(sintheta) / abs(asin(sintheta)) * acos(costheta)
        else:
            e_angle = acos(costheta)

        if guid in boundary_polylines:
            is_boundary = True
        else:
            is_boundary = False

        halfedge_info[nb_halfedges] = (guid, nb_halfedges + 1, s_idx, e_idx, s_vector, s_angle, is_boundary)
        halfedge_info[nb_halfedges + 1] = (guid, nb_halfedges, e_idx, s_idx, e_vector, e_angle, is_boundary)
        nb_halfedges += 2

    #sort halfedges around start vertex
    sorted_he = {vertex: [] for xyz, vertex in vertices.items()}
    #match keys to an unsorted list of half edges starting from this vertex
    for key, items in halfedge_info.items():
        u = items[2]
        sorted_he[u].append(key)
    for vert, list_he in sorted_he.items():
        x = {key: halfedge_info[key][5] for key in list_he}
        sorted_x = sorted(x.items(), key=operator.itemgetter(1))
        sorted_he[vert] = sorted_x

    #count visits for each halfedge
    visited = {key: False for key, items in halfedge_info.items()}
    
    nb_faces = 0
    
    #get face vertices
    final_fv = []
    for key, items in halfedge_info.items():
        #if already visited, go to next halfedge
        if visited[key]:
            continue
        else:
            #initiate with first edge
            face_he = []
            init_he = key
            face_he.append(init_he)
            visited[init_he] = True
            u0 = halfedge_info[face_he[-1]][2]
            stop = False
            max_he = len(halfedge_info)
            #if not stop ie last vertex is not equal to the first one
            while not stop and max_he > 0:
                max_he -= 1
                v = halfedge_info[face_he[-1]][3]
                if v == u0:
                    stop = True
                else:
                    #get halfedges around last vertex, flip last edge and get the next halfedge around this vertex
                    new_he_list = [y[0] for y in sorted_he[v]]
                    idx = new_he_list.index(halfedge_info[face_he[-1]][1])
                    new_he = new_he_list[idx - 1]
                    #add halfedge to face list and note as visited
                    face_he.append(new_he)
                    visited[new_he] = True
            #get face vertices from face halfedges
            face_vertices = [halfedge_info[he][2] for he in face_he]
            boundary = True
            for i in face_he:
                if not halfedge_info[i][6]:
                    boundary = False
                    break
            if not boundary:
                final_fv.append(face_vertices)

    return final_v, final_fv, edges_to_polyline

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
