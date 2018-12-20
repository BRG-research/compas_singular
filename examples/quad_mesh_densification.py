import rhinoscriptsyntax as rs

from compas_pattern.datastructures.mesh_quad_coarse import CoarseQuadMesh

from compas_rhino.geometry import RhinoMesh

from compas_pattern.algorithms.two_colourable_projection import two_colourable_projection

from compas.geometry import bounding_box
from compas.geometry import distance_point_point

from compas_pattern.cad.rhino.utilities import draw_mesh
from compas_pattern.cad.rhino.utilities import draw_graph

guid = rs.GetObject('get quad mesh')
mesh = CoarseQuadMesh.from_vertices_and_faces(*RhinoMesh.from_guid(guid).get_vertices_and_faces())

mesh.collect_strips()
mesh.init_strip_density()
mesh.set_strips_density_target(1)
mesh.densification()
draw_mesh(mesh.quadmesh)