import rhinoscriptsyntax as rs

from compas.datastructures.mesh import Mesh
import compas_rhino as rhino

from compas_pattern.topology.mesh_from_polylines import mesh_from_polylines


guids = rs.GetObjects('get polylines')

polylines = []
for guid in guids:
    polylines.append([pt[0] for pt in rs.PolylineVertices(guid)])
rs.EnableRedraw(False)

mesh = mesh_from_polylines(polylines)
print mesh
vertices = [mesh.vertex_coordinates(vkey) for vkey in mesh.vertices()]
face_vertices = [mesh.face_vertices(fkey) for fkey in mesh.faces()]

rhino.utilities.drawing.xdraw_mesh(vertices, face_vertices, None, None)

rs.EnableRedraw(True)