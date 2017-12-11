import rhinoscriptsyntax as rs

from compas.datastructures.mesh import Mesh
import compas_rhino as rhino

from compas.utilities import geometric_key

from compas_pattern.topology.unweld_mesh_along_edge_path import unweld_mesh_along_edge_path

guid = rs.GetObject('get mesh')
mesh = rhino.mesh_from_guid(Mesh, guid)
# if there are several edge paths for unwelding that come at the same point (e.g. T-junction),
# they must be split at this point
polylines = rs.GetObjects('polylines for unwelding')
rs.EnableRedraw(False)

vertex_map = {geometric_key(mesh.vertex_coordinates(vkey)): vkey for vkey in mesh.vertices()}

edge_paths = []
for polyline in polylines:
    edge_path = []
    poly_vertices = rs.PolylineVertices(polyline)
    vertex_path = [vertex_map[geometric_key(vertex)] for vertex in poly_vertices]
    for i in range(len(vertex_path) - 1):
        if vertex_path[i + 1] in mesh.halfedge[vertex_path[i]]:
            edge_path.append([vertex_path[i], vertex_path[i + 1]])
    edge_paths.append(edge_path)

for edge_path in edge_paths:
    unweld_mesh_along_edge_path(mesh, edge_path)

vertices = [mesh.vertex_coordinates(vkey) for vkey in mesh.vertices()]
face_vertices = [mesh.face_vertices(fkey) for fkey in mesh.faces()]

rhino.utilities.drawing.xdraw_mesh(vertices, face_vertices, None, None)

rs.EnableRedraw(True)