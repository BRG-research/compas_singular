import math

import rhinoscriptsyntax as rs

import compas_rhino as rhino

from compas.datastructures.mesh import Mesh


from compas_pattern.topology.conway_operators import conway_dual
from compas_pattern.topology.conway_operators import conway_join
from compas_pattern.topology.conway_operators import conway_ambo
from compas_pattern.topology.conway_operators import conway_kis
from compas_pattern.topology.conway_operators import conway_needle
from compas_pattern.topology.conway_operators import conway_gyro

from compas.geometry.algorithms.smoothing import mesh_smooth_centroid
from compas.geometry.algorithms.smoothing import mesh_smooth_area

from compas_pattern.cad.rhino.utilities import draw_mesh

mesh = rs.GetObject('mesh', filter = 32)
mesh = rhino.mesh_from_guid(Mesh, mesh)

rs.EnableRedraw(False)
#conway_dual(mesh)
#conway_gyro(mesh, 'left')
conway_join(mesh)
#conway_dual(mesh)

#fixed_vertices = mesh.vertices_on_boundary()
#curve = rs.GetObject('curve', filter = 4)
#for vkey in fixed_vertices:
#    xyz = mesh.vertex_coordinates(vkey)
#    t = rs.CurveClosestPoint(curve, xyz)
#    x, y, z = rs.EvaluateCurve(curve, t)
#    attr = mesh.vertex[vkey]
#    attr['x'] = x
#    attr['y'] = y
#    attr['z'] = z

#mesh_smooth_area(mesh, fixed = fixed_vertices, kmax = 50, damping = .5)

is_polygonal = False
for fkey in mesh.faces():
    if len(mesh.face_vertices(fkey)) > 4:
        is_polygonal = True

if not is_polygonal:
    draw_mesh(mesh)
else:
    edges = []
    for u, v in mesh.edges():
        u_xyz = mesh.vertex_coordinates(u)
        v_xyz = mesh.vertex_coordinates(v)
        if u_xyz != v_xyz:
            edges.append(rs.AddLine(u_xyz, v_xyz))
    rs.AddGroup('mesh')
    rs.AddObjectsToGroup(edges, 'mesh')

rs.EnableRedraw(False)