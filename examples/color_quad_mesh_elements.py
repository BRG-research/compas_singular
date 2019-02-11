import rhinoscriptsyntax as rs
from compas_rhino.geometry import RhinoMesh
from compas_pattern.datastructures.mesh_quad import QuadMesh
from compas_pattern.topology.colorability import *
from compas_pattern.cad.rhino.utilities import draw_mesh

guids = rs.GetObjects('get quad meshes')

for guid in guids:
    mesh = QuadMesh.from_vertices_and_faces(*RhinoMesh.from_guid(guid).get_vertices_and_faces())
    
    colors = {0: [255, 0, 0], 1: [0, 0, 255], 2: [0, 255, 0], 3: [255, 255, 0], 4: [255, 0, 255], 5: [0, 255, 255], 6: [255, 255, 255]}
    
    dx = 0
    
#    rs.EnableRedraw(False)
#    # vertices
#    key_to_color = mesh_vertex_n_coloring(mesh)
#    for key, color in key_to_color.items():
#        guid = rs.AddPoint(mesh.vertex_coordinates(key))
#        rs.ObjectColor(guid, colors[color])
#        rs.MoveObject(guid, [dx, 0, 0])
#        guid = rs.AddCircle(mesh.vertex_coordinates(key), .1)
#        rs.ObjectColor(guid, colors[color])
#        rs.MoveObject(guid, [dx, 0, 0])
#    guid = draw_mesh(mesh)
#    rs.MoveObject(guid, [dx, 0, 0])
#    
#    rs.EnableRedraw(False)
#    # faces
#    key_to_color = mesh_face_n_coloring(mesh)
#    for key, color in key_to_color.items():
#        guid = rs.AddPolyline([mesh.vertex_coordinates(vkey) for vkey in mesh.face_vertices(key) + mesh.face_vertices(key)[:1]])
#        rs.ObjectColor(guid, colors[color])
#        rs.MoveObject(guid, [2 * dx, 0, 0])
    
    rs.EnableRedraw(False)
    # strips
    key_to_color = mesh_strip_n_coloring(mesh)
    for key, color in key_to_color.items():
        guid = rs.AddPolyline(mesh.strip_edge_polyline(key))
        rs.CurveArrows(guid, 3)
        rs.ObjectColor(guid, colors[color])
        rs.MoveObject(guid, [3 * dx, 0, 0])
#        for contour in mesh.strip_contour_polylines(key):
#            guid = rs.AddPolyline(contour)
#            rs.ObjectColor(guid, colors[color])
#            rs.MoveObject(guid, [4 * dx, 0, 0])
#    guid = draw_mesh(mesh)
    rs.MoveObject(guid, [3 * dx, 0, 0])
