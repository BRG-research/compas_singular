import rhinoscriptsyntax as rs

from compas.datastructures.mesh import Mesh
import compas_rhino as rhino

from compas.utilities import geometric_key

from compas_pattern.operations.unweld_mesh_along_edge_path import unweld_mesh_along_edge_path

guid = rs.GetObject('get mesh')
mesh = rhino.mesh_from_guid(Mesh, guid)
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
    print vertex_path
    print edge_path


for edge_path in edge_paths:
    unweld_mesh_along_edge_path(mesh, edge_path)

rhino.draw_mesh(mesh, show_faces = True, show_vertices = False, show_edges = False)

rs.EnableRedraw(True)