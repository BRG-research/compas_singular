import rhinoscriptsyntax as rs
import compas_rhino.artists as rhino_artist
import compas_rhino.helpers as rhino_helper
#from compas_rhino.geometry import RhinoGeometry
from compas_pattern.datastructures.mesh_quad.mesh_quad import QuadMesh
from compas_pattern.datastructures.mesh_quad.grammar_shape import add_handle
from compas_rhino.utilities import draw_mesh

def add_handle_artist(mesh):
	"""Select two mesh faces and add handle.

	Parameters
	----------
	mesh : Mesh
		The mesh.

	Returns
	-------
	fkeys
		The new face keys from the handle.

	"""

	artist = rhino_artist.MeshArtist(mesh, layer='mesh_artist')
	artist.clear_layer()

	artist.draw_facelabels()
	artist.redraw()
	fkey_1 = rhino_helper.mesh_select_face(mesh, message = 'fkey_1')
	if fkey_1 is not None:
		fkey_2 = rhino_helper.mesh_select_face(mesh, message = 'fkey_2')
		if fkey_2 is not None:
			fkeys = add_handle(mesh, fkey_1, fkey_2)

		else:
			fkeys = []
	else:
		fkeys = []

	artist.clear()
	rs.DeleteLayer('mesh_artist')

	return fkeys

def add_handles_artist(mesh):
	"""Select multiple paris of mesh faces and add handles.

	Parameters
	----------
	mesh : Mesh
		The mesh.

	Returns
	-------
	fkeys
		The new face keys from the handles.

	"""

	all_fkeys = []

	while True:
		fkeys = add_handle_artist(mesh)
		if fkeys == []:
			break
		else:
			all_fkeys += fkeys

	return all_fkeys

mesh = rs.GetObject('get mesh')
vertices = rs.MeshVertices(mesh)
faces = rs.MeshFaceVertices(mesh)
#mesh = QuadMesh.from_vertices_and_faces(*RhinoGeometry.from_guid(rs.GetObject('get mesh')).get_vertices_and_faces())
mesh = QuadMesh.from_vertices_and_faces(vertices, faces)
add_handle_artist(mesh)
vertices, faces = mesh.to_vertices_and_faces()
draw_mesh(vertices.values(), faces.values())