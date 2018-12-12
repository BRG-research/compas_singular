import rhinoscriptsyntax as rs

import compas_rhino as rhino
from compas_rhino.geometry import RhinoGeometry

from compas.datastructures.mesh import Mesh
from compas_pattern.datastructures.pseudo_quad_mesh import PseudoQuadMesh
from compas_pattern.datastructures.pseudo_quad_mesh import pqm_from_mesh
from compas_pattern.cad.rhino.utilities import draw_mesh

from compas_pattern.algorithms.editing import editing


# mesh selection
guid = rs.GetObject('get mesh')
mesh = RhinoGeometry.from_guid(guid)
vertices, faces = mesh.get_vertices_and_faces()
mesh = PseudoQuadMesh.from_vertices_and_faces(vertices, faces)

poles = rs.GetObjects('pole points', filter = 1)
if poles is None:
    poles = []
poles = [rs.PointCoordinates(pole) for pole in poles]

vertices, face_vertices = pqm_from_mesh(mesh, poles)

mesh = PseudoQuadMesh.from_vertices_and_faces(vertices, face_vertices)

editing(mesh)

mesh = mesh.to_mesh()

mesh_guid = draw_mesh(mesh)