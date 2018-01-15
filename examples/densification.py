import rhinoscriptsyntax as rs

from compas.datastructures.mesh import Mesh
import compas_rhino as rhino

from compas_pattern.algorithms.coarse_to_dense_mesh import quad_mesh_densification

conform_mesh = rs.GetObject('mesh to densify', filter = 32)
conform_mesh = rhino.mesh_from_guid(Mesh, conform_mesh)

target_length = rs.GetReal('target length for densification', number = 1)

rs.EnableRedraw(False)

dense_mesh = quad_mesh_densification(conform_mesh, target_length)

vertices = [dense_mesh.vertex_coordinates(vkey) for vkey in dense_mesh.vertices()]
face_vertices = [dense_mesh.face_vertices(fkey) for fkey in dense_mesh.faces()]
dense_mesh_guid = rhino.utilities.drawing.xdraw_mesh(vertices, face_vertices, None, None)
layer_name = 'dense_mesh'
rs.AddLayer(layer_name)
rs.ObjectLayer(dense_mesh_guid, layer = layer_name)

rs.EnableRedraw(True)