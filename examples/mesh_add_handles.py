import rhinoscriptsyntax as rs
from compas_rhino.geometry import RhinoMesh
from compas_pattern.datastructures.mesh_quad import QuadMesh
from compas_pattern.cad.rhino.artist import add_handles_artist
from compas_pattern.cad.rhino.utilities import draw_mesh

guid = rs.GetObject('get quad mesh')

mesh = QuadMesh.from_vertices_and_faces(*RhinoMesh.from_guid(guid).get_vertices_and_faces())

add_handles_artist(mesh)

draw_mesh(mesh)