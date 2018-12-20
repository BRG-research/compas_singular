from compas_pattern.cad.rhino.objects.surface import RhinoSurface
from compas_rhino.geometry.mesh import RhinoMesh
from compas_pattern.datastructures.mesh import Mesh
from compas_pattern.algorithms.smoothing import surface_constrained_smoothing
from compas_pattern.cad.rhino.utilities import draw_mesh

srf = RhinoSurface.from_selection()
mesh = RhinoMesh.from_selection()
mesh = Mesh.from_vertices_and_faces(mesh.get_vertex_coordinates(), mesh.get_face_vertices())
surface_constrained_smoothing(mesh, srf)
draw_mesh(mesh)