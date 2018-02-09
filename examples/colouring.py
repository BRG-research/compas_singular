import rhinoscriptsyntax as rs

import compas_rhino as rhino

from compas.datastructures.mesh import Mesh

from compas_pattern.topology.polyline_extraction import quad_mesh_polylines_all

import math

from compas.datastructures.network import Network

from compas_pattern.datastructures.pseudo_quad_mesh import PseudoQuadMesh

from compas_pattern.topology.polyline_extraction import dual_edge_groups

from compas.topology import vertex_coloring

from compas_pattern.topology.face_strip_operations import face_strip_collapse

# mesh selection
guid = rs.GetObject('get mesh')
mesh = rhino.mesh_from_guid(Mesh, guid)

init_polyedges = quad_mesh_polylines_all(mesh)

polyedges = init_polyedges[:]

n = len(polyedges)

vertices = [[math.cos(k * 2 * math.pi / n), math.sin(k * 2 * math.pi / n), 0] for k in range(n)]

edges = []

while len(polyedges) != 0:
    polyedge_1 = polyedges.pop()
    for vkey_1 in polyedge_1:
        if (vkey_1 == polyedge_1[0] or vkey_1 == polyedge_1[-1]) and not mesh.is_vertex_on_boundary(vkey_1):
            continue
        for polyedge_2 in polyedges:
            for vkey_2 in polyedge_2:
                if vkey_1 == vkey_2:
                    if (vkey_2 == polyedge_2[0] or vkey_2 == polyedge_2[-1]) and not mesh.is_vertex_on_boundary(vkey_2):
                        continue
                    if mesh.is_vertex_on_boundary(polyedge_1[0]) and mesh.is_vertex_on_boundary(polyedge_1[1]) and mesh.is_vertex_on_boundary(polyedge_2[0]) and mesh.is_vertex_on_boundary(polyedge_2[1]):
                        continue
                    idx_0 = init_polyedges.index(polyedge_1)
                    idx_1 = init_polyedges.index(polyedge_2)
                    edges.append([idx_0, idx_1])

graph = Network.from_vertices_and_edges(vertices, edges)

adjacency = graph.adjacency

key_to_colour = vertex_coloring(adjacency)

colours = []
for key, colour in key_to_colour.items():
    if colour not in colours:
        colours.append(colour)

for colour in colours:
    rs.AddLayer(name = str(colour))

if rs.IsLayer(str(0)):
    rs.LayerColor(str(0), [255, 0, 0])
if rs.IsLayer(str(1)):
    rs.LayerColor(str(1), [0, 0, 255])
if rs.IsLayer(str(2)):
    rs.LayerColor(str(1), [0, 255, 0])

rs.EnableRedraw(False)
for key, polyedge in enumerate(init_polyedges):
    polyline = rs.AddPolyline([mesh.vertex_coordinates(vkey) for vkey in polyedge])
    colour = key_to_colour[key]
    rs.ObjectLayer(polyline, str(colour))
rs.EnableRedraw(True)