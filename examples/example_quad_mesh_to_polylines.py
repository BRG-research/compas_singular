import rhinoscriptsyntax as rs

from compas.datastructures.mesh import Mesh
import compas_rhino as rhino

from compas_pattern.topology.quad_mesh_to_polylines import quad_mesh_to_polylines

guid = rs.GetObject('get mesh')
mesh = rhino.mesh_from_guid(Mesh, guid)

rs.EnableRedraw(False)

polyline = quad_mesh_to_polylines(mesh, dual = False)

for pl in polyline:
    points = [mesh.vertex_coordinates(vkey) for vkey in pl]
    rs.AddPolyline(points)

print len(polyline), 'polylines added from mesh'

#dual_polyline = quad_mesh_to_polylines(mesh, dual = True)
#
#for pl in dual_polyline:
#    points = [mesh.face_centroid(fkey) for fkey in pl]
#    rs.AddPolyline(points)
#
#print len(polyline), ' dual polylines added from mesh'

rs.EnableRedraw(True)