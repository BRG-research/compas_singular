import rhinoscriptsyntax as rs

import compas_rhino as rhino

from compas.datastructures.mesh import Mesh

#from compas_pattern.topology.face_strip_operations import face_strip_collapse
#from compas_pattern.topology.face_strip_operations import face_strip_subdivide

from compas_pattern.topology.grammar_primitive import primitive_1
from compas_pattern.topology.grammar_primitive import primitive_2
from compas_pattern.topology.grammar_primitive import primitive_3
from compas_pattern.topology.grammar_primitive import primitive_4
from compas_pattern.topology.grammar_primitive import primitive_5

from compas_pattern.topology.grammar_extended import extended_21

# mesh selection
guid = rs.GetObject('get mesh')
mesh = rhino.mesh_from_guid(Mesh, guid)

rule = rs.GetInteger('rule #?')

if rule == 1:
    artist = rhino.MeshArtist(mesh, layer='mesh_artist')
    artist.clear_layer()
    
    artist.draw_facelabels()
    artist.redraw()
    fkey = rhino.mesh_select_face(mesh, message = 'fkey')
    artist.clear_layer()
    artist.redraw()
    
    artist.draw_vertices()
    artist.draw_vertexlabels()
    artist.redraw()
    b = rhino.mesh_select_vertex(mesh, message = 'b')
    d = rhino.mesh_select_vertex(mesh, message = 'd')
    artist.clear_layer()
    artist.redraw()
    
    rs.DeleteLayer('mesh_artist')
    
    primitive_1(mesh, fkey, b, d)

if rule == 2:
    artist = rhino.MeshArtist(mesh, layer='mesh_artist')
    artist.clear_layer()
    
    artist.draw_facelabels()
    artist.redraw()
    fkey = rhino.mesh_select_face(mesh, message = 'fkey')
    artist.clear_layer()
    artist.redraw()
    
    artist.draw_vertices()
    artist.draw_vertexlabels()
    artist.redraw()
    a = rhino.mesh_select_vertex(mesh, message = 'a')
    artist.clear_layer()
    artist.redraw()
    
    rs.DeleteLayer('mesh_artist')
    
    primitive_2(mesh, fkey, a)

if rule == 3:
    artist = rhino.MeshArtist(mesh, layer='mesh_artist')
    artist.clear_layer()
    
    artist.draw_vertices()
    artist.draw_vertexlabels()
    artist.redraw()
    a = rhino.mesh_select_vertex(mesh, message = 'a')
    c = rhino.mesh_select_vertex(mesh, message = 'c')
    artist.clear_layer()
    artist.redraw()
    
    rs.DeleteLayer('mesh_artist')
    
    primitive_3(mesh, a, c)

if rule == 4:
    artist = rhino.MeshArtist(mesh, layer='mesh_artist')
    artist.clear_layer()
    
    artist.draw_facelabels()
    artist.redraw()
    fkey = rhino.mesh_select_face(mesh, message = 'fkey')
    artist.clear_layer()
    artist.redraw()
    
    artist.draw_vertices()
    artist.draw_vertexlabels()
    artist.redraw()
    b = rhino.mesh_select_vertex(mesh, message = 'b')
    artist.clear_layer()
    artist.redraw()
    
    rs.DeleteLayer('mesh_artist')
    
    primitive_4(mesh, fkey, b)

if rule == 5:
    artist = rhino.MeshArtist(mesh, layer='mesh_artist')
    artist.clear_layer()
    
    artist.draw_vertices()
    artist.draw_vertexlabels()
    artist.redraw()
    e = rhino.mesh_select_vertex(mesh, message = 'e')
    c = rhino.mesh_select_vertex(mesh, message = 'c')
    artist.clear_layer()
    artist.redraw()
    
    rs.DeleteLayer('mesh_artist')
    
    primitive_5(mesh, e, c)

if rule == 21:
    artist = rhino.MeshArtist(mesh, layer='mesh_artist')
    artist.clear_layer()
    
    artist.draw_facelabels()
    artist.redraw()
    fkey = rhino.mesh_select_face(mesh, message = 'fkey')
    artist.clear_layer()
    artist.redraw()
    
    artist.draw_vertices()
    artist.draw_vertexlabels()
    artist.redraw()
    a = rhino.mesh_select_vertex(mesh, message = 'a')
    artist.clear_layer()
    artist.redraw()
    
    rs.DeleteLayer('mesh_artist')
    
    extended_21(mesh, fkey, a)

#mesh = face_strip_collapse(Mesh, mesh, ukey, vkey)

#mesh = face_strip_subdivide(Mesh, mesh, ukey, vkey)

#e = quad_mix_1(mesh, fkey, vkey, ukey)
#
### conforming: propagate T-junctions
## propagate until boundary or closed loop
#is_loop = False
#wkey = e
#count = mesh.number_of_faces()
#while count > 0:
#    count -= 1
#    next_fkey = mesh.halfedge[vkey][wkey]
#    ukey = mesh.face_vertex_descendant(next_fkey, wkey)
#    if wkey in mesh.halfedge[ukey] and mesh.halfedge[ukey][wkey] is not None:
#        next_fkey = mesh.halfedge[ukey][wkey]
#        if len(mesh.face_vertices(next_fkey)) == 5:
#            vkey = wkey
#            wkey = penta_quad_1(mesh, next_fkey, wkey)
#            # add to faces along feature to check
#            continue
#        if len(mesh.face_vertices(next_fkey)) == 6:
#            vkey = wkey
#            wkey = hexa_quad_1(mesh, next_fkey, wkey)
#            #if wkey == e2:
#            #    is_loop = True
#            # add to faces along feature to check
#            break
#    break
# # if not loop, propaget in other direction
# if not is_loop:
#     vkey = v
#     wkey = e2
#     count = mesh.number_of_faces()
#     while count > 0:
#         count -= 1
#         next_fkey = mesh.halfedge[vkey][wkey]
#         ukey = mesh.face_vertex_descendant(next_fkey, wkey)
#         if wkey in mesh.halfedge[ukey] and mesh.halfedge[ukey][wkey] is not None:
#             next_fkey = mesh.halfedge[ukey][wkey]
#             if len(mesh.face_vertices(next_fkey)) == 5:
#                 vkey = wkey
#                 wkey = penta_quad_1(mesh, next_fkey, wkey)
#                 # add to faces along feature to check
#                 continue
#             if len(mesh.face_vertices(next_fkey)) == 6:
#                 vkey = wkey
#                 wkey = hexa_quad_1(mesh, next_fkey, wkey)
#                 if wkey == e2:
#                     is_loop = True
#                 # add to faces along feature to check
#                 break
#         break

#print mesh
#for u, v in mesh.edges():
#    u_xyz = mesh.vertex_coordinates(u)
#    v_xyz = mesh.vertex_coordinates(v)
#    if u_xyz == v_xyz:
#        print u_xyz, v_xyz
#    rs.AddLine(u_xyz, v_xyz)
# draw mesh
vertices = [mesh.vertex_coordinates(vkey) for vkey in mesh.vertices()]
face_vertices = [mesh.face_vertices(fkey) for fkey in mesh.faces()]
mesh_guid = rhino.utilities.drawing.xdraw_mesh(vertices, face_vertices, None, None)
rhino.helpers.mesh_draw(mesh, show_faces = False)
#rs.AddLayer('edited_mesh')
#rs.ObjectLayer(mesh_guid, layer = 'edited_mesh')
