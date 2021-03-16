from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

import rhinoscriptsyntax as rs

from compas.geometry import distance_point_point
from compas.geometry import closest_point_in_cloud
from compas.geometry import Polyline

from compas_rhino.geometry import RhinoPoint
# from compas_rhino.geometry import RhinoMesh
# from compas_rhino.artists import MeshArtist
# from compas_rhino.objects import mesh_select_vertices

from compas_singular.utilities import list_split

# from ..geometry import RhinoSurface
from ..geometry import RhinoCurve


__all__ = [
    'automated_smoothing_surface_constraints',
    'automated_smoothing_constraints',
    # 'customized_smoothing_constraints',
    # 'display_smoothing_constraints'
]


def automated_smoothing_surface_constraints(mesh, surface):
    """Apply automatically surface-related constraints to the vertices of a mesh to smooth: kinks, boundaries and surface.

    Parameters
    ----------
    mesh : Mesh
        The mesh to apply the constraints to for smoothing.
    surface : :class:`compas_singular.rhino.RhinoSurface`
        A Rhino surface on which to constrain mesh vertices.

    Returns
    -------
    constraints : dict
        A dictionary of mesh constraints for smoothing as vertex keys pointing to point, curve or surface objects.

    """
    constraints = {}

    points = [RhinoPoint.from_guid(rs.AddPoint(point)) for point in surface.kinks()]
    curves = [RhinoCurve.from_guid(guid) for guid in surface.borders(border_type=0)]

    constraints.update({vertex: surface for vertex in mesh.vertices()})

    for vertex in [vkey for bdry in mesh.vertices_on_boundaries() for vkey in bdry]:
        xyz = mesh.vertex_coordinates(vertex)
        projections = [(curve, distance_point_point(xyz, curve.closest_point(xyz))) for curve in curves]
        constraints[vertex] = min(projections, key=lambda x: x[1])[0]

    index_vertex = {index: vertex for index, vertex in enumerate([vkey for bdry in mesh.vertices_on_boundaries() for vkey in bdry])}
    boundary = [mesh.vertex_coordinates(vertex) for bdry in mesh.vertices_on_boundaries() for vertex in bdry]
    constraints.update({index_vertex[closest_point_in_cloud(point.xyz, boundary)[2]]: point for point in points})

    return constraints


def automated_smoothing_constraints(mesh, rhinopoints=None, rhinocurves=None, rhinosurface=None, rhinomesh=None):
    """Apply automatically point, curve and surface constraints to the vertices of a mesh to smooth.

    Parameters
    ----------
    mesh : Mesh
        The mesh to apply the constraints to for smoothing.
    rhinopoints : list
        List of XYZ coordinates on which to constrain mesh vertices.
        Default is None.
    rhinocurves : list of :class:`compas_singular.rhino.RhinoCurve`, optional
        List of Rhino curves on which to constrain mesh vertices.
        Default is None.
    rhinosurface : :class:`compas_singular.rhino.RhinoSurface`, optional
        A Rhino surface guid on which to constrain mesh vertices.
        Default is None.
    rhinomesh : :class:`compas_singular.rhino.RhinoCurve`, optional
        A Rhino mesh guid on which to constrain mesh vertices.
        Default is None.

    Returns
    -------
    constraints : dict
        A dictionary of mesh constraints for smoothing as vertex keys pointing to point, curve or surface objects.

    """
    constraints = {}
    constrained_vertices = {}

    vertices = list(mesh.vertices())
    cloud = [mesh.vertex_coordinates(vertex) for vertex in mesh.vertices()]

    if rhinopoints:
        constrained_vertices.update({vertices[closest_point_in_cloud(point.xyz, cloud)[2]]: point for point in rhinopoints})

    if rhinomesh:
        constraints.update({vertex: rhinomesh for vertex in mesh.vertices()})

    if rhinosurface:
        constraints.update({vertex: rhinosurface for vertex in mesh.vertices()})

    if rhinocurves:
        boundaries = [
            split_boundary for boundary in mesh.boundaries()
            for split_boundary in list_split(boundary, [boundary.index(vertex) for vertex in constrained_vertices.keys() if vertex in boundary])]

        boundary_polylines = [Polyline([mesh.vertex_coordinates(vertex) for vertex in boundary]) for boundary in boundaries]
        boundary_midpoints = [polyline.point(t=0.5) for polyline in boundary_polylines]
        curve_midpoints = [rs.EvaluateCurve(curve.guid, rs.CurveParameter(curve.guid, 0.5)) for curve in rhinocurves]

        midpoint_map = {index: closest_point_in_cloud(boundary_midpoint, curve_midpoints)[2] for index, boundary_midpoint in enumerate(boundary_midpoints)}

        constraints.update({vertex: rhinocurves[midpoint_map[index]] for index, boundary in enumerate(boundaries) for vertex in boundary})

    if rhinopoints:
        constraints.update(constrained_vertices)

    return constraints


# def customized_smoothing_constraints(mesh, constraints):
#     """Add custom point, curve and surface constraints to the vertices of a mesh to smooth.

#     Parameters
#     ----------
#     mesh : Mesh
#         The mesh to apply the constraints to for smoothing.
#     constraints : dict
#         A dictionary of mesh constraints for smoothing as vertex keys pointing to point, curve or surface objects.

#     Returns
#     -------
#     constraints : dict
#         The updated dictionary of mesh constraints for smoothing as vertex keys pointing to point, curve or surface objects.

#     """

#     while True:

#         guids = display_smoothing_constraints(mesh, constraints)
#         vertexs = mesh_select_vertices(mesh)
#         if len(vertexs) == 2 and rs.GetString('get all polyedge?', strings=['True', 'False']) == 'True':
#             u, v = vertexs
#             vertexs = mesh.polyedge(u, v)

#         if vertexs is None:
#             break

#         constraint = rs.GetString('edit smoothing constraints?', strings=['point', 'curve', 'surface', 'exit'])

#         rs.DeleteObjects(guids)

#         if constraint is None or constraint == 'exit':
#             break

#         elif constraint == 'point':
#             point = RhinoPoint.from_selection()
#             constraints.update({vertex: point.guid for vertex in vertexs})

#         elif constraint == 'curve':
#             curve = RhinoCurve.from_selection()
#             constraints.update({vertex: curve.guid for vertex in vertexs})

#         elif constraint == 'surface':
#             surface = RhinoSurface.from_selection()
#             constraints.update({vertex: surface.guid for vertex in vertexs})

#     return constraints


# def display_smoothing_constraints(mesh, constraints):
#     """Display current state of constraints on the vertices of a mesh to smooth.

#     Parameters
#     ----------
#     mesh : Mesh
#         The mesh to apply the constraints to for smoothing.
#     constraints : dict
#         A dictionary of mesh constraints for smoothing as vertex keys pointing to point, curve or surface objects.

#     Returns
#     -------
#     guid
#         Guid of Rhino points coloured according to the type of constraint applied.

#     """

#     # color = {vertex: (255, 0, 0) if vertex in constraints and rs.ObjectType(constraints[vertex]) == 1
#     #          else (0, 255, 0) if vertex in constraints and rs.ObjectType(constraints[vertex]) == 4
#     #          else (0, 0, 255) if vertex in constraints and rs.ObjectType(constraints[vertex]) == 8
#     #          else (0, 0, 0) for vertex in mesh.vertices()}

#     guids_index = {guid: i for i, guid in enumerate(list(set(constraints.values())))}
#     n = len(guids_index.keys())
#     color = {}
#     for vertex in mesh.vertices():
#         if vertex in constraints:
#             k = float(guids_index[constraints[vertex]]) / float((n - 1))
#             color[vertex] = (int(255.0 * k), int(255.0 * (1.0 - k)), 0)
#         else:
#             color[vertex] = (0, 0, 0)

#     artist = MeshArtist(mesh)
#     return artist.draw_vertices(color=color)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass
