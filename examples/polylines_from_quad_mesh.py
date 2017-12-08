import rhinoscriptsyntax as rs

from compas.datastructures.mesh import Mesh
import compas_rhino as rhino

from compas_pattern.operations.polylines_from_quad_mesh import polylines_from_quad_mesh

guid = rs.GetObject('get mesh')
mesh = rhino.mesh_from_guid(Mesh, guid)

polyline = polylines_from_quad_mesh(mesh)

for pl in polyline:
    points = [mesh.vertex_coordinates(pt) for pt in pl]
    rs.AddPolyline(points)

print len(polyline), ' polylines added from mesh'