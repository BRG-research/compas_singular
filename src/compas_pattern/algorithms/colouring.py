import math

import itertools

from compas.datastructures.network import Network

from compas_pattern.datastructures.pseudo_quad_mesh import PseudoQuadMesh

from compas_pattern.topology.polyline_extraction import dual_edge_polylines

from compas.topology import vertex_coloring

from compas_pattern.topology.face_strip_operations import face_strip_collapse

from compas.geometry import centroid_points

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
    'generate_crossing_graph',
    'is_two_colourable',
    'make_two_colourable',
    'apply_transformations',
    'compute_two_colourable_meshes',
]

def generate_crossing_graph(mesh):
    """Generate crossing graph from face strips in the coarse quad mesh.
    """

    # check
    if not mesh.is_quadmesh():
        return None

    # compute face strips as dual edge groups
    edge_groups, max_group = dual_edge_polylines(mesh)

    # collect groups info: group -> [index, list of faces]   
    groups = {}
    index = 0
    for edge, group in edge_groups.items():
        u,v = edge
        if group not in groups:
            groups[group] = [index, []]
            index += 1
        fkey_1 = mesh.halfedge[u][v]
        if fkey_1 is not None and fkey_1 not in groups[group][1]:
            groups[group][1].append(fkey_1)
        fkey_2 = mesh.halfedge[v][u]
        if fkey_2 is not None and fkey_2 not in groups[group][1]:
            groups[group][1].append(fkey_2)

    n = len(groups.keys())

    # map groups as vertices along unit circle
    vertices = [0] * n
    for group, attributes in groups.items():
        index, faces = attributes
        centroids = [mesh.face_centroid(fkey) for fkey in faces]
        xyz = centroid_points(centroids)
        vertices[index] = xyz

    # collect edges
    edges = []
    for fkey in mesh.faces():
        a, b, c, d = mesh.face_vertices(fkey)
        group_0 = edge_groups[(a, b)]
        group_1 = edge_groups[(b, c)]

        idx_0 = groups[group_0][0]
        idx_1 = groups[group_1][0]
        
        edges.append([idx_0, idx_1])


    crossing_graph = Network.from_vertices_and_edges(vertices, edges)
    

    return crossing_graph, edge_groups, groups


def is_two_colourable(graph):
    """Check if a graph is two-colourable.
    """

    adjacency = graph.adjacency

    key_to_colour = vertex_coloring(adjacency)

    colours = []
    for vkey, colour in key_to_colour.items():
        graph.set_vertex_attribute(vkey, 'colour', colour)
        if colour not in colours:
            colours.append(colour)

    colourability = len(colours)

    if colourability > 2:
        return False
    else:
        return True


def make_two_colourable(graph, kmax = 1):
    """Delete vertices in a graph to make it two-colourable.
    """

    combinations_for_two_colourability = []

    # attempt to disconnect k vertices
    k = 0
    while k < kmax:
        k += 1
        vertices = list(graph.vertices())
        
        # combinations of k elements among n elements
        combinations_to_try = list(itertools.combinations(vertices, k))

        for combination in combinations_to_try:

            permutations_to_try = list(itertools.permutations(combination, len(combination)))
            for permutation in permutations_to_try:
                
                valid_operation = True

                # try one combination
                new_graph = graph.copy()

                # delete the vertices in the permutation
                for vkey in permutation:
                    new_graph.delete_vertex(vkey)

                ## check validity: no remaining vertex is disconected
                #for vkey in new_graph.vertices():
                #    if len(new_graph.vertex_neighbours(vkey)) == 0:
                #        valid_operation = False
                #        break
                #if not valid_operation:
                #    continue

                ## test if new graph is two-colourable
                #if is_two_colourable(new_graph):
                #    combinations_for_two_colourability.append([new_graph, permutation])
                #    # don't test other permutations if combination valid
                #    break

                combinations_for_two_colourability.append([new_graph, permutation])

    return combinations_for_two_colourability

def apply_transformations(cls, mesh, edge_groups, groups, combinations):
    """Apply transformations (face strip collapse) on the mesh that correspond to the combinations (vertex deletion) that made the crossing graph two-colourable.
    """

    two_colourable_objects = []

    # apply all combinations

    for graph, combination in combinations:

        # apply one combination
        new_mesh = mesh.copy()

        # apply one collapse
        for group_index in combination:
            collapsed = False

            # find group to collapse
            for group, attributes in groups.items():
                index, faces = attributes
                if index == group_index:

                    # find an edge of the group
                    for fkey_1 in faces:
                        if fkey_1 in new_mesh.faces():
                            for u, v in new_mesh.face_halfedges(fkey_1):
                                fkey_2 = new_mesh.halfedge[v][u]
                                if fkey_2 in faces:

                                    # collapse
                                    face_strip_collapse(cls, new_mesh, u, v)
                                    collapsed = True
                                    break
                        
                        if collapsed:
                            break
                
                if collapsed:
                    continue

        two_colourable_objects.append([graph, new_mesh])

    return two_colourable_objects

def compute_two_colourable_meshes(cls, mesh, kmax = 1):
    """Delete vertices in a graph to make it two-colourable.
    """

    crossing_graph, edge_groups, groups = generate_crossing_graph(mesh)
    if is_two_colourable(crossing_graph):
        return mesh
    two_colourable_combinations = make_two_colourable(crossing_graph, kmax = kmax)
    two_colourable_objects = apply_transformations(cls, mesh, edge_groups, groups, two_colourable_combinations)
    return two_colourable_objects

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
