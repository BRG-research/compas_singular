from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from compas.datastructures import mesh_smooth_centerofmass
from compas.datastructures import mesh_smooth_area
from compas.datastructures import mesh_smooth_centroid

# from compas_rhino.geometry import RhinoMesh
# from compas_rhino.geometry import RhinoPoint

# from ..geometry import RhinoSurface
# from ..geometry import RhinoCurve


__all__ = [
    'constrained_smoothing',
    'surface_constrained_smoothing',
]


def constrained_smoothing(mesh, kmax=100, damping=0.5, constraints={}, algorithm='centroid'):
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
        for vertex, constraint in constraints.items():
            if not constraint:
                continue
            x, y, z = constraint.closest_point(mesh.vertex_coordinates(vertex))
            mesh.vertex[vertex]['x'] = x
            mesh.vertex[vertex]['y'] = y
            mesh.vertex[vertex]['z'] = z

    if algorithm == 'area':
        return mesh_smooth_area(mesh, kmax=kmax, damping=damping, callback=callback, callback_args=[mesh, constraints])

    if algorithm == 'centerofmass':
        return mesh_smooth_centerofmass(mesh, kmax=kmax, damping=damping, callback=callback, callback_args=[mesh, constraints])

    return mesh_smooth_centroid(mesh, kmax=kmax, damping=damping, callback=callback, callback_args=[mesh, constraints])


def surface_constrained_smoothing(mesh, srf, kmax=100, damping=0.5, algorithm='centroid'):
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
    def callback(k, args):
        mesh, srf = args
        for vertex, attr in mesh.vertices(True):
            if mesh.is_vertex_on_boundary(vertex):
                x, y, z = srf.closest_point_on_boundaries(mesh.vertex_coordinates(vertex))
            else:
                x, y, z = srf.closest_point(mesh.vertex_coordinates(vertex))
            attr['x'] = x
            attr['y'] = y
            attr['z'] = z

    fixed = [vertex for bdry in mesh.vertices_on_boundaries() for vertex in bdry if mesh.vertex_degree(vertex) == 2]

    if algorithm == 'area':
        return mesh_smooth_area(mesh, fixed, kmax, damping, callback, [mesh, srf])

    return mesh_smooth_centroid(mesh, fixed, kmax, damping, callback, [mesh, srf])


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass
