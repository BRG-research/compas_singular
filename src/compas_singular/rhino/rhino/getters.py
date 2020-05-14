import compas

try:
    import rhinoscriptsyntax as rs

except ImportError:
    compas.raise_if_ironpython()

from compas_rhino.geometry import RhinoMesh

from compas_singular.datastructures.mesh_quad_pseudo_coarse.mesh_quad_pseudo_coarse import CoarsePseudoQuadMesh
from compas_singular.datastructures.mesh_quad_pseudo.mesh_quad_pseudo import PseudoQuadMesh

from compas.utilities import pairwise


def clean_faces(faces):

	for face in faces:
		for u, v in pairwise(face + face[:1]):
			if u == v:
				face.remove(u)
				break


def get_compas_singularity_mesh():
	guid = rs.GetObject('get compas_singularity mesh', filter=32)
	vertices, faces = RhinoMesh.from_guid(guid).get_vertices_and_faces()
	clean_faces(faces)
	poles = []
	for face in faces:
		if len(face) != 4:
			poles = [rs.PointCoordinates(point) for point in rs.GetObjects('get pole points', filter=1)]
			break
	compas_singularity_mesh = CoarsePseudoQuadMesh.from_vertices_and_faces_with_poles(vertices, faces, poles)
	compas_singularity_mesh.init_strip_density()
	compas_singularity_mesh.quad_mesh = compas_singularity_mesh.copy()
	compas_singularity_mesh.polygonal_mesh = compas_singularity_mesh.copy()
	return compas_singularity_mesh


def get_dense_mesh():
	guid = rs.GetObject('get dense mesh', filter=32)
	vertices, faces = RhinoMesh.from_guid(guid).get_vertices_and_faces()
	clean_faces(faces)
	poles = []
	for face in faces:
		if len(face) != 4:
			poles = [rs.PointCoordinates(point) for point in rs.GetObjects('get pole points', filter=1)]
			break
	compas_singularity_mesh = CoarsePseudoQuadMesh.from_quad_mesh(PseudoQuadMesh.from_vertices_and_faces_with_poles(vertices, faces, poles))
	return compas_singularity_mesh
	