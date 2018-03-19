try:
    import rhinoscriptsyntax as rs

except ImportError:
    import platform
    if platform.python_implementation() == 'IronPython':
        raise

from compas_rhino.geometry.surface import RhinoSurface

import compas_rhino as rhino

from compas_pattern.cad.rhino.utilities import surface_borders
from compas_pattern.cad.rhino.utilities import curve_discretisation

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
    'mapping',
]


def mapping(discretization_spacing, surface_guid, curve_features_guids = [], point_features_guids = []):
    """Creates planar polylines from the boundaries of a NURBS surface, NURBS curves and point on the NURBS surface
    by using the UV parameterisation with a user-input discretisation spacing.

    Parameters
    ----------
    discretization_spacing: real
        Spacing value for discretisation of NURBS surface borders and curves into polylines.
    surface: Rhino surface guid
        Untrimmed or trimmed Rhino NURBS surface.
    curve_features: Rhino curve guid
        Rhino NURBS curve on the surface.
    point_features: Rhino point guid
        Rhino point on the surface.

    Returns
    -------
    output: list
        Planar parameterised geometrical output: boundary, holes, polyline features and point features.

    Raises
    ------
    -

    """
    
    boundaries = surface_borders(surface_guid, border_type = 1)
    boundary_polylines = [curve_discretisation(boundary, discretization_spacing) for boundary in boundaries]
    uv_boundary_polylines = [[rs.SurfaceClosestPoint(surface_guid, vertex) for vertex in rs.PolylineVertices(boundary_polyline)] for boundary_polyline in boundary_polylines]
    planar_boundary_polylines = [[[u, v, 0] for u, v in uv_boundary_polyline] for uv_boundary_polyline in uv_boundary_polylines]
    planar_boundary_polyline = []
    for polyline in planar_boundary_polylines:
        planar_boundary_polyline += polyline[: -1]
    planar_boundary_polyline.append(planar_boundary_polyline[0])
    rs.DeleteObjects(boundaries)
    rs.DeleteObjects(boundary_polylines)

    holes = surface_borders(surface_guid, border_type = 2)
    holes = rs.JoinCurves(holes, delete_input = True)
    hole_polylines = [curve_discretisation(hole, discretization_spacing) for hole in holes]
    uv_hole_polylines = [[rs.SurfaceClosestPoint(surface_guid, vertex) for vertex in rs.PolylineVertices(hole_polyline)] for hole_polyline in hole_polylines]
    planar_hole_polylines = [[[u, v, 0] for u, v in hole] for hole in uv_hole_polylines]
    rs.DeleteObjects(holes)
    rs.DeleteObjects(hole_polylines)

    polyline_features = [curve_discretisation(curve_features_guid, discretization_spacing) for curve_features_guid in curve_features_guids]
    uv_polyline_features = [[rs.SurfaceClosestPoint(surface_guid, vertex) for vertex in rs.PolylineVertices(polyline_feature)] for polyline_feature in polyline_features]
    planar_polyline_features = [[[u, v, 0] for u, v in feature] for feature in uv_polyline_features]
    rs.DeleteObjects(polyline_features)

    uv_point_features = [rs.SurfaceClosestPoint(surface_guid, point) for point in point_features_guids]
    planar_point_features = [[u, v, 0] for u, v in uv_point_features]

    return planar_boundary_polyline, planar_hole_polylines, planar_polyline_features, planar_point_features

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
