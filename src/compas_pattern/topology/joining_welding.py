from compas.datastructures.network import Network
from compas_pattern.datastructures.mesh import Mesh

from compas.utilities import geometric_key
from compas.utilities import pairwise

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
    'mesh_unweld_edges',
    'mesh_disconnected_vertices',
    'mesh_disconnected_faces',
    'mesh_explode',
    'network_disconnected_vertices',
    'network_disconnected_edges',
    'network_explode',
]

def mesh_unweld_edges(mesh, edges):
    """Unwelds a mesh along edges.

    Parameters
    ----------
    mesh : Mesh
    edges: list
        List of edges as tuples of vertex keys.

    """

    # set of vertices in edges to unweld
    vertices =  set([i for edge in edges for i in edge])

    # to store changes to do all at once 
    vertex_changes = {}

    for vkey in vertices:

        # maps between old mesh face index and new network vertex index
        old_to_new = {nbr: i for i, nbr in enumerate(mesh.vertex_faces(vkey))}
        new_to_old = {i: nbr for i, nbr in enumerate(mesh.vertex_faces(vkey))}

        # get adjacency network of faces around the vertex excluding adjacency through the edges to unweld
        network_vertices = [mesh.face_centroid(fkey) for fkey in mesh.vertex_faces(vkey)]
        network_edges = ((old_to_new[mesh.halfedge[vkey][nbr]], old_to_new[mesh.halfedge[nbr][vkey]]) for nbr in mesh.vertex_neighbors(vkey) if not mesh.is_edge_on_boundary(vkey, nbr) and (vkey, nbr) not in edges and (nbr, vkey) not in edges)
        network = Network.from_vertices_and_edges(network_vertices, network_edges)

        # collect the disconnected parts around the vertex due to unwelding
        vertex_changes[vkey] = [[new_to_old[key] for key in part] for part in network_disconnected_vertices(network)]
        
    for vkey, changes in vertex_changes.items():
        # for each disconnected part replace the vertex by a new vertex in the faces of the part
        for change in changes:
            mesh.substitute_vertex_in_faces(vkey, mesh.add_vertex(attr_dict = mesh.vertex[vkey]), change)

        # delete old vertices
        mesh.delete_vertex(vkey)

def mesh_disconnected_vertices(mesh):
    """Get the disconnected vertex groups in a mesh.

    Parameters
    ----------
    mesh : Mesh
        A mesh.

    Returns
    -------
    parts : list
        The list of disconnected vertex groups.

    """

    parts = []
    vertices = list(mesh.vertices())

    while len(vertices) > 0:
        # pop one face to start a part
        part = [vertices.pop()]
        next_neighbours = [part[-1]]

        # propagate to neighbours
        while len(next_neighbours) > 0:

            for vkey in mesh.vertex_neighbors(next_neighbours.pop()):
                
                if vkey not in part:
                    part.append(vkey)
                    vertices.remove(vkey)
                    
                    if vkey not in next_neighbours:
                        next_neighbours.append(vkey)
        
        parts.append(part)

    return parts

def mesh_disconnected_faces(mesh):
    """Get the disconnected face groups in a mesh.

    Parameters
    ----------
    mesh : Mesh
        A mesh.

    Returns
    -------
    parts : list
        The list of disconnected face groups.

    """

    parts = mesh_disconnected_vertices(mesh)

    return [set([fkey for vkey in part for fkey in mesh.vertex_faces(vkey)]) for part in parts]

def mesh_explode(mesh, cls=None):
    """Explode a mesh into its disconnected parts.

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

    parts = mesh_disconnected_faces(mesh)

    exploded_meshes = []

    for part in parts:
        
        vertex_keys = list(set([vkey for fkey in part for vkey in mesh.face_vertices(fkey)]))
        vertices = [mesh.vertex_coordinates(vkey) for vkey in vertex_keys]
        
        key_to_index = {vkey: i for i, vkey in enumerate(vertex_keys)}
        faces = [ [key_to_index[vkey] for vkey in mesh.face_vertices(fkey)] for fkey in part]
        
        exploded_meshes.append(cls.from_vertices_and_faces(vertices, faces))

    return exploded_meshes

def network_disconnected_vertices(network):
    """Get the disconnected vertex groups in a network.

    Parameters
    ----------
    network : Network
        A network.

    Returns
    -------
    parts : list
        The list of disconnected vertex groups.

    """

    parts = []
    vertices = list(network.vertices())

    while len(vertices) > 0:
        # pop one vertex to start a part
        part = [vertices.pop()]
        next_neighbours = [part[-1]]

        # propagate to neighbours
        while len(next_neighbours) > 0:

            for vkey in network.vertex_neighbors(next_neighbours.pop()):

                if vkey not in part:
                    part.append(vkey)
                    vertices.remove(vkey)

                    if vkey not in next_neighbours:
                        next_neighbours.append(vkey)
        
        parts.append(part)

    return parts

def network_disconnected_edges(network):
    """Get the disconnected edge groups in a network.

    Parameters
    ----------
    network : Network
        A network.

    Returns
    -------
    parts : list
        The list of disconnected edge groups.

    """


    parts = network_disconnected_vertices(network)

    return [[(u, v) for u in part for v in network.vertex_neighbors(u) if u < v] for part in parts]


def network_explode(network, cls=None):
    """Explode a network into its disconnected parts.

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

    parts = network_disconnected_edges(network)

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

    import compas

