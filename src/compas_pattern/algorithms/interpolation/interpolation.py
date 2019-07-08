import networkx as nx
import itertools as it

from compas_pattern.datastructures.mesh_quad.grammar_pattern import delete_strips

__all__ = [
]


def distance_between_two_meshes(mesh_1, mesh_2):

    mesh_1.collect_strips()
    g1 = quad_mesh_strip_graph(mesh_1)
    mesh_2.collect_strips()
    g2 = quad_mesh_strip_graph(mesh_2)
    distance, nodes_1, nodes_2 = find_largest_isomorphic_subgraph(g1, g2)
    return distance


def simple_interpolate_two_meshes(mesh_1, mesh_2):

    mesh_1.collect_strips()
    g1 = quad_mesh_strip_graph(mesh_1)
    mesh_2.collect_strips()
    g2 = quad_mesh_strip_graph(mesh_2)
    dist, strips_1, strips_2 = find_largest_isomorphic_subgraph(g1, g2)

    simple_interpolation = {(k, dist - k): [] for k in range(dist + 1)}
    
    for k in range(len(strips_1) + 1):
        for del_strips in it.combinations(strips_1, k):
            mesh_copy = mesh_1.copy()
            delete_strips(mesh_copy, del_strips, preserve_boundaries=True)
            simple_interpolation[(k, dist - k)].append(mesh_copy)
    
    for k in range(len(strips_2) + 1):
        for del_strips in it.combinations(strips_2, k):
            mesh_copy = mesh_2.copy()
            delete_strips(mesh_copy, del_strips, preserve_boundaries=True)
            simple_interpolation[(dist - k, k)].append(mesh_copy)

    return simple_interpolation


def quad_mesh_strip_graph(mesh):

    # add node attribute closed
    return nx.MultiGraph([tuple(mesh.face_strips(fkey)) for fkey in mesh.faces()])


def quad_mesh_graph(mesh):

    return nx.Graph(mesh.edges()), {vkey: 'boundary' if mesh.is_vertex_on_boundary(vkey) else 'not boundary' for vkey in mesh.vertices()}


def find_largest_isomorphic_subgraph(g1, g2):

    n1 = g1.number_of_nodes()
    n2 = g2.number_of_nodes()
    
    for k in range(0, max(n1, n2) + 1):
        for nodes_1 in it.combinations(g1.nodes(), max(k, k + n1 - n2)):
            g1c = g1.copy()
            g1c.remove_nodes_from(nodes_1)
            for nodes_2 in it.combinations(g2.nodes(), max(k, k + n2 - n1)):
                g2c = g2.copy()
                g2c.remove_nodes_from(nodes_2)
                # add node_match for closed strips
                if nx.is_isomorphic(g1c, g2c):
                    distance = max(k, k + n1 - n2) + max(k, k + n2 - n1)
                    return distance, nodes_1, nodes_2


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    from compas_pattern.datastructures.mesh_quad.mesh_quad import QuadMesh
    import networkx as nx

    mesh_1 = QuadMesh.from_json('/Users/Robin/Desktop/json/3.json')
    mesh_2 = QuadMesh.from_json('/Users/Robin/Desktop/json/5.json')

    for key, value in simple_interpolate_two_meshes(mesh_1, mesh_2).items():
        print (key, value)
    #print(mesh.number_of_vertices())
    # edges_1 = [(0, 1), (1, 2), (2, 3), (3, 1)]
    # edges_2 = [(0, 1), (1, 2), (2, 0)]
    # edges_3 = [(0, 1), (1, 3), (3, 2), (1, 2)]
    # g1 = nx.Graph(edges_1)
    # g2 = nx.Graph(edges_2)
    # g3 = nx.Graph(edges_3)
    # print(find_largest_isomorphic_subgraph(g1, g2))
    # print(find_largest_isomorphic_subgraph(g1, g3))

    #g = nx.MultiGraph([(0,0),(0,1),(0,1)])
    #print(g.edges())
