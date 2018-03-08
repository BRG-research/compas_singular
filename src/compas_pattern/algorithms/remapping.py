try:
    import rhinoscriptsyntax as rs

except ImportError:
    import platform
    if platform.python_implementation() == 'IronPython':
        raise

from compas.datastructures.mesh import Mesh

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
    'remapping',
]

def remapping(mesh, surface_guid):
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

    for vkey in mesh.vertices():
        u, v, w = mesh.vertex_coordinates(vkey)
        x, y, z = rs.EvaluateSurface(surface_guid, u, v)
        attr = mesh.vertex[vkey]
        attr['x'] = x
        attr['y'] = y
        attr['z'] = z

    return mesh


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
