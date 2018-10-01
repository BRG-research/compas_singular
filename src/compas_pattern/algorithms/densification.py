import math

try:
	import rhinoscriptsyntax as rs

except ImportError:
	import platform
	if platform.python_implementation() == 'IronPython':
		raise

from compas.datastructures.mesh import Mesh

from compas_pattern.topology.polyline_extraction import dual_edge_polylines

from compas.geometry.algorithms.interpolation import discrete_coons_patch

from compas_pattern.topology.joining_welding import join_and_weld_meshes

from compas_pattern.datastructures.pseudo_quad_mesh import PseudoQuadMesh

from compas_pattern.datastructures.quad_mesh import QuadMesh
from compas_pattern.datastructures.coarse_quad_mesh import CoarseQuadMesh

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
	'densification',
	'densify_quad_mesh',
]

def densify_quad_mesh(mesh):
	"""Generate dense quad mesh from coarse quad mesh
	based on strip density parameters already stored as edge attributes.

	Parameters
	----------
	mesh : CoarseQuadMesh
		A coarse quad mesh to densify.

	Returns
	-------
	QuadMesh
		A dense quad mesh.
	"""

	meshes = []

	for fkey in mesh.faces():
		ab, bc, cd, da = [[mesh.edge_point(u, v, float(i) / float(mesh.get_edge_attribute((u, v), 'density_parameter'))) for i in range(0, mesh.get_edge_attribute((u, v), 'density_parameter') + 1)] for u, v in mesh.face_halfedges(fkey)]
		vertices, faces = discrete_coons_patch(ab, bc, list(reversed(cd)), list(reversed(da)))
		meshes.append(QuadMesh.from_vertices_and_faces(vertices, faces))

	vertices, face_vertices = join_and_weld_meshes(meshes)
	
	return QuadMesh.from_vertices_and_faces(vertices, face_vertices)

def densification(mesh, target_length, custom = True):
	"""Densifies a quad mesh based on a target length.
	
	Parameters
	----------
	mesh : Mesh
		The quad mesh to densify.
	target_length : float
		Target length for densification.
	custom : bool
		User modification of density parameters.

	Returns
	-------
	dense_mesh: Mesh, None
		Densified quad mesh.
		None if not a quad mesh.

	Raises
	------
	-

	"""

	if not mesh.is_quadmesh():
		return None

	edge_groups, max_group = dual_edge_polylines(mesh)

	dual_polyedges = []
	for i in range(max_group + 1):
		dual_polyedge = []
		for u, v in edge_groups:
			if edge_groups[(u, v)] == i:
				if (v, u) not in dual_polyedge:
					dual_polyedge.append(([u, v]))
		if len(dual_polyedge) > 0:
			dual_polyedges.append(dual_polyedge)

	# determine subdivision parameter based on target length and dual edge average length
	group_subdivision = {}
	edge_group = {}

	for i, dual_polyedge in enumerate(dual_polyedges):
		average_length = 0
		for u, v in dual_polyedge:
			average_length += mesh.edge_length(u, v)
		average_length /= len(dual_polyedge)

		subdivision_parameter = math.ceil(average_length / target_length)
		group_subdivision[i] = subdivision_parameter

		for u, v in dual_polyedge:
			edge_group[(u, v)] = i
			edge_group[(v, u)] = i

	if custom:
		# propose customization of local density
		count = 100
		while count > 0:
			count -= 1
			rs.EnableRedraw(False)
			all_dots = []
			for dual_polyedge in dual_polyedges:
				u0, v0 = dual_polyedge[0]
				group = edge_group[(u0, v0)]
				parameter = group_subdivision[group]
				dots = []
				for u, v in dual_polyedge:
					if u > v:
						continue
					point = mesh.edge_midpoint(u, v)
					group = edge_group[(u, v)]
					parameter = int(group_subdivision[group])
					dots.append(rs.AddTextDot(parameter, point))
				k = float(group) / float(max_group) * 255
				RGB = [k] * 3
				rs.AddGroup(group)
				rs.ObjectColor(dots, RGB)
				rs.AddObjectsToGroup(dots, group)
				all_dots += dots
			rs.EnableRedraw(True)
			dot = rs.GetObject('edge group to modify', filter = 8192)
			if dot is not None:
				group = int(rs.ObjectGroups(dot)[0])
				parameter = rs.GetInteger('subdivision parameter', number = 3, minimum = 1)
				group_subdivision[group] = parameter
			rs.EnableRedraw(False)
			rs.DeleteObjects(all_dots)
			rs.EnableRedraw(True)
			if dot is None:
				break

	# mesh each patch
	meshes = []

	for fkey in mesh.faces():
		a, b, c, d = mesh.face_vertices(fkey) 
		# exceptions if pseudo quad face with a (u, u) edge in no groups
		if (a, b) in edge_group: 
			group_1 = edge_group[(a, b)]
		else:
			group_1 = edge_group[(c, d)]
		if (b, c) in edge_group:
			group_2 = edge_group[(b, c)]
		else:
			group_2 = edge_group[(d, a)]
		n = int(group_subdivision[group_1])
		m = int(group_subdivision[group_2])
		# subdivision points
		ab = [mesh.edge_point(a, b, float(i) / n) for i in range(0, n + 1)]
		bc = [mesh.edge_point(b, c, float(i) / m) for i in range(0, m + 1)]
		dc = [mesh.edge_point(d, c, float(i) / n) for i in range(0, n + 1)]
		ad = [mesh.edge_point(a, d, float(i) / n) for i in range(0, m + 1)]

		# create mesh
		vertices, face_vertices = discrete_coons_patch(ab, bc, dc, ad)
		face_mesh = PseudoQuadMesh.from_vertices_and_faces(vertices, face_vertices)
		meshes.append(face_mesh)

	vertices, face_vertices = join_and_weld_meshes(meshes)
	dense_mesh = PseudoQuadMesh.from_vertices_and_faces(vertices, face_vertices)

	# remove pseudo quads: [a, b, c, c] -> [a, b, c]
	for fkey in dense_mesh.faces():
		to_change = False
		face_vertices = dense_mesh.face_vertices(fkey)
		new_face_vertices = []
		for vkey in face_vertices:
			if len(new_face_vertices) == 0 or vkey != new_face_vertices[-1]:
				new_face_vertices.append(vkey)
			else:
				to_change = True
		if new_face_vertices[0] == new_face_vertices[-1]:
			del new_face_vertices[-1]
			to_change = True
		if to_change:
			dense_mesh.delete_face(fkey)
			dense_mesh.add_face(new_face_vertices, fkey)

	# unweld along two-sided openings

	return dense_mesh

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas

	from compas.plotters import MeshPlotter

	vertices = [[12.97441577911377, 24.33094596862793, 0.0], [18.310085296630859, 8.467333793640137, 0.0], [30.052173614501953, 18.846050262451172, 0.0], [17.135400772094727, 16.750551223754883, 0.0], [16.661802291870117, 22.973459243774414, 0.0], [14.180665969848633, 26.949295043945313, 0.0], [36.052761077880859, 26.372636795043945, 0.0], [26.180931091308594, 21.778648376464844, 0.0], [19.647378921508789, 12.288106918334961, 0.0], [9.355668067932129, 16.475896835327148, 0.0], [18.929227828979492, 16.271940231323242, 0.0], [7.34525203704834, 12.111981391906738, 0.0], [13.31309986114502, 14.699410438537598, 0.0], [18.699434280395508, 19.613750457763672, 0.0], [11.913931846618652, 10.593378067016602, 0.0], [17.163223266601563, 26.870658874511719, 0.0], [26.110898971557617, 26.634754180908203, 0.0], [22.851469039916992, 9.81414794921875, 0.0], [21.051292419433594, 7.556171894073486, 0.0], [22.1370792388916, 19.089054107666016, 0.0]]
	faces = [[15, 5, 0, 4], [0, 9, 12, 4], [9, 11, 14, 12], [14, 1, 8, 12], [1, 18, 17, 8], [17, 2, 7, 8], [2, 6, 16, 7], [16, 15, 4, 7], [13, 19, 7, 4], [19, 10, 8, 7], [10, 3, 12, 8], [3, 13, 4, 12]]

	mesh = CoarseQuadMesh.from_vertices_and_faces(vertices, faces)

	mesh.collect_strip_edge_attribute()
	mesh.density_target_length(2)
	dense_mesh = densify_quad_mesh(mesh)

	plotter = MeshPlotter(dense_mesh, figsize=(10, 6))

	plotter.draw_vertices(text='key', radius=0.2, picker=10)

	for text in plotter.axes.texts:
		text.set_visible(False)

	plotter.draw_edges()
	plotter.draw_faces()
	plotter.show()
