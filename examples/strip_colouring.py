import rhinoscriptsyntax as rs
from compas_rhino.geometry import RhinoMesh
from compas_pattern.datastructures.mesh_quad import QuadMesh
from compas_pattern.datastructures.mesh_quad_coarse import CoarseQuadMesh
from compas_pattern.cad.rhino.artist import add_handles_artist
from compas_pattern.cad.rhino.utilities import draw_mesh
from compas_pattern.cad.rhino.utilities import draw_graph
from compas_pattern.topology.colorability import is_network_two_colourable

# get quad mesh and its strips
guid = rs.GetObject('get quad mesh')
mesh = QuadMesh.from_vertices_and_faces(*RhinoMesh.from_guid(guid).get_vertices_and_faces())
mesh.collect_strips()

# draw strip connectivity graph, with colours if two colourable
strip_connectivity = mesh.strip_connectivity()
key_to_group = is_network_two_colourable(strip_connectivity)
if key_to_group is not None:
    group_to_colour = {0: [255,0,0], 1: [0,0,255], 2: [0,255,0]}
    key_to_colour = {key: group_to_colour[group] for key, group in key_to_group.items()}
    draw_graph(strip_connectivity, key_to_colour)

## get coarse quad mesh, draw strip connectivity graph, with colours if two-colourable and draw mesh
#coarse_mesh = CoarseQuadMesh.from_quad_mesh(mesh)
#strip_connectivity = coarse_mesh.strip_connectivity()
#key_to_group = is_network_two_colourable(strip_connectivity)
#if key_to_group is not None:
#    group_to_colour = {0: [255,0,0], 1: [0,0,255], 2: [0,255,0]}
#    key_to_colour = {key: group_to_colour[group] for key, group in key_to_group.items()}
#    draw_graph(strip_connectivity, key_to_colour)
#draw_mesh(coarse_mesh)

# add strips and their contours with colours if two-colourable
strip_colours = mesh.sort_two_colourable_strips()
if strip_colours is not None:
    rs.EnableRedraw(False)
    colours = [[255,0,0],[0,0,255]]
    for i, skeys in enumerate(strip_colours):
        for skey in skeys:
            contours = mesh.strip_contour_polylines(skey)
            contour_1 = rs.AddPolyline(contours[0])
            contour_2 = rs.AddPolyline(contours[1])
            section = rs.AddLine(contours[0][0], contours[1][0])
            rs.AddObjectsToGroup([contour_1, contour_2], rs.AddGroup())
            #sweep = rs.AddSweep2([contour_1, contour_2], [section])
            rs.ObjectColor([contour_1, contour_2], colours[i])
            rs.DeleteObject(section)
    rs.EnableRedraw(True)