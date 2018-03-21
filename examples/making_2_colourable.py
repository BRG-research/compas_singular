import rhinoscriptsyntax as rs

import compas_rhino as rhino

from compas.datastructures.mesh import Mesh
from compas.datastructures.network import Network
from compas_pattern.datastructures.pseudo_quad_mesh import PseudoQuadMesh

from compas_pattern.algorithms.colouring import generate_crossing_graph
from compas_pattern.algorithms.colouring import is_two_colourable
from compas_pattern.algorithms.colouring import compute_two_colourable_meshes

from compas_pattern.cad.rhino.utilities import draw_mesh

# mesh selection
guid = rs.GetObject('coarse quad mesh to make two-colourable')
mesh = rhino.mesh_from_guid(Mesh, guid)

delta_x = 30
delta_y = -20

rs.EnableRedraw(False)

crossing_graph, edge_groups, groups = generate_crossing_graph(mesh)
is_two_colourable(crossing_graph)

colours = [[255, 0, 0], [0, 0, 255], [0, 255, 0], [255, 255, 0], [255, 0, 255], [0, 255, 255]]

graph_objects = [rs.AddLine(crossing_graph.vertex_coordinates(ukey), crossing_graph.vertex_coordinates(vkey)) for ukey, vkey in crossing_graph.edges()]
for vkey in crossing_graph.vertices():
    pt = rs.AddPoint(crossing_graph.vertex_coordinates(vkey))
    colour_key = crossing_graph.get_vertex_attribute(vkey, 'colour')
    colour = colours[colour_key]
    rs.ObjectColor(pt, colour)
    graph_objects.append(pt)
rs.MoveObjects(graph_objects, [0, delta_y, 0])
group = rs.AddGroup()
rs.AddObjectsToGroup(graph_objects, group)

rs.EnableRedraw(False)
two_colourable_objects = compute_two_colourable_meshes(PseudoQuadMesh, mesh, kmax = 2)

rs.EnableRedraw(False)
count = 1
for crossing_graph, mesh in two_colourable_objects:
    mesh_guid = draw_mesh(mesh)
    rs.MoveObject(mesh_guid, [delta_x * count, 0, 0])
    graph_objects = [rs.AddLine(crossing_graph.vertex_coordinates(ukey), crossing_graph.vertex_coordinates(vkey)) for ukey, vkey in crossing_graph.edges()]
    for vkey in crossing_graph.vertices():
        pt = rs.AddPoint(crossing_graph.vertex_coordinates(vkey))
        colour_key = crossing_graph.get_vertex_attribute(vkey, 'colour')
        colour = colours[colour_key]
        rs.ObjectColor(pt, colour)
        graph_objects.append(pt)
    rs.MoveObjects(graph_objects, [delta_x * count, delta_y, 0])
    group = rs.AddGroup()
    rs.AddObjectsToGroup(graph_objects, group)
    count += 1

rs.EnableRedraw(True)
