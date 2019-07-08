from compas_pattern.datastructures.mesh.operations import mesh_substitute_vertex_in_faces

from compas.topology import adjacency_from_edges
from compas.topology import connected_components


__all__ = [
    'mesh_unweld_edges'
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
        network_edges = [(old_to_new[mesh.halfedge[vkey][nbr]], old_to_new[mesh.halfedge[nbr][vkey]]) for nbr in mesh.vertex_neighbors(vkey) if not mesh.is_edge_on_boundary(vkey, nbr) and (vkey, nbr) not in edges and (nbr, vkey) not in edges]
        
        adjacency = adjacency_from_edges(network_edges)
        for key, values in adjacency.items():
            adjacency[key] = {value: None for value in values}
        # include non connected vertices
        edge_vertices = list(set([i for edge in network_edges for i in edge]))
        for i in range(len(mesh.vertex_faces(vkey))):
            if i not in edge_vertices:
                adjacency[i] = {}
        
        # collect the disconnected parts around the vertex due to unwelding
        vertex_changes[vkey] = [[new_to_old[key] for key in part] for part in connected_components(adjacency)]
        
    for vkey, changes in vertex_changes.items():
        # for each disconnected part replace the vertex by a new vertex in the faces of the part
        for change in changes:
            mesh_substitute_vertex_in_faces(mesh, vkey, mesh.add_vertex(attr_dict = mesh.vertex[vkey]), change)

        # delete old vertices
        mesh.delete_vertex(vkey)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas

