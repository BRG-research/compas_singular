from compas.utilities import window
from compas_pattern.utilities import list_split

__all__ = [
	'add_strip'
]


def sort_faces(mesh, u, v, w):

	faces = [[], []]
	k = 0
	vertex_faces = mesh.vertex_faces(v, ordered=True, include_none=True)
	f0 = mesh.halfedge[w][v] if w is not None else None
	i0 = vertex_faces.index(f0)
	vertex_faces = vertex_faces[i0:] + vertex_faces[:i0]

	for face in vertex_faces:
		
		if face is not None:
			faces[k].append(face)

		if u is None:
		 	if face is None:
		 		k = 1 - k
		elif face == mesh.halfedge[v][u]:
		 		k = 1 - k

	return faces


def add_strip(mesh, polyedge):

	for i in range(len(polyedge)):
		v = polyedge[i]
		if i == 0:
			u = None
			w = polyedge[i + 1]
		elif i == len(polyedge) - 1:
			u = polyedge[i - 1]
			w = None
		else:
			u = polyedge[i - 1]
			w = polyedge[i + 1]
		print(sort_faces(mesh, u, v, w))

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
	from compas_pattern.datastructures.mesh_quad.mesh_quad import QuadMesh
	from compas_plotters.meshplotter import MeshPlotter


	mesh = QuadMesh.from_obj(compas.get('faces.obj'))

	# plotter = MeshPlotter(mesh, figsize = (20, 20))
	# plotter.draw_vertices(radius = 0.25, text='key')
	# plotter.draw_edges()
	# plotter.draw_faces(text='key')
	# plotter.show()

	# polyedge = [6, 7, 8, 9, 10, 11]
	# polyedge = [0, 1, 2, 3, 4, 5]
	# polyedge = [30, 31, 32, 33, 34, 35]
	# polyedge = [24, 25, 26, 32]
	# polyedge = [6, 7, 8, 14, 13, 7, 1]
	polyedge = [0, 1, 2, 8, 2]
	add_strip(mesh, polyedge)



