import rhinoscriptsyntax as rs

import compas_rhino as rhino

from compas.datastructures.mesh import Mesh

from compas_pattern.topology.conforming_operations import penta_to_quads
from compas_pattern.topology.conforming_operations import hexa_to_quads
from compas_pattern.topology.conforming_operations import tri_to_quads
from compas_pattern.topology.grammar_rules import quad_to_tris
from compas_pattern.topology.grammar_rules import quad_to_three_tris

# mesh selection
guid = rs.GetObject('get mesh')
mesh = rhino.mesh_from_guid(Mesh, guid)

# mesh element selection
artist = rhino.MeshArtist(mesh, layer='mesh_artist')
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

rs.DeleteLayer('mesh_artist')

g = quad_to_three_tris(mesh, fkey, vkey)

# conforming: propagate T-junctions
vertices = mesh.vertex_neighbours(g)

vertices.remove(vkey)
e, f = vertices
fkey = mesh.halfedge[g][e]
vkey = e
count = mesh.number_of_faces()
while count > 0:
    count -= 1
    ukey = mesh.face_vertex_descendant(fkey, vkey)
    if vkey in mesh.halfedge[ukey] and mesh.halfedge[ukey][vkey] is not None:
        fkey = mesh.halfedge[ukey][vkey]
        if len(mesh.face_vertices(fkey)) == 5:
            wkey = penta_to_quads(mesh, fkey, vkey)
            fkey = mesh.halfedge[vkey][wkey]
            vkey = wkey
            continue
        if len(mesh.face_vertices(fkey)) == 6:
            hexa_to_quads(mesh, fkey, vkey)
            break
    break
fkey = mesh.halfedge[g][f]
vkey = f
count = mesh.number_of_faces()
while count > 0:
    count -= 1
    ukey = mesh.face_vertex_descendant(fkey, vkey)
    if vkey in mesh.halfedge[ukey] and mesh.halfedge[ukey][vkey] is not None and len(mesh.face_vertices(mesh.halfedge[ukey][vkey])) != 4:
        fkey = mesh.halfedge[ukey][vkey]
        if len(mesh.face_vertices(fkey)) == 5:
            wkey = penta_to_quads(mesh, fkey, vkey)
            fkey = mesh.halfedge[vkey][wkey]
            vkey = wkey
            continue
        if len(mesh.face_vertices(fkey)) == 6:
            hexa_to_quads(mesh, fkey, vkey)
            break
    break

# draw mesh
vertices = [mesh.vertex_coordinates(vkey) for vkey in mesh.vertices()]
face_vertices = [mesh.face_vertices(fkey) for fkey in mesh.faces()]
mesh_guid = rhino.utilities.drawing.xdraw_mesh(vertices, face_vertices, None, None)
rs.AddLayer('edited_mesh')
rs.ObjectLayer(mesh_guid, layer = 'edited_mesh')