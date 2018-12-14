import rhinoscriptsyntax as rs

from compas_rhino.geometry import RhinoGeometry

from compas_pattern.datastructures.mesh import Mesh
from compas_pattern.datastructures.mesh_quad import QuadMesh
from compas_pattern.datastructures.mesh_quad_coarse import CoarseQuadMesh

mesh = QuadMesh.from_vertices_and_faces(*RhinoGeometry.from_guid(rs.GetObject('get mesh')).get_vertices_and_faces())
mesh = CoarseQuadMesh.from_quad_mesh(mesh)

mesh.to_json('Z:/Users/Robin/Documents/COMPAS/packages/compas_pattern/tests/mesh_square_circle_coarse.json')
