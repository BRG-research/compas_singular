import rhinoscriptsyntax as rs

import compas_rhino as rhino

from compas.datastructures.mesh import Mesh

from compas_pattern.topology.grammar_rules import quad_mix_1
from compas_pattern.topology.grammar_rules import penta_quad_1
from compas_pattern.topology.grammar_rules import hexa_quad_1

# mesh selection
guid = rs.GetObject('get mesh')
mesh = rhino.mesh_from_guid(Mesh, guid)

# mesh element selection
artist = rhino.MeshArtist(mesh, layer='mesh_artist')
artist.clear_layer()

artist.draw_vertexlabels()
artist.redraw()
vkey = rhino.mesh_select_vertex(mesh, message = 'vkey')
ukey = rhino.mesh_select_vertex(mesh, message = 'ukey')
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

rs.DeleteLayer('mesh_artist')

e = quad_mix_1(mesh, fkey, vkey, ukey)

## conforming: propagate T-junctions
# propagate until boundary or closed loop
is_loop = False
wkey = e
count = mesh.number_of_faces()
while count > 0:
    count -= 1
    next_fkey = mesh.halfedge[vkey][wkey]
    ukey = mesh.face_vertex_descendant(next_fkey, wkey)
    if wkey in mesh.halfedge[ukey] and mesh.halfedge[ukey][wkey] is not None:
        next_fkey = mesh.halfedge[ukey][wkey]
        if len(mesh.face_vertices(next_fkey)) == 5:
            vkey = wkey
            wkey = penta_quad_1(mesh, next_fkey, wkey)
            # add to faces along feature to check
            continue
        if len(mesh.face_vertices(next_fkey)) == 6:
            vkey = wkey
            wkey = hexa_quad_1(mesh, next_fkey, wkey)
            #if wkey == e2:
            #    is_loop = True
            # add to faces along feature to check
            break
    break
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


# draw mesh
vertices = [mesh.vertex_coordinates(vkey) for vkey in mesh.vertices()]
face_vertices = [mesh.face_vertices(fkey) for fkey in mesh.faces()]
mesh_guid = rhino.utilities.drawing.xdraw_mesh(vertices, face_vertices, None, None)
rs.AddLayer('edited_mesh')
rs.ObjectLayer(mesh_guid, layer = 'edited_mesh')
