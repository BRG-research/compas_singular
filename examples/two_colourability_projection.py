import rhinoscriptsyntax as rs

from compas_pattern.datastructures.mesh_quad import QuadMesh

from compas_rhino.geometry import RhinoMesh

from compas_pattern.algorithms.two_colourable_projection import two_colourable_projection

from compas.geometry import bounding_box
from compas.geometry import distance_point_point

from compas_pattern.cad.rhino.utilities import draw_mesh
from compas_pattern.cad.rhino.utilities import draw_graph

guid = rs.GetObject('get quad mesh')
mesh = QuadMesh.from_vertices_and_faces(*RhinoMesh.from_guid(guid).get_vertices_and_faces())
box = bounding_box([mesh.vertex_coordinates(vkey) for vkey in mesh.vertices()])
scale_x = distance_point_point(box[0], box[1]) * 1.1
scale_y = distance_point_point(box[0], box[3]) * 1.1

kmax = 3

mesh.collect_strips()
results = two_colourable_projection(mesh, kmax)

group_to_colour = {0: [255,0,0], 1: [0,0,255], 2: [0,255,0]}
rs.EnableRedraw(False)

i = 0
for combination, result in results.items():
    if type(result) == tuple:
        i += 1
        print result
        two_col_mesh, two_col_network, key_to_group = result
        
        guid = draw_mesh(two_col_mesh)
        rs.MoveObject(guid, [i * scale_x, 0, 0])
        
        key_to_colour = {key: group_to_colour[group] for key, group in key_to_group.items()}
        group = draw_graph(two_col_network, key_to_colour)
        rs.MoveObjects(rs.ObjectsByGroup(group), [i * scale_x, - scale_y, 0])

rs.EnableRedraw(True)