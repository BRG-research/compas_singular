
import rhinoscriptsyntax as rs

from compas.datastructures.mesh import Mesh
import compas_rhino as rhino
from compas_rhino.geometry import RhinoGeometry

from compas_pattern.datastructures.pseudo_quad_mesh import PseudoQuadMesh

from compas_pattern.datastructures.pseudo_quad_mesh import pqm_from_mesh

from compas_pattern.algorithms.densification import densification

from compas_pattern.cad.rhino.utilities import draw_mesh

guids = rs.GetObjects('get meshes')
poles = rs.GetObjects('pole points', filter = 1)
if poles is None:
    poles = []
poles = [rs.PointCoordinates(pole) for pole in poles]
target_length = rs.GetReal('target length for densification', number = 1)

for guid in guids:
    mesh = RhinoGeometry.from_guid(guid)
    vertices, faces = mesh.get_vertices_and_faces()
    coarse_quad_mesh = Mesh.from_vertices_and_faces(vertices, faces)
    
    
    rs.EnableRedraw(False)
    
    vertices, face_vertices = pqm_from_mesh(coarse_quad_mesh, poles)
    
    coarse_quad_mesh = PseudoQuadMesh.from_vertices_and_faces(vertices, face_vertices)
    
    quad_mesh = densification(coarse_quad_mesh, target_length)
    
    quad_mesh_guid = draw_mesh(quad_mesh)
    
    #layer = 'quad_mesh'
    #rs.AddLayer(layer)
    #rs.ObjectLayer(quad_mesh_guid, layer = layer)
    
    rs.EnableRedraw(True)