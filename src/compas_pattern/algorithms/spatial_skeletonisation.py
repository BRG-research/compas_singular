from compas.datastructures.mesh import Mesh
from scipy.spatial import Delaunay
from compas.utilities import XFunc

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
    'spatial_skeleton',
]

def spatial_skeleton_xfunc(vertices):

    return spatial_skeleton(vertices)

def spatial_skeleton(vertices):
    """Generate spatial skeleton of a closed mesh.
    
    Parameters
    ----------
    mesh : Mesh
        Closed mesh.

    Returns
    -------
    skeleton : list
        Polylines representing the skeleton branches.

    Raises
    ------
    -

    """

    delaunay_simplices = Delaunay(vertices).simplices.tolist()


    print delaunay_simplices

    return delaunay_simplices

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
