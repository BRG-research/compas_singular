from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from compas.topology import adjacency_from_edges
from compas.topology import vertex_coloring

from compas_singular.topology import is_adjacency_two_colorable


__all__ = [
    'quad_mesh_strip_2_coloring',
    'quad_mesh_strip_n_coloring',
    'quad_mesh_polyedge_2_coloring',
    'quad_mesh_polyedge_n_coloring'
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

    vertices, edges = quad_mesh.strip_graph()
    return is_adjacency_two_colorable(adjacency_from_edges(edges))


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

    vertices, edges = quad_mesh.strip_graph()
    return vertex_coloring(adjacency_from_edges(edges))


def quad_mesh_polyedge_2_coloring(quad_mesh):
    """Try to color the polyedges of a quad mesh with two colors only without overlapping polyedges with the same color.
    Polyedges connected by their extremities, which are singularities, do not count as overlapping.

    Parameters
    ----------
    quad_mesh : QuadMesh
        A quad mesh.

    Returns
    -------
    dict, None
        A dictionary with polyedge keys pointing to colors, if two-colorable.
        None if not two-colorable.
    """

    vertices, edges = quad_mesh.polyedge_graph()
    return is_adjacency_two_colorable(adjacency_from_edges(edges))


def quad_mesh_polyedge_n_coloring(quad_mesh):
    """Color the polyedges of a quad mesh with a minimum number of colors without overlapping polyedges with the same color.
    Polyedges connected by their extremities, which are singularities, do not count as overlapping.

    Parameters
    ----------
    quad_mesh : QuadMesh
        A quad mesh.

    Returns
    -------
    dict
        A dictionary with polyedge keys pointing to colors.
    """

    vertices, edges = quad_mesh.polyedge_graph()
    return vertex_coloring(adjacency_from_edges(edges))


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass

    # import time
    # import compas
    # from compas_singular.datastructures.mesh_quad.mesh_quad import QuadMesh

    # mesh = QuadMesh.from_json('/Users/Robin/Desktop/cnit2.json')

    # mesh.collect_strips()
    # mesh.collect_polyedges()
    # t0 = time.time()
    # result = quad_mesh_strip_2_coloring(mesh)
    # t1 = time.time()
    # print(t1 - t0, result)
    # # print(quad_mesh_strip_n_coloring(mesh))
    # # print(quad_mesh_polyedge_2_coloring(mesh))
    # # print(quad_mesh_polyedge_n_coloring(mesh))
