from compas_pattern.datastructures.network.coloring import is_network_two_colorable
from compas.topology import vertex_coloring

__author__ = ['Robin Oval']
__copyright__ = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__ = 'MIT License'
__email__ = 'oval@arch.ethz.ch'

__all__ = [
    'mesh_strip_2_coloring',
    'mesh_strip_n_coloring'
]


def mesh_strip_2_coloring(quad_mesh):
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


def mesh_strip_n_coloring(quad_mesh):
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


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
