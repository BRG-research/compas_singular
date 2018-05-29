import math

import compas_rhino as rhino

try:
    import rhinoscriptsyntax as rs

except ImportError:
    import platform
    if platform.python_implementation() == 'IronPython':
        raise

from compas.datastructures.mesh import Mesh

from compas.utilities import geometric_key

from compas_pattern.topology.polyline_extraction import mesh_boundaries

from compas_pattern.cad.rhino.utilities import surface_borders
from compas_pattern.cad.rhino.utilities import is_point_on_curve

from compas_pattern.cad.rhino.utilities import draw_mesh

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
    'define_constraints',
    'automatic_constraints',
    'customed_constraints',
    'apply_constraints',
]

def define_constraints(mesh, surface_constraint, curve_constraints = [], point_constraints = [], custom = True):

    constraints, surface_boundaries = automatic_constraints(mesh, surface_constraint, curve_constraints, point_constraints)
    
    if custom:
        constraints = customed_constraints(mesh, constraints, surface_boundaries, surface_constraint)

    return constraints, surface_boundaries

def automatic_constraints(mesh, surface_constraint, curve_constraints = [], point_constraints = []):
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
            constraints[vkey] = ['point', xyz]

    # set boundary curve constraints
    split_vertices = [vkey for vkey, constraint in constraints.items() if constraint[0] == 'point']
    split_mesh_boundaries = mesh_boundaries(mesh, vertex_splits = split_vertices)

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
                        constraints[vkey] = ['curve', crv_cstr]
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
                        constraints[vkey] = ['curve', crv_cstr]
        
        else:
            for srf_bdry in surface_boundaries:
                start_xyz = mesh.vertex_coordinates(mesh_bdry[0])
                end_xyz = mesh.vertex_coordinates(mesh_bdry[-1])
                # if the mesh boundary extremities match the ones of the curve boundary...
                if is_point_on_curve(srf_bdry, start_xyz) and is_point_on_curve(srf_bdry, end_xyz):
                    # ... and if there is an intermediary mesh boundary vertex on this curve boundary (needed for two-sided boundary elements)
                    to_constrain = False
                    for vkey in mesh_bdry[1 : -1]:
                        if is_point_on_curve(srf_bdry, mesh.vertex_coordinates(vkey)):
                            to_constrain = True
                    if to_constrain:
                        crv_cstr = srf_bdry
                        for vkey in mesh_bdry:
                            xyz = mesh.vertex_coordinates(vkey)
                            if is_point_on_curve(crv_cstr, xyz) and vkey not in constraints:
                                constraints[vkey] = ['curve', crv_cstr]
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
                                constraints[vkey] = ['curve', crv_cstr]

    # constrain to point features
    point_constraints_keys = [geometric_key(rs.PointCoordinates(pt)) for pt in point_constraints]
    for vkey in mesh.vertices():
        xyz = mesh.vertex_coordinates(vkey)
        geom_key = geometric_key(xyz)
        if geom_key in point_constraints_keys:
            constraints[vkey] = ['point', xyz]

    # constrain to curve features
    for crv in curve_constraints:
        # extremities
        start = rs.CurveStartPoint(crv)
        start_geom_key = geometric_key(start)
        end = rs.CurveEndPoint(crv)
        end_geom_key = geometric_key(end)
        for vkey in mesh.vertices():
            xyz = mesh.vertex_coordinates(vkey)
            geom_key = geometric_key(xyz)
            if geom_key == start_geom_key:
                constraints[vkey] = ['point', xyz]
                start_key = vkey
            if geom_key == end_geom_key:
                constraints[vkey] = ['point', xyz]
                end_key = vkey
        # regular nodes
        path = [start_key]
        for nbr in mesh.vertex_neighbours(start_key):
            completed = False
            if mesh.is_vertex_on_boundary(nbr):
                continue
            path.append(nbr)
            count = len(list(mesh.vertices()))
            while count > 0:
                count -= 1
                u, v = path[-2], path[-1]
                fkey = mesh.halfedge[u][v]
                x = mesh.face_vertex_descendant(fkey, v)
                fkey = mesh.halfedge[x][v]
                w = mesh.face_vertex_descendant(fkey, v)
                path.append(w)
                if w == end_key:
                    completed = True
                    break
                elif mesh.is_vertex_on_boundary(w) or len(mesh.vertex_neighbours(w)) != 4:
                    break
            if completed:
                break
            else:
                path = [start_key]
        for vkey in path[1 : -1]:
            constraints[vkey] = ['curve', crv]

        
    # set surface constraints by default for the others
    for vkey in mesh.vertices():
        if vkey not in constraints:
            constraints[vkey] = ['surface', surface_constraint]

    # udpdate drawn mesh
    layer = 'pattern_topology'
    mesh_guid = rs.ObjectsByLayer(layer)[0]
    rs.DeleteObject(mesh_guid)
    mesh_guid = draw_mesh(mesh)
    rs.ObjectLayer(mesh_guid, layer)

    return constraints, surface_boundaries

def customed_constraints(mesh, constraints, surface_boundaries, surface_constraint):

    count = 1000
    while count > 0:
        count -= 1


        all_curve_constraints = []
        for vkey, constraint in constraints.items():
            constraint_type, constraint_object = constraint
            if constraint_type == 'curve' and constraint_object not in all_curve_constraints:
                all_curve_constraints.append(constraint_object)
        n  = len(all_curve_constraints)
        rs.EnableRedraw(False)
        dots = []
        for i, crv in enumerate(all_curve_constraints):
            dot = rs.AddTextDot(i, rs.CurveMidPoint(crv))
            dots.append(dot)
            rs.ObjectColor(dot, [0, float(i) / n * 255, (n - float(i)) / n * 255])
        rs.EnableRedraw(True)

        # display  vertices to select with colour code
        vertex_colors = {}
        for vkey, constraint in constraints.items():
            contraint_type, constraint_object = constraint
            if contraint_type == 'point':
                rgb = [255, 0, 255]
            elif contraint_type == 'curve':
                i = all_curve_constraints.index(constraint_object)
                rgb = [0, float(i) / n * 255, (n - float(i)) / n * 255]
            elif contraint_type == 'surface':
                rgb = [255, 255, 255]
            else:
                rgb = [0, 0, 0]
            vertex_colors[vkey] = rgb

        artist = rhino.MeshArtist(mesh, layer='mesh_artist')
        artist.clear_layer()
        
        artist.draw_vertices(color = vertex_colors)
        artist.redraw()
        vkeys = rhino.mesh_select_vertices(mesh, message = 'change vertex constraints?')
        artist.clear_layer()
        artist.redraw()
        
        rs.DeleteLayer('mesh_artist')

        if vkeys == []:
            rs.DeleteObjects(dots)
            return constraints

        rs.EnableRedraw(True)

        constraint_types = ['point', 'curve', 'surface', 'none']
        new_constraint_type = rs.GetString('constraint type?', strings = constraint_types)

        # set new point constraint
        if new_constraint_type == 'point':
            for vkey in vkeys:
                constraints[vkey][0] = 'point'

                # if single vertex, possibility to update position
                if len(vkeys) == 1:
                    xyz = rs.GetPoint('new point location?')
                    if xyz is not None:
                        constraints[vkey][1] = xyz
                        x, y, z = xyz
                        attr = mesh.vertex[vkey]
                        attr['x'] = x
                        attr['y'] = y
                        attr['z'] = z

                        # udpdate drawn mesh
                        layer = 'pattern_topology'
                        mesh_guid = rs.ObjectsByLayer(layer)[0]
                        rs.DeleteObject(mesh_guid)
                        mesh_guid = draw_mesh(mesh)
                        rs.ObjectLayer(mesh_guid, layer)

        # set new curve constraint
        elif new_constraint_type == 'curve':
            curve_constraint = rs.GetObject('curve constraint?', filter = 4)
            for vkey in vkeys:
                constraints[vkey] = ['curve', curve_constraint]

        # set new surface constraint
        elif new_constraint_type == 'surface':
            for vkey in vkeys:
                constraints[vkey] = ['surface', surface_constraint]

        # remove constraint
        elif new_constraint_type == 'none':
            for vkey in vkeys:
                constraints[vkey] = ['none', None]

        rs.DeleteObjects(dots)

        rs.EnableRedraw(False)

    return constraints

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
            if not rs.IsPointOnSurface(cstr_object, [x, y, z]):
                borders = surface_borders(cstr_object)
                xyz0 = [x, y, z]
                min_dist = -1
                pt = None
                for border in borders:
                    t = rs.CurveClosestPoint(border, xyz0)
                    xyz = rs.EvaluateCurve(border, t)
                    dist = rs.Distance(xyz, xyz0)
                    if dist < min_dist or min_dist < 0:
                        min_dist = dist
                        pt = xyz
                x, y, z = pt
                rs.DeleteObjects(borders)
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