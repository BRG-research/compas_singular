import rhinoscriptsyntax as rs

import compas_rhino as rhino

from compas.datastructures.mesh import Mesh

from compas.utilities import geometric_key

from compas_pattern.cad.rhino.surface_input_to_planar_polylines import surface_input_to_planar_polylines
from compas_pattern.algorithms.polylines_to_delaunay import polylines_to_delaunay
from compas_pattern.topology.unweld_mesh_along_edge_path import unweld_mesh_along_edge_path
from compas_pattern.algorithms.delaunay_to_qpd import delaunay_to_patch_decomposition
from compas_pattern.topology.polylines_to_mesh import polylines_to_mesh
from compas_pattern.topology.polylines_to_mesh import polylines_to_mesh_old
from compas_pattern.algorithms.conforming_algorithm import conforming_initial_patch_decomposition

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


# generate specific Delaunay mesh from planar shape and features

boundary = rs.PolylineVertices(boundary_polyline_guid)

holes = [rs.PolylineVertices(guid) for guid in hole_polyline_guids]

polyline_features = [rs.PolylineVertices(guid) for guid in feature_polyline_guids]

point_features = [rs.PointCoordinates(guid) for guid in feature_point_guids]

delaunay_mesh = polylines_to_delaunay(boundary, holes = holes, polyline_features = polyline_features, point_features = point_features)

vertices = [delaunay_mesh.vertex_coordinates(vkey) for vkey in delaunay_mesh.vertices()]
face_vertices = [
delaunay_mesh.face_vertices(fkey) for fkey in delaunay_mesh.faces()]
delaunay_mesh_guid = rhino.utilities.drawing.xdraw_mesh(vertices, face_vertices, None, None)
rs.AddLayer('delaunay_mesh')
rs.ObjectLayer(delaunay_mesh_guid, layer = 'delaunay_mesh')

# patch polylines from Delaunay mesh


medial_branches, boundary_polylines = delaunay_to_patch_decomposition(delaunay_mesh)
patch_decomposition = medial_branches + boundary_polylines

rs.AddLayer('patch_decomposition')
rs.ObjectLayer(delaunay_mesh_guid, layer = 'delaunay_mesh')
for vertices in patch_decomposition:
    guid = rs.AddPolyline(vertices)
    rs.ObjectLayer(guid, layer = 'patch_decomposition')

# conversion patch polylines to control mesh

mesh = polylines_to_mesh_old(boundary_polylines, medial_branches)

vertices = [mesh.vertex_coordinates(vkey) for vkey in mesh.vertices()]
face_vertices = [mesh.face_vertices(fkey) for fkey in mesh.faces()]
mesh_guid = rhino.utilities.drawing.xdraw_mesh(vertices, face_vertices, None, None)
rs.AddLayer('control_mesh')
rs.ObjectLayer(mesh_guid, layer = 'control_mesh')

# conforming operations into a quad control mesh

conform_mesh = conforming_initial_patch_decomposition(mesh)

vertices = [conform_mesh.vertex_coordinates(vkey) for vkey in conform_mesh.vertices()]
face_vertices = [conform_mesh.face_vertices(fkey) for fkey in conform_mesh.faces()]
conform_mesh_guid = rhino.utilities.drawing.xdraw_mesh(vertices, face_vertices, None, None)
rs.AddLayer('conform_mesh')
rs.ObjectLayer(conform_mesh_guid, layer = 'conform_mesh')

# possibility to apply grammar rules

mesh = conform_mesh

from compas_pattern.topology.grammar_rules import quad_to_two_quads_diagonal
#for vkey in mesh.vertices_on_boundary():
#    vertex_faces = mesh.vertex_faces(vkey)
#    if len(vertex_faces) == 1:
#        fkey = vertex_faces[0]
#        quad_to_two_quads_diagonal(mesh, fkey, vkey)

from compas_pattern.topology.grammar_rules import quad_to_two_quads
fkey = mesh.faces_on_boundary()[0]
ukey = mesh.face_vertices(fkey)[0]
vkey = mesh.face_vertices(fkey)[1]
quad_to_two_quads(mesh, fkey, ukey, vkey)

vertices = [mesh.vertex_coordinates(vkey) for vkey in mesh.vertices()]
face_vertices = [mesh.face_vertices(fkey) for fkey in mesh.faces()]
mesh_guid = rhino.utilities.drawing.xdraw_mesh(vertices, face_vertices, None, None)
rs.AddLayer('edited_mesh')
rs.ObjectLayer(mesh_guid, layer = 'edited_mesh')


rs.EnableRedraw(True)

# mesh densification

# mapping and smoothing on spatial shape

# conversion to pattern