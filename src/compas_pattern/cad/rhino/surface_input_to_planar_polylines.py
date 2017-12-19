from compas.cad import SurfaceGeometryInterface
from compas.geometry import subtract_vectors

try:
    import rhinoscriptsyntax as rs
    import scriptcontext as sc

    from Rhino.Geometry import Point3d

    find_object = sc.doc.Objects.Find

except ImportError:
    import platform
    if platform.python_implementation() == 'IronPython':
        raise


from compas_rhino.geometry.surface import RhinoSurface
import compas_rhino as rhino

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
    'surface_input_to_planar_polylines',
]

def surface_borders(surface, border_type = 0):
        """"""
        border = rs.DuplicateSurfaceBorder(surface, border_type)
        curves = rs.ExplodeCurves(border, delete_input = True)
        return curves

def surface_input_to_planar_polylines(discretization_spacing, surface_guid, curve_features_guids = [], point_features_guids = []):
    """Create planar polylines out ot the boundaries of the surfaces and its curve and point features using its UV parameterisation.
    NURBS curves converted into polylines using a discretisation spacing

    Parameters
    ----------
    discretization_spacing
        Spacing value for discretisation of NURBS into polylines.
    surface: Rhino surface guid
        Rhino NURBS surface. Can be untrimmed but cannot be a polysurface.
    curve_features: Rhino curve guid
        Rhino NURBS curve on the surface.
    point_features: Rhino point guid
        Rhino point on the surface.

    Returns
    -------
    planar_param_geometry: list
        Planar parameterised geometrical output: boundary, holes, polyline features and point features.

    Raises
    ------
    -

    """

    #surface = RhinoSurface(surface_guid)
    
    boundaries = rs.JoinCurves(surface_borders(surface_guid, border_type = 1), delete_input = True)
    boundary_polylines = [rs.ConvertCurveToPolyline(boundary, angle_tolerance = 5.0, tolerance = 0.01, delete_input = True, min_edge_length = 0, max_edge_length = discretization_spacing) for boundary in boundaries]
    boundary_polylines_UV = [[rs.SurfaceClosestPoint(surface_guid, vertex) for vertex in rs.PolylineVertices(boundary_polyline)] for boundary_polyline in boundary_polylines]
    rs.DeleteObjects(boundaries)

    holes = rs.JoinCurves(surface_borders(surface_guid, border_type = 2), delete_input = True)
    hole_polylines = [rs.ConvertCurveToPolyline(hole, angle_tolerance = 5.0, tolerance = 0.01, delete_input = True, min_edge_length = 0, max_edge_length = discretization_spacing) for hole in holes]
    hole_polylines_UV = [[rs.SurfaceClosestPoint(surface_guid, vertex) for vertex in rs.PolylineVertices(hole_polyline)] for hole_polyline in hole_polylines]
    rs.DeleteObjects(holes)

    polyline_features = [rs.ConvertCurveToPolyline(curve_features_guid, angle_tolerance = 5.0, tolerance = 0.01, delete_input = True, min_edge_length = 0, max_edge_length = discretization_spacing) for curve_features_guid in curve_features_guids]
    polyline_features_UV = [[rs.SurfaceClosestPoint(surface_guid, vertex) for vertex in rs.PolylineVertices(polyline_feature)] for polyline_feature in polyline_features]

    point_features_UV = [rs.SurfaceClosestPoint(surface_guid, point) for point in point_features_guids]

    return boundary_polylines_UV, hole_polylines_UV, polyline_features_UV, point_features_UV


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
