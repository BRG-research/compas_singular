import rhinoscriptsyntax as rs
from compas_rhino.geometry import RhinoMesh
from compas_pattern.datastructures.mesh_quad_coarse import CoarseQuadMesh
from compas_pattern.topology.grammar import add_strip
from compas_pattern.topology.grammar import add_strips
from compas_pattern.cad.rhino.artist import select_mesh_polyedge
from compas_pattern.cad.rhino.utilities import draw_mesh

from compas.topology import breadth_first_paths

import compas_rhino.artists as rhino_artist
import compas_rhino.helpers as rhino_helper

from compas_pattern.cad.rhino.smoothing_constraints import automated_smoothing_constraints
from compas_pattern.algorithms.smoothing import constrained_smoothing

from compas.datastructures.mesh.operations import mesh_weld

import itertools

def select_vertex(mesh, message = None):
    if message is None:
        message = 'select vertex'
    artist = rhino_artist.MeshArtist(mesh, layer='mesh_artist')
    artist.clear_layer()
    artist.draw_vertexlabels(text = {key: str(key) for key in mesh.vertices()})
    artist.redraw()
    vkey = rhino_helper.mesh_select_vertex(mesh, message)
    artist.clear_layer()
    artist.redraw()
    rs.DeleteLayer('mesh_artist')
    return vkey

guid = rs.GetObject('get quad mesh')

mesh = CoarseQuadMesh.from_vertices_and_faces(*RhinoMesh.from_guid(guid).get_vertices_and_faces())
mesh.init_strip_density()


skey = add_strip(mesh, select_mesh_polyedge(mesh))
draw_mesh(mesh)
mesh.set_strips_density_target(.5)
mesh.densification()
draw_mesh(mesh.quad_mesh)

#polyedge_1 = select_mesh_polyedge(mesh)
#polyedge_2 = select_mesh_polyedge(mesh)
#skey = add_strips(mesh, [polyedge_1, polyedge_2])
#draw_mesh(mesh)




#adjacency = mesh.adjacency
#
##root = select_vertex(mesh, 'select root')
##goal = select_vertex(mesh, 'select goal')
#
#curve = rs.GetObject(message = 'boundary curve constraint')
#
#combinations = list(itertools.combinations(list(mesh.vertices_on_boundary()), 2))
#for i, combination in enumerate(combinations):
#    start, end = combination
#    polyedges = breadth_first_paths(adjacency, start, end)
#    for j, polyedge in enumerate(list(polyedges)):
#        #print polyedge
#        edited_mesh = mesh.copy()
#        edited_mesh.collect_strips()
#        add_strip(edited_mesh, polyedge)
#        #constraints = automated_smoothing_constraints(edited_mesh, curves = [curve])
#        #constrained_smoothing(edited_mesh, kmax = 30, damping = .5, constraints = constraints, algorithm = 'area')
#        #guid = draw_mesh(edited_mesh)
#        edited_mesh.init_strip_density()
#        #edited_mesh.set_strips_density_target(.5)
#        edited_mesh.set_strips_density(3)
#        edited_mesh.densification()
#        quad_mesh = edited_mesh.quad_mesh.copy()
#        constraints = automated_smoothing_constraints(quad_mesh, curves = [curve])
#        constrained_smoothing(quad_mesh, kmax = 30, damping = .5, constraints = constraints, algorithm = 'area')
#        rs.EnableRedraw(False)
#        guid = draw_mesh(quad_mesh)
#        vector = [(j + 1) * 5., - (i + 1) * 5., 0.]
#        rs.MoveObject(guid, vector)
#        guids = [rs.AddPolyline(polyline) for polyline in quad_mesh.singularity_polylines()]
#        rs.MoveObjects(guids, vector)
#        rs.ObjectColor(guids, [255, 0, 0])
#        rs.EnableRedraw(True)
