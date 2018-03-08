from compas.datastructures.mesh import Mesh

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
    'patterning',
]

def patterning(mesh):
    """Remap a planar mesh in space uv on a spatial surface in space xyz.

    Parameters
    ----------
    planar_mesh : Mesh
        A planar mesh to remap on the surface.
    spatial_surface : Rhino surface guid
        A spatial Rhino surface on which to remap the mesh.

    Returns
    -------
    mesh: Mesh
        The remapped mesh.

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
