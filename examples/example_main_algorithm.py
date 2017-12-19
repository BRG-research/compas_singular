import rhinoscriptsyntax as rs

import compas_rhino as rhino

from compas.datastructures.mesh import Mesh

from compas.utilities import geometric_key

from compas_pattern.cad.rhino.surface_input_to_planar_polylines import surface_input_to_planar_polylines
from compas_pattern.algorithms.polylines_to_delaunay import polylines_to_delaunay
from compas_pattern.topology.unweld_mesh_along_edge_path import unweld_mesh_along_edge_path
from compas_pattern.algorithms.delaunay_to_qpd import delaunay_to_patch_decomposition
from compas_pattern.topology.polylines_to_mesh import polylines_to_mesh

# collect spatial shape: surface/mesh + features
surface_guid = rs.GetSurfaceObject('select surface')[0]
curve_features_guids = rs.GetObjects('select curve features', filter = 4)
if curve_features_guids is None:
    curve_features_guids = []
point_features_guids = rs.GetPoints('select point features')
if point_features_guids is None:
    point_features_guids = []

# parameterisation from spatial to planar

discretisation = rs.GetReal('discretisation')

rs.EnableRedraw(False)
output = surface_input_to_planar_polylines(discretisation, surface_guid, curve_features_guids = curve_features_guids, point_features_guids = point_features_guids)

boundary_polylines_UV, hole_polylines_UV, polyline_features_UV, point_features_UV = output

boundary_polyline_guid = rs.AddPolyline([[u, v, 0] for u, v in boundary_polylines_UV[0]])
rs.AddLayer('boundary_polyline_planar')
rs.ObjectLayer(boundary_polyline_guid, layer = 'boundary_polyline_planar')

hole_polyline_guids = [rs.AddPolyline([[u, v, 0] for u, v in hole]) for hole in hole_polylines_UV]
rs.AddLayer('hole_polyline_planar')
rs.ObjectLayer(hole_polyline_guids, layer = 'hole_polyline_planar')

feature_polyline_guids = [rs.AddPolyline([[u, v, 0] for u, v in feature]) for feature in polyline_features_UV]
rs.AddLayer('feature_polyline_planar')
rs.ObjectLayer(feature_polyline_guids, layer = 'feature_polyline_planar')

feature_point_guids = [rs.AddPoint([u, v, 0]) for u, v in point_features_UV]
rs.AddLayer('feature_point_planar')
rs.ObjectLayer(feature_point_guids, layer = 'feature_point_planar')

rs.EnableRedraw(True)


# generate specific Delaunay mesh from planar shape and features
rs.EnableRedraw(False)

boundary = rs.PolylineVertices(boundary_polyline_guid)

holes = []
for guid in hole_polyline_guids:
    holes.append(rs.PolylineVertices(guid))

polyline_features = []
for guid in feature_polyline_guids:
    polyline_features.append(rs.PolylineVertices(guid))

point_features = []
for guid in feature_point_guids:
    point_features.append(rs.PointCoordinates(guid))

delaunay_mesh = polylines_to_delaunay(boundary, holes = holes, polyline_features = polyline_features, point_features = point_features)

vertices = [delaunay_mesh.vertex_coordinates(vkey) for vkey in delaunay_mesh.vertices()]
face_vertices = [
delaunay_mesh.face_vertices(fkey) for fkey in delaunay_mesh.faces()]
delaunay_mesh_guid = rhino.utilities.drawing.xdraw_mesh(vertices, face_vertices, None, None)
rs.AddLayer('delaunay_mesh')
rs.ObjectLayer(delaunay_mesh_guid, layer = 'delaunay_mesh')

rs.EnableRedraw(True)

# patch polylines from Delaunay mesh
rs.EnableRedraw(False)

patch_decomposition = delaunay_to_patch_decomposition(delaunay_mesh)

rs.AddLayer('patch_decomposition')
rs.ObjectLayer(delaunay_mesh_guid, layer = 'delaunay_mesh')
for vertices in patch_decomposition:
    if len(vertices) == 1:
        rs.AddTextDot('!', vertices[0])
    guid = rs.AddPolyline(vertices)
    rs.ObjectLayer(guid, layer = 'patch_decomposition')

rs.EnableRedraw(True)
# conversion patch polylines to control mesh

#mesh = polylines_to_mesh(patch_decomposition)
#vertices = [mesh.vertex_coordinates(vkey) for vkey in mesh.vertices()]
#face_vertices = [mesh.face_vertices(fkey) for fkey in mesh.faces()]
#mesh_guid = rhino.utilities.drawing.xdraw_mesh(vertices, face_vertices, None, None)
#rs.AddLayer('control_mesh')
#rs.ObjectLayer(mesh_guid, layer = 'control_mesh')

# conforming operations into a quad control mesh

# possibility to apply grammar rules

# mesh densification

# mapping and smoothing on spatial shape

# conversion to pattern