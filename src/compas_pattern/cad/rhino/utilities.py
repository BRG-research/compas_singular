try:
    import rhinoscriptsyntax as rs

except ImportError:
    import platform
    if platform.python_implementation() == 'IronPython':
        raise

from compas.utilities import geometric_key

from compas_pattern.cad.rhino.spatial_NURBS_input_to_planar_discrete_output import surface_borders

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
    'is_point_on_curve',
    'surface_border_kinks',
]


def is_point_on_curve(curve_guid, point_xyz):
    geom_key = geometric_key(point_xyz)
    t = rs.CurveClosestPoint(curve_guid, point_xyz)
    pt_on_crv = rs.EvaluateCurve(curve_guid, t)
    geom_key_pt_on_crv = geometric_key(pt_on_crv)
    if geom_key == geom_key_pt_on_crv:
        return True
    else:
        return False

def surface_border_kinks(surface_guid):
    kinks = []
    borders = surface_borders(surface_guid)
    for curve_guid in borders:
        start_tgt = rs.CurveTangent(curve_guid, rs.CurveParameter(curve_guid, 0))
        end_tgt = rs.CurveTangent(curve_guid, rs.CurveParameter(curve_guid, 1))
        if not rs.IsCurveClosed(curve_guid) or not rs.IsVectorParallelTo(start_tgt, end_tgt):
            start = rs.CurveStartPoint(curve_guid)
            end = rs.CurveEndPoint(curve_guid)
            if start not in kinks:
                kinks.append(start)
            if end not in kinks:
                kinks.append(end)

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
