try:
    import rhinoscriptsyntax as rs

except ImportError:
    import platform
    if platform.python_implementation() == 'IronPython':
        raise

from compas.utilities import geometric_key

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
    'surface_borders',
    'spatial_NURBS_input_to_planar_discrete_output',
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
    


    return 0

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
