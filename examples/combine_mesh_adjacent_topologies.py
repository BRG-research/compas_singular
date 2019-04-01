import random

import rhinoscriptsyntax as rs

from compas_rhino.geometry import RhinoMesh
from compas_pattern.datastructures.mesh_quad_coarse import CoarseQuadMesh

from compas.utilities.statistics import average
from compas_pattern.algorithms.adjacent_topologies import adjacent_topologies_delete
from compas_pattern.algorithms.adjacent_topologies import adjacent_topologies_add

from compas_pattern.topology.grammar import delete_strips
from compas_pattern.topology.grammar import split_strips
from compas_pattern.topology.grammar import strips_to_split_to_preserve_boundaries_before_deleting_strips
from compas_pattern.topology.grammar import edit_strips

from compas_pattern.cad.rhino.objects.surface import RhinoSurface
from compas_pattern.cad.rhino.smoothing_constraints import automated_smoothing_constraints
from compas_pattern.cad.rhino.smoothing_constraints import automated_smoothing_surface_constraints
from compas_pattern.algorithms.smoothing import constrained_smoothing

from compas_pattern.cad.rhino.utilities import arrange_guids_in_circle
from compas_pattern.cad.rhino.utilities import draw_mesh


guid0 = rs.GetObject('get quad mesh')

mesh0 = CoarseQuadMesh.from_vertices_and_faces(*RhinoMesh.from_guid(guid0).get_vertices_and_faces())

#points = rs.GetObjects(message = 'point constraints', filter = 1)
#curves = rs.GetObjects(message = 'curve constraints', filter = 4)
surface = RhinoSurface(rs.GetObject(message = 'surface constraint', filter = 8))

def geometrical_processing(mesh, surface):
    return mesh
    #mesh = CoarseQuadMesh.from_quad_mesh(mesh)
    #mesh.init_strip_density()
    #mesh.set_strips_density(1)
    #mesh.densification()
    #constraints = automated_smoothing_constraints(mesh.quad_mesh, curves = curves, points = points)
    #constraints = automated_smoothing_surface_constraints(mesh.quad_mesh, surface)
    #constrained_smoothing(mesh.quad_mesh, kmax = 30, damping = .5, constraints = constraints, algorithm = 'area')
    #return draw_mesh(mesh.quad_mesh)

def performance_evaluation(mesh):
    #return random.random()
    return average([mesh.face_skewness(fkey) for fkey in mesh.faces()])

rs.DeleteObject(guid0)
guid00 = geometrical_processing(mesh0, surface)

#adjacent_topologies_delete = adjacent_topologies_delete(mesh0, 0)
kmax = 8
adjacent_topologies_add = adjacent_topologies_add(mesh0, kmax)

## draw adjacent topologies
#rs.EnableRedraw(False)
#delete_guids = [geometrical_processing(mesh, surface) for mesh, combination in adjacent_topologies_delete]
#arrange_guids_in_circle(delete_guids)
guid_performance = {}
#for i, topology in enumerate(adjacent_topologies_delete):
#    mesh, combination = topology
#    guid_performance[delete_guids[i]] = performance_evaluation(mesh)

add_guids = []
guid_to_add_polyedge = {}
for k, topologies in adjacent_topologies_add.items():
    add_guids_k = []
    for mesh, combination in topologies:
        mesh_guid = geometrical_processing(mesh, surface)
        guid_performance[mesh_guid] = performance_evaluation(mesh)
        add_guids_k.append(mesh_guid)
        guid_to_add_polyedge[mesh_guid] = combination
    add_guids += add_guids_k
    arrange_guids_in_circle(add_guids_k)
maximum = max(guid_performance.values())
minimum = min(guid_performance.values())
#for guid in delete_guids + add_guids:
#    value = guid_performance[guid]
#    norm_value = (value - minimum) / (maximum - minimum)
#    color = [norm_value * 255, (1 - norm_value) * 255, 0]
#    color = [0, 0, 0]
#    rs.ObjectColor(guid, color)
#rs.EnableRedraw(True)
#
## link drawn topologies to operation
#guid_to_delete_strip = {delete_guids[i]: adjacent_topologies_delete[i][1] for i in range(len(adjacent_topologies_delete))}
#
## select adjacent topoliges
#selected_guids = rs.GetObjects(message = 'select meshes to combine', filter = 32)
#
## collect operations
#strips_to_delete = [skey for guid in selected_guids if guid in guid_to_delete_strip for skey in guid_to_delete_strip[guid]]
#polyedges_to_add = [guid_to_add_polyedge[guid] for guid in selected_guids if guid in guid_to_add_polyedge]
#
## apply operations from selected topologies
#combined_mesh = mesh0.copy()
#combined_mesh.collect_strips()
#edit_strips(combined_mesh, polyedges_to_add, strips_to_delete)
#
## draw
#rs.DeleteObjects(delete_guids + add_guids)
#rs.DeleteObject(guid00)
#geometrical_processing(combined_mesh, curves, points)
#
#rs.EnableRedraw(True)
