import rhinoscriptsyntax as rs

import compas_rhino as rhino

from compas.datastructures.mesh import Mesh

from compas_pattern.cad.rhino.utilities import draw_mesh
from compas_pattern.datastructures.pseudo_quad_mesh import PseudoQuadMesh

#from compas_pattern.topology.face_strip_operations import face_strip_collapse
#from compas_pattern.topology.face_strip_operations import face_strip_subdivide
#from compas_pattern.topology.face_strip_operations import face_strips_merge

#from compas_pattern.topology.grammar_primitive import primitive_1
#from compas_pattern.topology.grammar_primitive import primitive_2
#from compas_pattern.topology.grammar_primitive import primitive_3
#from compas_pattern.topology.grammar_primitive import primitive_4
#from compas_pattern.topology.grammar_primitive import primitive_5

#from compas_pattern.topology.grammar_extended import extended_21 #6
#from compas_pattern.topology.grammar_extended import extended_21443 #7
#from compas_pattern.topology.grammar_extended import extended_212144321443 #8
#from compas_pattern.topology.grammar_extended import extended_22122333 #9

from compas_pattern.topology.grammar import face_pole
from compas_pattern.topology.grammar import edge_pole
from compas_pattern.topology.grammar import vertex_pole
from compas_pattern.topology.grammar import face_opening
from compas_pattern.topology.grammar import flat_corner_2
from compas_pattern.topology.grammar import flat_corner_3
from compas_pattern.topology.grammar import flat_corner_33
from compas_pattern.topology.grammar import split_35
from compas_pattern.topology.grammar import split_26
from compas_pattern.topology.grammar import simple_split
from compas_pattern.topology.grammar import double_split
from compas_pattern.topology.grammar import insert_pole
from compas_pattern.topology.grammar import insert_partial_pole

from compas_pattern.topology.global_propagation import mesh_propagation

# mesh selection
guid = rs.GetObject('get mesh')
layer = rs.ObjectLayer(guid)
mesh = rhino.mesh_from_guid(PseudoQuadMesh, guid)

rules = ['face_pole', 'edge_pole', 'vertex_pole', 'face_opening', 'flat_corner_2', 'flat_corner_3', 'flat_corner_33', 'split_35', 'split_26', 'simple_split', 'double_split', 'insert_pole', 'insert_partial_pole']
rule = rs.GetString('rule?', strings = rules)

original_vertices = list(mesh.vertices())

if rule == 'face_pole':
    artist = rhino.MeshArtist(mesh, layer='mesh_artist')
    artist.clear_layer()
    
    artist.draw_facelabels()
    artist.redraw()
    fkey = rhino.mesh_select_face(mesh, message = 'fkey')
    artist.clear_layer()
    artist.redraw()
    
    rs.DeleteLayer('mesh_artist')
    
    face_pole(mesh, fkey)

if rule == 'edge_pole':
    artist = rhino.MeshArtist(mesh, layer='mesh_artist')
    artist.clear_layer()
    
    artist.draw_facelabels()
    artist.redraw()
    fkey = rhino.mesh_select_face(mesh, message = 'fkey')
    artist.clear_layer()
    artist.redraw()
    
    artist.draw_edgelabels(text = {(u, v): "{}-{}".format(u, v) for u, v in mesh.face_halfedges(fkey)})
    artist.redraw()
    edge = rhino.mesh_select_edge(mesh, message = 'edge')
    artist.clear_layer()
    artist.redraw()
    
    rs.DeleteLayer('mesh_artist')
    
    edge_pole(mesh, fkey, edge)

if rule == 'vertex_pole':
    artist = rhino.MeshArtist(mesh, layer='mesh_artist')
    artist.clear_layer()
    
    artist.draw_facelabels()
    artist.redraw()
    fkey = rhino.mesh_select_face(mesh, message = 'fkey')
    artist.clear_layer()
    artist.redraw()
    
    artist.draw_vertexlabels(text = {key: str(key) for key in mesh.face_vertices(fkey)})
    artist.redraw()
    pole = rhino.mesh_select_vertex(mesh, message = 'pole')
    artist.clear_layer()
    artist.redraw()
    
    rs.DeleteLayer('mesh_artist')
    
    vertex_pole(mesh, fkey, pole)

if rule == 'face_opening':
    artist = rhino.MeshArtist(mesh, layer='mesh_artist')
    artist.clear_layer()
    
    artist.draw_facelabels()
    artist.redraw()
    fkey = rhino.mesh_select_face(mesh, message = 'fkey')
    artist.clear_layer()
    artist.redraw()
    
    rs.DeleteLayer('mesh_artist')
    
    face_opening(mesh, fkey)

if rule == 'flat_corner_2':
    artist = rhino.MeshArtist(mesh, layer='mesh_artist')
    artist.clear_layer()
    
    artist.draw_facelabels()
    artist.redraw()
    fkey = rhino.mesh_select_face(mesh, message = 'fkey')
    artist.clear_layer()
    artist.redraw()
    
    artist.draw_vertexlabels(text = {key: str(key) for key in mesh.face_vertices(fkey)})
    artist.redraw()
    corner = rhino.mesh_select_vertex(mesh, message = 'corner')
    artist.clear_layer()
    artist.redraw()
    
    rs.DeleteLayer('mesh_artist')
    
    flat_corner_2(mesh, fkey, corner)

if rule == 'flat_corner_3':
    artist = rhino.MeshArtist(mesh, layer='mesh_artist')
    artist.clear_layer()
    
    artist.draw_facelabels()
    artist.redraw()
    fkey = rhino.mesh_select_face(mesh, message = 'fkey')
    artist.clear_layer()
    artist.redraw()
    
    artist.draw_vertexlabels(text = {key: str(key) for key in mesh.face_vertices(fkey)})
    artist.redraw()
    corner = rhino.mesh_select_vertex(mesh, message = 'corner')
    artist.clear_layer()
    artist.redraw()
    
    rs.DeleteLayer('mesh_artist')
    
    flat_corner_3(mesh, fkey, corner)

if rule == 'flat_corner_33':
    artist = rhino.MeshArtist(mesh, layer='mesh_artist')
    artist.clear_layer()
    
    artist.draw_facelabels()
    artist.redraw()
    fkey = rhino.mesh_select_face(mesh, message = 'fkey')
    artist.clear_layer()
    artist.redraw()
    
    artist.draw_vertexlabels(text = {key: str(key) for key in mesh.face_vertices(fkey)})
    artist.redraw()
    corner = rhino.mesh_select_vertex(mesh, message = 'corner')
    artist.clear_layer()
    artist.redraw()
    
    rs.DeleteLayer('mesh_artist')
    
    flat_corner_33(mesh, fkey, corner)

if rule == 'split_35':
    artist = rhino.MeshArtist(mesh, layer='mesh_artist')
    artist.clear_layer()
    
    artist.draw_facelabels()
    artist.redraw()
    fkey = rhino.mesh_select_face(mesh, message = 'fkey')
    artist.clear_layer()
    artist.redraw()
    
    artist.draw_edgelabels(text = {(u, v): "{}-{}".format(u, v) for u, v in mesh.face_halfedges(fkey)})
    artist.redraw()
    edge = rhino.mesh_select_edge(mesh, message = 'edge')
    artist.clear_layer()
    artist.redraw()
    
    rs.DeleteLayer('mesh_artist')
    
    split_35(mesh, fkey, edge)

if rule == 'split_26':
    artist = rhino.MeshArtist(mesh, layer='mesh_artist')
    artist.clear_layer()
    
    artist.draw_facelabels()
    artist.redraw()
    fkey = rhino.mesh_select_face(mesh, message = 'fkey')
    artist.clear_layer()
    artist.redraw()
    
    artist.draw_edgelabels(text = {(u, v): "{}-{}".format(u, v) for u, v in mesh.face_halfedges(fkey)})
    artist.redraw()
    edge = rhino.mesh_select_edge(mesh, message = 'edge')
    artist.clear_layer()
    artist.redraw()
    
    rs.DeleteLayer('mesh_artist')
    
    split_26(mesh, fkey, edge)

if rule == 'simple_split':
    artist = rhino.MeshArtist(mesh, layer='mesh_artist')
    artist.clear_layer()
    
    artist.draw_facelabels()
    artist.redraw()
    fkey = rhino.mesh_select_face(mesh, message = 'fkey')
    artist.clear_layer()
    artist.redraw()
    
    artist.draw_edgelabels(text = {(u, v): "{}-{}".format(u, v) for u, v in mesh.face_halfedges(fkey)})
    artist.redraw()
    edge = rhino.mesh_select_edge(mesh, message = 'edge')
    artist.clear_layer()
    artist.redraw()
    
    rs.DeleteLayer('mesh_artist')
    
    simple_split(mesh, fkey, edge)

if rule == 'double_split':
    artist = rhino.MeshArtist(mesh, layer='mesh_artist')
    artist.clear_layer()
    
    artist.draw_facelabels()
    artist.redraw()
    fkey = rhino.mesh_select_face(mesh, message = 'fkey')
    artist.clear_layer()
    artist.redraw()
    
    rs.DeleteLayer('mesh_artist')
    
    double_split(mesh, fkey)

if rule == 'insert_pole':
    artist = rhino.MeshArtist(mesh, layer='mesh_artist')
    artist.clear_layer()
    
    artist.draw_facelabels()
    artist.redraw()
    fkey = rhino.mesh_select_face(mesh, message = 'fkey')
    artist.clear_layer()
    artist.redraw()
    
    artist.draw_vertexlabels(text = {key: str(key) for key in mesh.face_vertices(fkey)})
    artist.redraw()
    pole = rhino.mesh_select_vertex(mesh, message = 'pole')
    artist.clear_layer()
    artist.redraw()
    
    rs.DeleteLayer('mesh_artist')
    
    insert_pole(mesh, fkey, pole)

if rule == 'insert_partial_pole':
    artist = rhino.MeshArtist(mesh, layer='mesh_artist')
    artist.clear_layer()
    
    artist.draw_facelabels()
    artist.redraw()
    fkey = rhino.mesh_select_face(mesh, message = 'fkey')
    artist.clear_layer()
    artist.redraw()
    
    artist.draw_vertexlabels(text = {key: str(key) for key in mesh.face_vertices(fkey)})
    artist.redraw()
    pole = rhino.mesh_select_vertex(mesh, message = 'pole')
    artist.clear_layer()
    artist.redraw()
    
    artist.draw_edgelabels({(u, v): "{}-{}".format(u, v) for u, v in mesh.face_halfedges(fkey) if u != pole and v!= pole})
    artist.redraw()
    edge = rhino.mesh_select_edge(mesh, message = 'edge')
    artist.clear_layer()
    artist.redraw()
    
    rs.DeleteLayer('mesh_artist')
    
    insert_partial_pole(mesh, fkey, pole, edge)

mesh = mesh.to_mesh()

mesh_propagation(mesh, original_vertices)

# replace mesh
mesh_guid = draw_mesh(mesh)
rs.ObjectLayer(mesh_guid, layer = layer)
rs.DeleteObject(guid)

#layer = 'edited_mesh'
#rs.AddLayer('layer')
#rs.ObjectLayer(mesh_guid, layer = layer)
