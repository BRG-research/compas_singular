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
    'patches_to_mesh',
    'patches_to_mesh_old',
]

def patches_to_mesh(polylines):
    """Constructs the mesh datastructure based on polylines forming a set of patches using mesh_from_lines.

    Parameters
    ----------
    polylines : list
        List of polylines as list of vertices.

    Returns
    -------
    mesh: Mesh

    Raises
    ------
    -

    """

    # # convert polylines in lines to use Mesh.from_lines
    # lines = []
    # for polyline in polylines:
    #     lines.append([polyline[i], polyline[i + 1]] for i in range(len(polyline) - 1))
    # mesh = Mesh.from_lines(lines)

    # # convert polygonal faces into minimal valency faces
    # for fkey in mesh.faces():
    #     # missing exception for polyline extremities
    #     reduced_face_vertices = [vkey for vkey in mesh.face_vertices(fkey) if len(mesh.vertex_neighbours(vkey)) != 2]
    #     attr = mesh.facedata[fkey]
    #     mesh.delete_face(fkey)
    #     mesh.add_face(reduced_face_vertices, fkey, attr_dict = attr)

    # return mesh

    return None

def patches_to_mesh_old(boundary_polylines, non_boundary_polylines):
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
    
    #dictionary of edges with curve guid
    edges = {nb_edges: polyline for nb_edges, polyline in enumerate(polylines)}
    
    #dictionary of geometric key with vertex index
    vertices = {geometric_key(point): index for index, point in enumerate(final_v)}
    
    #dictionary of halfedges with start and end vertices + dictionary to flip halfedges
    nb_halfedges = 0
    halfedges = {}
    flip_he = {}
    he_vectors = {}
    #{('u', 'v'): guid}
    edge_guid = {}
    for index, guid in edges.items():
        start = guid[0]
        end = guid[-1]
        s_xyz = geometric_key(start)
        e_xyz = geometric_key(end)
        s_idx = vertices[s_xyz]
        e_idx = vertices[e_xyz]
        halfedges[nb_halfedges] = [s_idx, e_idx]
        halfedges[nb_halfedges + 1] = [e_idx, s_idx]
        flip_he[nb_halfedges] = nb_halfedges + 1
        flip_he[nb_halfedges + 1] = nb_halfedges
        edge_guid[(s_idx, e_idx)] = guid
        edge_guid[(e_idx, s_idx)] = guid
        nb_halfedges += 2
        he_vectors[(s_idx, e_idx)] = subtract_vectors(guid[0], guid[1])
        he_vectors[(e_idx, s_idx)] = subtract_vectors(guid[-1], guid[-2])
        
    #angle between each halfedge and (1,0,0)
    he_angles = {}
    for he, uv in halfedges.items():
        u, v = uv
        u_xyz = final_v[u]
        v_xyz = final_v[v]
        length = distance_point_point(u_xyz, v_xyz)
        uv = vector_from_points(u_xyz, v_xyz)
        uv = he_vectors[(u, v)] # NEW
        length = (uv[0] ** 2 + uv[1] ** 2) ** .5
        costheta = uv[0] / length
        sintheta = uv[1] / length
        if asin(sintheta) != 0 :
            theta = asin(sintheta) / abs(asin(sintheta)) * acos(costheta)
        else:
            theta = acos(costheta)
        he_angles[he] = theta
    
    #sort halfedges around start vertex
    sorted_he = {vertex: [] for xyz, vertex in vertices.items()}
    #match keys to an unsorted list of half edges starting from this vertex
    for he in halfedges:
        u = halfedges[he][0]
        sorted_he[u].append(he)
    for vert, list_he in sorted_he.items():
        x = {he: he_angles[he] for he in list_he}
        sorted_x = sorted(x.items(), key=operator.itemgetter(1))
        sorted_he[vert] = sorted_x
    
    #count visits for each halfedge
    visited = {he: False for he in halfedges}
    
    nb_faces = 0
    
    #get face vertices
    final_fv = []
    for he in halfedges:
        #if already visited, go to next halfedge
        if visited[he]:
            continue
        else:
            #initiate with first edge
            face_he = []
            init_he = he
            face_he.append(init_he)
            visited[init_he] = True
            u0 = halfedges[face_he[-1]][0]
            stop = False
            max_he = len(halfedges)
            #if not stop ie last vertex is not equal to the first one
            while not stop and max_he > 0:
                max_he -= 1
                v = halfedges[face_he[-1]][1]
                if v == u0:
                    stop = True
                else:
                    #get halfedges around last vertex, flip last edge and get the next halfedge around this vertex
                    new_he_list = [y[0] for y in sorted_he[v]]
                    idx = new_he_list.index(flip_he[face_he[-1]])
                    new_he = new_he_list[idx - 1]
                    #add halfedge to face list and note as visited
                    face_he.append(new_he)
                    visited[new_he] = True
            #get face vertices from face halfedges
            face_vertices = [halfedges[he][0] for he in face_he]
            boundary = True
            for i in range(len(face_vertices)):
                u = face_vertices[i - 1]
                v = face_vertices[i]
                guid = edge_guid[(u, v)]
                if guid in non_boundary_polylines:
                    boundary = False
                    break
            if not boundary:
                final_fv.append(face_vertices)
    
    mesh = Mesh.from_vertices_and_faces(final_v, final_fv)

    return mesh

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
