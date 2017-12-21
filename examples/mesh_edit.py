import rhinoscriptsyntax as rs

import compas_rhino as rhino

from compas.datastructures.mesh import Mesh

guid = rs.GetObject('get mesh')
mesh = rhino.mesh_from_guid(Mesh, guid)

from compas_pattern.topology.conforming_operations import tri_to_quads
from compas_pattern.topology.grammar_rules import quad_to_tris

artist = rhino.MeshArtist(mesh, layer='MeshArtist')
artist.clear_layer()

artist.draw_vertexlabels()
artist.redraw()
vkey = rhino.mesh_select_vertex(mesh, message = 'vkey')
artist.clear_layer()
artist.redraw()

artist.draw_facelabels()
artist.redraw()
fkey = rhino.mesh_select_face(mesh, message = 'fkey')
artist.clear_layer()
artist.redraw()

#artist.draw_edgelabels()
#artist.redraw()
#ukey, vkey = rhino.mesh_select_edge(mesh, message = 'edge of the face along which to split')
#artist.clear_layer()
#artist.redraw()

quad_to_tris(mesh, fkey, vkey)

vertices = [mesh.vertex_coordinates(vkey) for vkey in mesh.vertices()]
face_vertices = [mesh.face_vertices(fkey) for fkey in mesh.faces()]
mesh_guid = rhino.utilities.drawing.xdraw_mesh(vertices, face_vertices, None, None)
rs.AddLayer('edited_mesh')
rs.ObjectLayer(mesh_guid, layer = 'edited_mesh')