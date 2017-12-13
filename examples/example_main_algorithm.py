import rhinoscriptsyntax as rs

import compas_rhino as rhino

from compas.datastructures.mesh import Mesh

from compas.utilities import geometric_key

from compas_pattern.algorithms.polylines_to_delaunay import polylines_to_delaunay
from compas_pattern.topology.unweld_mesh_along_edge_path import unweld_mesh_along_edge_path
from compas_pattern.algorithms.delaunay_to_qpd import delaunay_to_patch_decomposition

# collect spatial shape: surface/mesh + features

# parameterisation from spatial to planar

# generate specific Delaunay mesh from planar shape and features
guid = rs.GetObject('boundary')
boundary = rs.PolylineVertices(guid)

guids = rs.GetObjects('holes')
if guids is None:
    guids = []
holes = []
for guid in guids:
    holes.append(rs.PolylineVertices(guid))

guids = rs.GetObjects('polyline features')
if guids is None:
    guids = []
polyline_features = []
for guid in guids:
    polyline_features.append(rs.PolylineVertices(guid))

guids = rs.GetObjects('point features')
if guids is None:
    guids = []
point_features = []
for guid in guids:
    point_features.append(rs.PointCoordinates(guid))

rs.EnableRedraw(False)

delaunay_mesh = polylines_to_delaunay(boundary, holes = holes, polyline_features = polyline_features, point_features = point_features)

vertices = [delaunay_mesh.vertex_coordinates(vkey) for vkey in delaunay_mesh.vertices()]
face_vertices = [
delaunay_mesh.face_vertices(fkey) for fkey in delaunay_mesh.faces()]
delaunay_mesh_guid = rhino.utilities.drawing.xdraw_mesh(vertices, face_vertices, None, None)
rs.AddLayer('delaunay_mesh')
rs.ObjectLayer(delaunay_mesh_guid, layer = 'delaunay_mesh')

# patch polylines from Delaunay mesh
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

# conforming operations into a quad control mesh

# possibility to apply grammar rules

# mesh densification

# mapping and smoothing on spatial shape

# conversion to pattern