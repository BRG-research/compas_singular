import rhinoscriptsyntax as rs

import compas_rhino as rhino

from compas.datastructures.mesh import Mesh
from compas_pattern.datastructures.pseudo_quad_mesh import PseudoQuadMesh
from compas_pattern.datastructures.pseudo_quad_mesh import pqm_from_mesh
from compas_pattern.cad.rhino.utilities import draw_mesh

from compas_pattern.topology.global_propagation import mesh_propagation

from compas_pattern.cad.rhino.editing_artist import apply_rule

# mesh selection
guid = rs.GetObject('get mesh')
layer = rs.ObjectLayer(guid)
mesh = rhino.mesh_from_guid(PseudoQuadMesh, guid)

poles = rs.GetObjects('pole points', filter = 1)
if poles is None:
    poles = []
poles = [rs.PointCoordinates(pole) for pole in poles]

vertices, face_vertices = pqm_from_mesh(mesh, poles)

mesh = PseudoQuadMesh.from_vertices_and_faces(vertices, face_vertices)

regular_vertices = list(mesh.vertices())

while 1:
    rules = ['face_pole', 'edge_pole', 'vertex_pole', 'face_opening', 'flat_corner_2', 'flat_corner_3', 'flat_corner_33', 'split_35', 'split_26', 'simple_split', 'double_split', 'insert_pole', 'insert_partial_pole', 'face_strip_collapse', 'face_strip_insert', 'PROPAGATE', 'STOP']
    rule = rs.GetString('rule?', strings = rules)
    
    if rule == 'PROPAGATE':
        mesh_propagation(mesh, regular_vertices)
        stop = 0
    else:
        stop = apply_rule(mesh, rule)
    
    for vkey in mesh.vertices():
        regular = True
        for fkey in mesh.vertex_faces(vkey):
            if len(mesh.face_vertices(fkey)) != 4:
                regular = False
                break
        if regular and vkey not in regular_vertices:
            regular_vertices.append(vkey)
    
    if stop:
        break

mesh_propagation(mesh, regular_vertices)

mesh = mesh.to_mesh()

# replace mesh
mesh_guid = draw_mesh(mesh)
rs.ObjectLayer(mesh_guid, layer = layer)
rs.DeleteObject(guid)

#layer = 'edited_mesh'
#rs.AddLayer('layer')
#rs.ObjectLayer(mesh_guid, layer = layer)
