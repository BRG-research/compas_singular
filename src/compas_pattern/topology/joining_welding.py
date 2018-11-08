from compas_pattern.datastructures.mesh import Mesh

from compas.datastructures.mesh.operations.weld import mesh_unweld_vertices

from compas.utilities import geometric_key
from compas.utilities import pairwise

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
    'unweld_polyedge',
    'unweld_mesh_along_edge_path',
    'mesh_disjointed_parts',
    'mesh_explode',
    'network_disjointed_parts',
    'network_explode',
]

def unweld_polyedge(mesh, polyedge):
    """Unwelds a mesh along a polyedge.

    Parameters
    ----------
    mesh : Mesh
    polyedge: list
        List of vertex keys.

    Returns
    -------
    mesh : Mesh
        The unwelded mesh.

    """

    # get sorted faces along the polyedge
    faces_left = [mesh.halfedge[u][v] for u, v in pairwise(polyedge)]
    faces_right = list(reversed([mesh.halfedge[v][u] for u, v in pairwise(polyedge)]))

    faces_start = mesh.vertex_faces(polyedge[0], ordered = True, include_none = True)
    idx = faces_start.index(faces_right[-1])
    faces_start = faces_start[idx :] + faces_start[: idx]
    faces_start = faces_start[1 : -1]

    faces_end = mesh.vertex_faces(polyedge[-1], ordered = True, include_none = True)
    idx = faces_end.index(faces_left[-1])
    faces_end = faces_end[idx :] + faces_end[: idx]
    faces_end = faces_end[1 : -1]

    faces = faces_start + faces_left + faces_end + faces_right

    # unweld polyedge vertices in each face
    for fkey in faces:
        mesh_unweld_vertices(mesh, fkey, polyedge)

    olds = []
    # weld back adjacent faces along polyedge
    for fkey_1, fkey_2 in pairwise(faces + faces[: 1]):
        if fkey_1 is not None and fkey_2 is not None:
            vkey_pivot = mesh.face_adjacency_vertices(fkey_1, fkey_2)[0]
            vkey_new = mesh.face_vertex_ancestor(fkey_1, vkey_pivot)
            vkey_old = mesh.face_vertex_descendant(fkey_2, vkey_pivot)
            olds.append(vkey_old)
            face_vertices = [vkey_new if vkey == vkey_old else vkey for vkey in mesh.face_vertices(fkey_2)]
            mesh.delete_face(fkey_2)
            mesh.add_face(face_vertices, fkey_2)

    mesh.cull_vertices()
    print 'polyedge', polyedge
    print 'olds', olds
    # delete original polyedge vertices
    for vkey in mesh.vertices():
        print mesh.vertex_neighbors(vkey), mesh.vertex_faces(vkey)
    
    return mesh

def unweld_mesh_along_edge_path(mesh, edge_path):
    """Unwelds a mesh along an edge path.

    Parameters
    ----------
    mesh : Mesh
    edge_path: list
        Edge path for unwelding.

    Returns
    -------
    mesh : Mesh
        The unwelded mesh.

    """
    
    duplicates = {}

    # convert edge path in vertex path
    vertex_path = [edge[0] for edge in edge_path]
    # add last vertex of edge path only if not closed loop
    if edge_path[0][0] != edge_path[-1][-1]:
        vertex_path.append(edge_path[-1][-1])

    # store changes to make in the faces along the vertex path in the following format {face to change = [old vertex, new vertex]}
    to_change = {}

    # iterate along path
    for i, vkey in enumerate(vertex_path):
        # vertices before and after current
        last_vkey = vertex_path[i - 1]
        next_vkey = vertex_path[i + 1 - len(vertex_path)]

        # skip the extremities of the vertex path, except if the path is a loop or if vertex is on boundary
        if (edge_path[0][0] == edge_path[-1][-1]) or (i != 0 and i != len(vertex_path) - 1) or mesh.is_vertex_on_boundary(vkey):
            # duplicate vertex and its attributes
            attr = mesh.vertex[vkey]
            new_vkey = mesh.add_vertex(attr_dict = attr)
            duplicates[vkey] = new_vkey
            # split neighbours in two groups depending on the side of the path
            vertex_nbrs = mesh.vertex_neighbors(vkey, True)
            
            # two exceptions on last_vkey or next_vkey if the vertex is on the boundary or a non-manifold vertex in case of the last vertex of a closed edge path
            if edge_path[0][0] == edge_path[-1][-1] and i == len(vertex_path) - 1:
                next_vkey = vertex_path[0]
            if mesh.is_vertex_on_boundary(vkey):
                for j in range(len(vertex_nbrs)):
                    if mesh.is_vertex_on_boundary(vertex_nbrs[j - 1]) and mesh.is_vertex_on_boundary(vertex_nbrs[j]):
                        before, after = vertex_nbrs[j - 1], vertex_nbrs[j]
                if i == 0:
                    last_vkey = before
                elif i == len(vertex_path) - 1:
                    next_vkey = after

            idxa = vertex_nbrs.index(last_vkey)
            idxb = vertex_nbrs.index(next_vkey)
            if idxa < idxb:
                half_nbrs = vertex_nbrs[idxa : idxb]
            else:
                half_nbrs = vertex_nbrs[idxa :] + vertex_nbrs[: idxb]
            
            # get faces corresponding to vertex neighbours
            faces = [mesh.halfedge[nbr][vkey] for nbr in half_nbrs]
            # store change per face with index of duplicate vertex
            for fkey in faces:
                if fkey in to_change:
                    # add to other changes
                    to_change[fkey] += [[vkey, new_vkey]]
                else: 
                    to_change[fkey] = [[vkey, new_vkey]]

    # apply stored changes
    for fkey, changes in to_change.items():
        if fkey is None:
            continue
        face_vertices = mesh.face_vertices(fkey)[:]
        for change in changes:
            old_vertex, new_vertex = change
            # replace in list of face vertices
            idx = face_vertices.index(old_vertex)
            face_vertices[idx] = new_vertex
        # modify face by removing it and adding the new one
        attr = mesh.facedata[fkey]
        mesh.delete_face(fkey)
        mesh.add_face(face_vertices, fkey, attr_dict = attr)

    return duplicates


def mesh_disjointed_parts(mesh):
    """Get the disjointed parts in a mesh as lists of faces.

    Parameters
    ----------
    mesh : Mesh
        A mesh.

    Returns
    -------
    parts : list
        The list of disjointed parts as lists of face keys.

    """

    parts = []
    faces = list(mesh.faces())

    while len(faces) > 0:
        # pop one face to start a part
        part = [faces.pop()]
        next_neighbours = [part[-1]]

        # propagate to neighbours
        while len(next_neighbours) > 0:

            for fkey in mesh.face_neighbors(next_neighbours.pop()):
                
                if fkey not in part:
                    part.append(fkey)
                    faces.remove(fkey)
                    
                    if fkey not in next_neighbours:
                        next_neighbours.append(fkey)
        
        parts.append(part)

    return parts

def mesh_explode(mesh, cls=None):
    """Explode a mesh into its disjointed parts.

    Parameters
    ----------
    mesh : Mesh
        A mesh.

    Returns
    -------
    exploded_meshes : list
        The list of the meshes from the exploded mesh parts.

    """

    if cls is None:
        cls = type(mesh)

    parts = mesh_disjointed_parts(mesh)

    exploded_meshes = []

    for part in parts:
        
        vertex_keys = list(set([vkey for fkey in part for vkey in mesh.face_vertices(fkey)]))
        vertices = [mesh.vertex_coordinates(vkey) for vkey in vertex_keys]
        
        key_to_index = {vkey: i for i, vkey in enumerate(vertex_keys)}
        faces = [ [key_to_index[vkey] for vkey in mesh.face_vertices(fkey)] for fkey in part]
        
        exploded_meshes.append(cls.from_vertices_and_faces(vertices, faces))

    return exploded_meshes


def network_disjointed_parts(network):
    """Get the disjointed parts in a network as lists of edges.

    Parameters
    ----------
    network : Network
        A network.

    Returns
    -------
    parts : list
        The list of disjointed parts as lists of edges.

    """

    parts = []
    edges = list(network.edges())

    while len(edges) > 0:
        # pop one vertex to start a part
        part = [edges.pop()]
        next_neighbours = [part[-1]]

        # propagate to neighbours
        while len(next_neighbours) > 0:

            for u, v in network.edge_connected_edges(*next_neighbours.pop()):

                if (u, v) not in part and (v, u) not in part:
                    part.append((u, v))
                    edges.remove((u, v))

                    if (u, v) not in next_neighbours:
                        next_neighbours.append((u, v))
        
        parts.append(part)

    return parts

def network_explode(network, cls=None):
    """Explode a network into its disjointed parts.

    Parameters
    ----------
    network : Network
        A network.

    Returns
    -------
    exploded_networks : list
        The list of the networks from the exploded network parts.

    """

    if cls is None:
        cls = type(network)

    parts = network_disjointed_parts(network)

    exploded_networks = []

    for part in parts:
        
        vertex_keys = list(set([vkey for edge in part for vkey in edge]))
        vertices = [network.vertex_coordinates(vkey) for vkey in vertex_keys]
        
        key_to_index = {vkey: i for i, vkey in enumerate(vertex_keys)}
        edges = [ (key_to_index[u], key_to_index[v]) for u, v in part]
        
        exploded_networks.append(cls.from_vertices_and_edges(vertices, edges))

    return exploded_networks

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    pass
