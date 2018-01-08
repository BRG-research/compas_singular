import math

try:
    import rhinoscriptsyntax as rs

except ImportError:
    import platform
    if platform.python_implementation() == 'IronPython':
        raise

from compas.datastructures.mesh import Mesh

from compas.utilities import geometric_key

from compas_pattern.topology.polyline_extraction import mesh_polylines_boundary

from compas_pattern.cad.rhino.spatial_NURBS_input_to_planar_discrete_output import surface_borders
from compas_pattern.cad.rhino.utilities import is_point_on_curve

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
    'define_constraints',
    'define_constraints',
]

def define_constraints(mesh, surface_constraint, curve_constraints = [], point_constraints = []):
    """Defines the constraints on the vertices of the mesh on a point, a curve or a surface.
    
    Parameters
    ----------
    mesh : Mesh
        A mesh.
    surface_constraint : Rhino surface guid
        A surface to project vertices.
    curve_constraints : Rhino curve guids
        Curve features on surface to constrain vertices.
    point_constraints : Rhino point guids
        Point features on surface to constrain vertices.

    Returns
    -------
    constraints: dict
        Dictionary of constraints {vertex_key: (constraint_type, constraint_information)}.

    Raises
    ------
    -

    """

    constraints = {}

    surface_boundaries = surface_borders(surface_constraint, border_type = 0)

    # set point constraints at point feature, curve feature extremities and boundary curve corners
    constrained_points = []
    for curve_guid in surface_boundaries:
        start_tgt = rs.CurveTangent(curve_guid, rs.CurveParameter(curve_guid, 0))
        end_tgt = rs.CurveTangent(curve_guid, rs.CurveParameter(curve_guid, 1))
        # add only if not closed or closed with a kink
        if not rs.IsCurveClosed(curve_guid) or not rs.IsVectorParallelTo(start_tgt, end_tgt):
            start = geometric_key(rs.CurveStartPoint(curve_guid))
            end = geometric_key(rs.CurveEndPoint(curve_guid))
            if start not in constrained_points:
                constrained_points.append(start)
            if end not in constrained_points:
                constrained_points.append(end)

    for vkey in mesh.vertices():
        xyz = mesh.vertex_coordinates(vkey)
        geom_key = geometric_key(xyz)
        if geom_key in constrained_points:
            constraints[vkey] = ('surface_corner', xyz)

    # set boundary curve constraints

    # collect boundary polylines with splits
    mesh_boundaries = mesh_polylines_boundary(mesh)
    split_vertices = [vkey for vkey, constraint in constraints.items() if constraint[0] == 'surface_corner']

    # add one vertex per mesh boundary element that has no split vertices yet, i.e. that has no corner vertices (2-valency)
    for boundary in mesh_boundaries:
        to_add = True
        for vkey in boundary:
            if vkey in split_vertices:
                to_add = False
                break
        if to_add:
            split_vertices.append(boundary[0])


    split_mesh_boundaries = []
    while len(split_vertices) > 0:
        start = split_vertices.pop()
        # exception if split vertex corresponds to a non-boundary point feature
        if not mesh.is_vertex_on_boundary(start):
            continue
        polyline = [start]

        while 1:
            for nbr, fkey in iter(mesh.halfedge[polyline[-1]].items()):
                if fkey is None:
                    polyline.append(nbr)
                    break

            # end of boundary element
            if start == polyline[-1]:
                split_mesh_boundaries.append(polyline)
                break
            # end of boundary subelement
            elif polyline[-1] in split_vertices:
                split_mesh_boundaries.append(polyline)
                split_vertices.remove(polyline[-1])
                polyline = polyline[-1 :]

    # constrain a mesh boundary to a surface boundary if the two extremities of the mesh boundary are on the surface boundary
    for mesh_bdry in split_mesh_boundaries:

        if mesh_bdry[0] == mesh_bdry[-1]:
            crv_cstr = None
            for vkey in mesh_bdry:
                xyz = mesh.vertex_coordinates(vkey)
                for srf_bdry in surface_boundaries:
                    if is_point_on_curve(srf_bdry, xyz):
                        crv_cstr = srf_bdry
                        break
                if crv_cstr is not None:
                    break
            if crv_cstr is not None:
                for vkey in mesh_bdry:
                    xyz = mesh.vertex_coordinates(vkey)
                    if is_point_on_curve(crv_cstr, xyz) and vkey not in constraints:
                        constraints[vkey] = ('curve', crv_cstr)
                for i, vkey in enumerate(mesh_bdry):
                    if vkey not in constraints:
                        # find next contrained point
                        n_plus = 1
                        norm_t_plus = None
                        count = len(mesh_bdry)
                        while count > 0:
                            count -= 1
                            vkey_plus = mesh_bdry[i + n_plus - len(mesh_bdry)]
                            if vkey_plus in constraints:
                                norm_t_plus = rs.CurveNormalizedParameter(crv_cstr, rs.CurveClosestPoint(crv_cstr, mesh.vertex_coordinates(vkey_plus)))
                            else:
                                n_plus += 1
                        # find previous contrained point
                        n_minus = 1
                        norm_t_minus = None
                        count = len(mesh_bdry)
                        while count > 0:
                            count -= 1
                            vkey_minus = mesh_bdry[i - n_minus]
                            if vkey_minus in constraints:
                                norm_t_minus = rs.CurveNormalizedParameter(crv_cstr, rs.CurveClosestPoint(crv_cstr, mesh.vertex_coordinates(vkey_minus)))
                            else:
                                n_minus += 1
                        # calculate barycentric parameter and move to it
                        # dichotomy required in case of curve seam being between the two parameters
                        #print n_minus, norm_t_minus, n_plus, norm_t_plus
                        if norm_t_minus == norm_t_plus:
                            norm_t = (norm_t_plus + .5) % 1
                        elif norm_t_minus < norm_t_plus:
                            norm_t = (n_minus * norm_t_plus + n_plus * norm_t_minus) / (n_minus + n_plus)
                        else:
                            norm_t_plus += 1
                            norm_t = (n_minus * norm_t_plus + n_plus * norm_t_minus) / (n_minus + n_plus)
                        # update coordiantes
                        t = rs.CurveParameter(crv_cstr, norm_t)
                        x, y, z = rs.EvaluateCurve(crv_cstr, t)
                        attr = mesh.vertex[vkey]
                        attr['x'] = x
                        attr['y'] = y
                        attr['z'] = z
                        # store constraint
                        constraints[vkey] = ('curve', crv_cstr)
        
        else:
            for srf_bdry in surface_boundaries:
                start_xyz = mesh.vertex_coordinates(mesh_bdry[0])
                end_xyz = mesh.vertex_coordinates(mesh_bdry[-1])
                if is_point_on_curve(srf_bdry, start_xyz) and is_point_on_curve(srf_bdry, end_xyz):
                    start_t = rs.CurveClosestPoint(srf_bdry, start_xyz)
                    end_t = rs.CurveClosestPoint(srf_bdry, end_xyz)
                    for i, vkey in enumerate(mesh_bdry):
                        if vkey not in constraints:
                            # project point on curve constraint at barycentric curve parameter 
                            n = len(mesh_bdry)
                            t = (i * end_t + (n - 1 - i) * start_t) / (n - 1)
                            x, y, z = rs.EvaluateCurve(srf_bdry, t)
                            attr = mesh.vertex[vkey]
                            attr['x'] = x
                            attr['y'] = y
                            attr['z'] = z
                            constraints[vkey] = ('curve', srf_bdry)
                    break


    # constrain to curve features
    
    
    # set surface constraints by default for the others
    for vkey in mesh.vertices():
        if vkey not in constraints:
            constraints[vkey] = ('surface', surface_constraint)

    return constraints, surface_boundaries

def apply_constraints(k, args):
    """Apply the constraints on the vertices of the mesh on a point, a curve or a surface.
    
    Parameters
    ----------
    mesh : Mesh
        A mesh.
    constraints : dict
        A dictionary with constraints on mesh vertices: {vertex_key: (constraint_type, constraint_information)}.

    Returns
    -------

    Raises
    ------
    -

    """

    mesh, constraints = args

    for vkey, constraint in constraints.items():
        cstr_type, cstr_object = constraint

        if cstr_type == 'curve':
            xyz = mesh.vertex_coordinates(vkey)
            t = rs.CurveClosestPoint(cstr_object, xyz)
            x, y, z = rs.EvaluateCurve(cstr_object, t)
            attr = mesh.vertex[vkey]
            attr['x'] = x
            attr['y'] = y
            attr['z'] = z

        elif cstr_type == 'surface':
            xyz = mesh.vertex_coordinates(vkey)
            u, v = rs.SurfaceClosestPoint(cstr_object, xyz)
            x, y, z = rs.EvaluateSurface(cstr_object, u, v)
            attr = mesh.vertex[vkey]
            attr['x'] = x
            attr['y'] = y
            attr['z'] = z


    return 0

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas