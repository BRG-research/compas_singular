import rhinoscriptsyntax as rs

import compas_rhino as rhino

from compas.datastructures.mesh import Mesh
from compas.datastructures.network import Network
from compas_pattern.datastructures.pseudo_quad_mesh import PseudoQuadMesh

from compas_pattern.topology.face_strip_operations import face_strip_collapse

from compas_pattern.algorithms.make_two_colourable import generate_crossing_graph_from_patch_decomposition
from compas_pattern.algorithms.make_two_colourable import is_graph_two_colourable

# mesh selection
guid = rs.GetObject('get quad patch decomposition')
mesh = rhino.mesh_from_guid(Mesh, guid)


crossing_graph = generate_crossing_graph_from_patch_decomposition(mesh)

is_two_colourable = is_graph_two_colourable(crossing_graph)
print 'is two-colourable ?', is_two_colourable

#for u, v in crossing_graph.edges():
#    u_xyz = crossing_graph.vertex_coordinates(u)
#    v_xyz = crossing_graph.vertex_coordinates(v)
#    rs.AddLine(u_xyz, v_xyz)

print crossing_graph
rhino.network_draw(crossing_graph)

#mesh = face_strip_collapse(Mesh, mesh, ukey, vkey)



## draw mesh
#vertices = [mesh.vertex_coordinates(vkey) for vkey in mesh.vertices()]
#face_vertices = [mesh.face_vertices(fkey) for fkey in mesh.faces()]
#mesh_guid = rhino.utilities.drawing.xdraw_mesh(vertices, face_vertices, None, None)
##rs.AddLayer('edited_mesh')
##rs.ObjectLayer(mesh_guid, layer = 'edited_mesh')
