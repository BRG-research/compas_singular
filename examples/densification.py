import rhinoscriptsyntax as rs

from compas.datastructures.mesh import Mesh
import compas_rhino as rhino

from compas_pattern.datastructures.pseudo_quad_mesh import PseudoQuadMesh

from compas_pattern.datastructures.pseudo_quad_mesh import pqm_from_mesh

from compas_pattern.algorithms.coarse_to_dense_mesh import quad_mesh_densification

from compas_pattern.cad.rhino.utilities import draw_mesh

coarse_quad_mesh = rs.GetObject('mesh to densify', filter = 32)
coarse_quad_mesh = rhino.mesh_from_guid(PseudoQuadMesh, coarse_quad_mesh)

poles = rs.GetObjects('pole points', filter = 1)
if poles is None:
    poles = []
poles = [rs.PointCoordinates(pole) for pole in poles]

target_length = rs.GetReal('target length for densification', number = 1)

rs.EnableRedraw(False)

vertices, face_vertices = pqm_from_mesh(coarse_quad_mesh, poles)

coarse_quad_mesh = PseudoQuadMesh.from_vertices_and_faces(vertices, face_vertices)

quad_mesh = quad_mesh_densification(coarse_quad_mesh, target_length)

quad_mesh_guid = draw_mesh(quad_mesh)

#layer = 'quad_mesh'
#rs.AddLayer(layer)
#rs.ObjectLayer(quad_mesh_guid, layer = layer)

rs.EnableRedraw(True)