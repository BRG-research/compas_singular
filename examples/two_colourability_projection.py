import rhinoscriptsyntax as rs

from compas_pattern.datastructures.mesh_quad.mesh_quad import QuadMesh
from compas_pattern.datastructures.mesh_quad.coloring import quad_mesh_strip_n_coloring
from compas_pattern.datastructures.mesh_quad.coloring import quad_mesh_strip_2_coloring

from compas_rhino.geometry import RhinoMesh

from compas_pattern.algorithms.projection.projection import two_colourable_projection

from compas.geometry import bounding_box
from compas.geometry import distance_point_point

from compas_pattern.algorithms.combination.arrange import arrange_in_spiral
from compas_pattern.algorithms.combination.arrange import arrange_in_circle
from compas_pattern.cad.rhino.draw import draw_mesh
from compas_pattern.cad.rhino.draw import draw_graph

guid = rs.GetObject('get quad mesh')
mesh = QuadMesh.from_vertices_and_faces(*RhinoMesh.from_guid(guid).get_vertices_and_faces())
box = bounding_box([mesh.vertex_coordinates(vkey) for vkey in mesh.vertices()])
scale_x = distance_point_point(box[0], box[1]) * 1.1
scale_y = distance_point_point(box[0], box[3]) * 1.1

kmax = 3

group_to_colour = {0: [255,0,0], 1: [0,0,255], 2: [0,255,0]}

mesh.collect_strips()

rs.EnableRedraw(False)
key_to_group = quad_mesh_strip_n_coloring(mesh)
key_to_colour = {key: group_to_colour[group] for key, group in key_to_group.items()}
guids = []
for skey in mesh.strips():
    polyline = mesh.strip_edge_polyline(skey)
    guid = rs.AddPolyline(polyline)
    rs.ObjectColor(guid, key_to_colour[skey])
    rs.CurveArrows(guid, 3)
    guids.append(guid)
rs.EnableRedraw(True)

results = two_colourable_projection(mesh, kmax)

meshes = []
for combination, result in results.items():
    if type(result) == tuple:
        two_col_mesh, two_col_network, key_to_group = result
        meshes.append(two_col_mesh)

arrange_in_circle(meshes)

for mesh in meshes:
    rs.EnableRedraw(False)
    draw_mesh(mesh)
    rs.EnableRedraw(False)
    key_to_group = quad_mesh_strip_2_coloring(mesh)
    key_to_colour = {key: group_to_colour[group] for key, group in key_to_group.items()}
    print key_to_group
    guids = []
    for skey in mesh.strips():
        polyline = mesh.strip_edge_polyline(skey)
        guid = rs.AddPolyline(polyline)
        rs.ObjectColor(guid, key_to_colour[skey])
        rs.CurveArrows(guid, 3)
        guids.append(guid)

#i = 0
#for combination, result in results.items():
#    if type(result) == tuple:
#        i += 1
#        
#        two_col_mesh, two_col_network, key_to_group = result
#        rs.EnableRedraw(False)
#        guid = draw_mesh(two_col_mesh)
#        rs.MoveObject(guid, [i * scale_x, 0, 0])
#        
#        key_to_colour = {key: group_to_colour[group] for key, group in key_to_group.items()}
#        #print key_to_colour
#        #print list(two_col_mesh.strips())
#        guids = []
#        rs.EnableRedraw(False)
#        for skey in two_col_mesh.strips():
#            polyline = two_col_mesh.strip_edge_polyline(skey)
#            guid = rs.AddPolyline(polyline)
#            rs.ObjectColor(guid, key_to_colour[skey])
#            rs.CurveArrows(guid, 3)
#            guids.append(guid)
#        rs.MoveObjects(guids, [i * scale_x, 0, 0])
#        #group = draw_graph(two_col_network, key_to_colour)
#        #rs.MoveObjects(rs.ObjectsByGroup(group), [i * scale_x, - scale_y, 0])
#        rs.EnableRedraw(True)
#
#rs.EnableRedraw(True)