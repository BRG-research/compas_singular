import math

from compas.datastructures.network import Network

from compas_pattern.datastructures.pseudo_quad_mesh import PseudoQuadMesh

from compas_pattern.topology.polyline_extraction import dual_edge_groups

from compas.topology import vertex_coloring

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
    'generate_crossing_graph_from_patch_decomposition',
    'is_graph_two_colourable',
    'make_crossing_graph_two_colourable',
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
    

    return crossing_graph


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


def make_crossing_graph_two_colourable():
    """Densifies a quad mesh based on a target length.
    
    Parameters
    ----------
    mesh : Mesh
        The quad mesh to densify.
    target_length : float
        Target length for densification.

    Returns
    -------
    dense_mesh: Mesh, None
        Densified quad mesh.
        None if not a quad mesh.

    Raises
    ------
    -

    """

    return 0

def make_patch_decomposition_two_colourable():
    """Densifies a quad mesh based on a target length.
    
    Parameters
    ----------
    mesh : Mesh
        The quad mesh to densify.
    target_length : float
        Target length for densification.

    Returns
    -------
    dense_mesh: Mesh, None
        Densified quad mesh.
        None if not a quad mesh.

    Raises
    ------
    -

    """

    return 0

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas