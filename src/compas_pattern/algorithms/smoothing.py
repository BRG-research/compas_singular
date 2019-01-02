try:
    import rhinoscriptsyntax as rs

except ImportError:
    import platform
    if platform.python_implementation() == 'IronPython':
        raise

from compas.geometry.algorithms.smoothing_cpp import smooth_centroid_cpp

from compas.geometry.algorithms.smoothing import mesh_smooth_centroid
from compas.geometry.algorithms.smoothing import mesh_smooth_area
from compas.geometry.algorithms.smoothing import mesh_smooth_centerofmass

from compas_rhino.geometry import RhinoPoint
from compas_pattern.cad.rhino.objects.curve import RhinoCurve
from compas_pattern.cad.rhino.objects.surface import RhinoSurface


__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
    'constrained_smoothing',
    'surface_constrained_smoothing',
]

def constrained_smoothing(mesh, kmax = 100, damping = 0.5, constraints = {}, algorithm = 'centroid'):
    """Constrained smoothing of a mesh. Constraints can be points, curves or surfaces.

    Parameters
    ----------
    mesh : Mesh
        A mesh to smooth.
    kmax : int
        Number of iterations for smoothing. Default value 100.
    damping : float
        Damping value for smoothing between 0 and 1. Default value 0.5.
    constraints : dict
        Dictionary of constraints as vertex keys pointing to Rhino objects (points, curves or surfaces). Emplty by default.
    algorithm : string
        Type of smoothing algorithm to apply (classic centroid or area-based). Classic centroid by default.

    """

    def callback(k, args):

        mesh, constraints = args

        for vkey, constraint in constraints.items():
            if rs.ObjectType(constraint) == 1:
                x, y, z = RhinoPoint(constraint).xyz
            elif rs.ObjectType(constraint) == 4:
                x, y, z = RhinoCurve(constraint).closest_point(mesh.vertex_coordinates(vkey))
            elif rs.ObjectType(constraint) == 8:
                x, y, z = RhinoSurface(constraint).closest_point(mesh.vertex_coordinates(vkey))
            else:
                continue

            mesh.vertex[vkey]['x'] = x
            mesh.vertex[vkey]['y'] = y
            mesh.vertex[vkey]['z'] = z

    func = {'centroid': mesh_smooth_centroid, 'area': mesh_smooth_area, 'centerofmass': mesh_smooth_centerofmass}

    if algorithm not in func:
        algorithm = 'centroid'
        
    func[algorithm](mesh, kmax = kmax, damping = damping, callback = callback, callback_args = [mesh, constraints])

def surface_constrained_smoothing(mesh, srf, kmax = 100, damping = 0.5, algorithm = 'centroid'):
    """Specific surface constrained smoothing of a mesh. Constraints are automatically applied based on the surface, its boundary and its corners.

    Parameters
    ----------
    mesh : Mesh
        A mesh to smooth.
    srf : RhinoSurface
        A RhinoSurface on which to constrain the mesh.
    kmax : int
        Number of iterations for smoothing. Default value 100.
    damping : float
        Damping value for smoothing between 0 and 1. Default value 0.5.
    algorithm : string
        Type of smoothing algorithm to apply (classic centroid or area-based). Classic centroid by default.

    """

    fixed = [vkey for vkey in mesh.vertices_on_boundary() if mesh.vertex_valency(vkey) == 2]

    def callback(k, args):

        mesh, srf = args

        for vkey, attr in mesh.vertices(True):
            if mesh.is_vertex_on_boundary(vkey):
                x, y, z = srf.closest_point_on_boundaries(mesh.vertex_coordinates(vkey))
            else:
                x, y, z = srf.closest_point(mesh.vertex_coordinates(vkey))
    
            attr['x'] = x
            attr['y'] = y
            attr['z'] = z

    callback_args = [mesh, srf]

    func = {'centroid': mesh_smooth_centroid, 'area': mesh_smooth_area}

    if algorithm not in func:
        algorithm = 'centroid'
        
    func[algorithm](mesh, fixed, kmax, damping, callback, callback_args)

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas