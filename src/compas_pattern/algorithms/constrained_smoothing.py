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
            xyz = mesh.vertex_coordinates(mesh_bdry[0])
            distance_min = -1
            crv = None
            for srf_bdry in surface_boundaries:
                t = rs.CurveClosestPoint(srf_bdry, xyz)
                pt = rs.EvaluateCurve(srf_bdry, t)
                distance = rs.Distance(xyz, pt)
                if distance < distance_min or distance_min < 0:
                    distance_min = distance
                    crv = srf_bdry
            if crv is not None:
                for vkey in mesh_bdry:
                    if vkey not in constraints:
                        constraints[vkey] = ('curve', crv)
        
        else:
            for srf_bdry in surface_boundaries:
                start_xyz = mesh.vertex_coordinates(mesh_bdry[0])
                end_xyz = mesh.vertex_coordinates(mesh_bdry[-1])
                if rs.IsPointOnCurve(srf_bdry, start_xyz) and rs.IsPointOnCurve(srf_bdry, end_xyz):
                    for vkey in mesh_bdry:
                        if vkey not in constraints:
                            constraints[vkey] = ('curve', srf_bdry)
                    break

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