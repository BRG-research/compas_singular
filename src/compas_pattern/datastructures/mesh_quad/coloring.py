from compas_pattern.datastructures.network.network import Network
from compas_pattern.datastructures.network.coloring import is_network_two_colorable
from compas.topology import vertex_coloring

from compas.geometry import centroid_points

__author__ = ['Robin Oval']
__copyright__ = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__ = 'MIT License'
__email__ = 'oval@arch.ethz.ch'

__all__ = [
    'quad_mesh_strip_2_coloring',
    'quad_mesh_strip_n_coloring',
    'quad_mesh_polyedge_2_coloring'
]


def quad_mesh_strip_2_coloring(quad_mesh):
    """Try to color the strips of a quad mesh with two colors only without overlapping strips with the same color.

    Parameters
    ----------
    quad_mesh : QuadMesh
            A quad mesh.

    Returns
    -------
    dict, None
            A dictionary with strip keys pointing to colors, if two-colorable.
            None if not two-colorable.

    """

    quad_mesh.collect_strips()
    return is_network_two_colorable(quad_mesh.strip_connectivity())


def quad_mesh_strip_n_coloring(quad_mesh):
    """Color the strips of a quad mesh with a minimum number of colors without overlapping strips with the same color.

    Parameters
    ----------
    quad_mesh : QuadMesh
            A quad mesh.

    Returns
    -------
    dict
            A dictionary with strip keys pointing to colors.

    """

    quad_mesh.collect_strips()
    return vertex_coloring(quad_mesh.strip_connectivity().adjacency)


def quad_mesh_polyedge_graph(quad_mesh):
    polyedges = quad_mesh.polyedges()
    polyedges = [tuple(polyedge) for polyedge in polyedges]

    vertices = {i: centroid_points([quad_mesh.vertex_coordinates(vkey) for vkey in polyedge]) for i, polyedge in enumerate(polyedges)}
    edges = []
    for i, polyedge in enumerate(polyedges):
        for vkey in polyedge:
            if not quad_mesh.is_vertex_singular(vkey):
                for j, polyedge_2 in enumerate(polyedges):
                    if vkey in polyedge_2:
                        edges.append((i, j))
                        break
    return Network.from_vertices_and_edges(vertices, edges)


def quad_mesh_polyedge_2_coloring(quad_mesh):
    network = quad_mesh_polyedge_graph(quad_mesh)
    return is_network_two_colorable(network)


def quad_mesh_polyedge_n_coloring(quad_mesh):
    network = quad_mesh_polyedge_graph(quad_mesh)
    return vertex_coloring(network)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
