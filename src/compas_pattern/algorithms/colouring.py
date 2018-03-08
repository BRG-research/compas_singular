import math

from compas.datastructures.network import Network

from compas_pattern.datastructures.pseudo_quad_mesh import PseudoQuadMesh

from compas_pattern.topology.polyline_extraction import dual_edge_groups

from compas.topology import vertex_coloring

from compas_pattern.topology.face_strip_operations import face_strip_collapse

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
    'generate_crossing_graph_from_patch_decomposition',
    'is_graph_two_colourable',
    'make_crossing_graph_two_colourable',
    'make_patch_decomposition_two_colourable',
]

def generate_crossing_graph_from_patch_decomposition(patches):
    """Generate crossing graph from eddge groups in the patch decomposition.
    
    Parameters
    ----------
    patches: a quad mesh
        A quad patch decomposition.

    Returns
    -------
    crossing_graph: Network, None
        Crossing graph.
        None if not a quad patch decomposition.

    Raises
    ------
    -

    """

    # check
    if not patches.is_quadmesh():
        return None

    # compute edge groups
    edge_groups, max_group = dual_edge_groups(patches)

    # collect groups
    groups = []
    for edge, group in edge_groups.items():
        if group not in groups:
            groups.append(group)

    n = len(groups)

    # map vertices along unit circle
    vertices = [[math.cos(k * 2 * math.pi / n), math.sin(k * 2 * math.pi / n), 0] for k in range(n)]
    edges = []

    # collect edges
    for fkey in patches.faces():
        a, b, c, d = patches.face_vertices(fkey)
        group_0 = edge_groups[(a, b)]
        group_1 = edge_groups[(b, c)]
        # convert edge group into vertex index
        idx_0 = groups.index(group_0)
        idx_1 = groups.index(group_1)
        edges.append([idx_0, idx_1])


    crossing_graph = Network.from_vertices_and_edges(vertices, edges)
    

    return crossing_graph, edge_groups, groups


def is_graph_two_colourable(graph):

    adjacency = graph.adjacency

    key_to_colour = vertex_coloring(adjacency)

    colours = []
    for key, colour in key_to_colour.items():
        if colour not in colours:
            colours.append(colour)

    colourability = len(colours)

    if colourability > 2:
        return False
    else:
        return True


def make_crossing_graph_two_colourable(graph, kmax = 1):
    import itertools

    two_col_combinations = []

    k = 0
    while k < kmax:
        k += 1
        vertices = list(graph.vertices())
        combinations_to_disconnect = list(itertools.combinations(vertices, k))
        #print combinations_to_disconnect
        for vertices_to_disconnect in combinations_to_disconnect:
            new_graph = graph.copy()
            for vkey in vertices_to_disconnect:
                new_graph.delete_vertex(vkey)
            if is_graph_two_colourable(new_graph):
                #print vertices_to_disconnect
                two_col_combinations.append(vertices_to_disconnect)
        if len(two_col_combinations) != 0:
            break

    return two_col_combinations

def make_patch_decomposition_two_colourable(cls, patches, edge_groups, groups, combinations):

    two_col_patches_solutions = []

    for combination in combinations:
        new_patches = patches.copy()
        for group_index in combination:
            group = groups[group_index]
            for edge, edge_group in edge_groups.items():
                if edge_group == group:
                    u, v = edge
                    face_strip_collapse(cls, new_patches, u, v)
                    break
        two_col_patches_solutions.append(new_patches)

    return two_col_patches_solutions

def compute_two_colourable_patches(cls, patches, kmax = 1):
    crossing_graph, edge_groups, groups = generate_crossing_graph_from_patch_decomposition(patches)
    if is_graph_two_colourable(crossing_graph):
        return patches
    two_col_combinations = make_crossing_graph_two_colourable(crossing_graph, kmax = kmax)
    two_col_patches_solutions = make_patch_decomposition_two_colourable(cls, patches, edge_groups, groups, two_col_combinations)
    return two_col_patches_solutions

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas