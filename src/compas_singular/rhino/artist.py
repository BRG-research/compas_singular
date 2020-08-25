import compas

if compas.RHINO:
	import rhinoscriptsyntax as rs

import compas_rhino as rhino
import compas_rhino.artists as rhino_artist
#import compas_rhino.helpers as rhino_helper

from compas.geometry import Polyline
from compas.geometry import scale_vector


__all__ = [
	'select_mesh_polyedge',
	'select_quad_mesh_polyedge',
	'select_quad_mesh_strip',
	'select_quad_mesh_strips'
]


def select_mesh_polyedge(mesh):
	"""Select mesh polyedge.

	Parameters
	----------
	mesh : Mesh
		The mesh.

	Returns
	-------
	polyedge : list
		The list of polyedge vertices.
	"""

	# add layer
	artist = rhino_artist.MeshArtist(mesh, layer='mesh_artist')
	artist.clear_layer()

	# collect polyedge vertices
	polyedge = []
	lines = []
	while True:

		# define candidate vertices for polyedge
		if len(polyedge) == 0:
			vkey_candidates = mesh.vertices()
		else:
			vkey_candidates = mesh.vertex_neighbors(polyedge[-1])

		# get vertex among candidates
		artist.draw_vertexlabels(text = {key: str(key) for key in vkey_candidates})
		artist.redraw()

		vkey = rhino_helper.mesh_select_vertex(mesh, message = 'vertex')

		artist.clear_layer()
		artist.redraw()

		# stop if no vertex is added
		if vkey is None:
			break

		# add vertex to polyedge
		polyedge.append(vkey)

		if len(polyedge) > 1:
			u = mesh.vertex_coordinates(polyedge[-2])
			v = mesh.vertex_coordinates(polyedge[-1])
			guid = rs.AddLine(u, v)
			rs.ObjectColor(guid, [255, 255, 0])
			lines.append(guid)

	rs.DeleteLayer('mesh_artist')
	rs.DeleteObjects(lines)

	return polyedge


def select_quad_mesh_polyedge(mesh):
	"""Select quad mesh polyedge. Selecting one edge is equivalent to selecting one polyedge.

	Parameters
	----------
	mesh : QuadMesh
		The quad mesh.

	Returns
	-------
	list
		The list of polyedge vertices.
	"""

	artist = rhino_artist.MeshArtist(mesh, layer='mesh_artist')
	artist.clear_layer()
	artist.draw_edgelabels()
	artist.redraw()

	edge = rhino_helper.mesh_select_edge(mesh)

	artist.clear_layer()
	artist.redraw()
	rs.DeleteLayer('mesh_artist')

	return mesh.polyedge(*edge)


def select_quad_mesh_strip(mesh, text='key'):
	"""Select quad mesh strip.

	Parameters
	----------
	mesh : QuadMesh, CoarseQuadMesh
		The quad mesh or coarse quad mesh.
	text : str
		Optional argument to show the strip key or density. The key by default.

	Returns
	-------
	hashable
		The strip key.
	"""

	n = mesh.number_of_strips()

	# different colors per strip
	strip_to_color = {skey: scale_vector([float(i), 0, n - 1 - float(i)], 255 / (n - 1)) for i, skey in enumerate(mesh.strips())}

	rs.EnableRedraw(False)

	# add strip polylines with colors and arrows
	guids_to_strip = {rs.AddPolyline(mesh.strip_edge_midpoint_polyline(skey)): skey for skey in mesh.strips()}
	for guid, skey in guids_to_strip.items():
		rs.ObjectColor(guid, strip_to_color[skey])
		rs.CurveArrows(guid, arrow_style = 3)

	# show strip key or density
	if text == 'key' or text == 'density':
		if text == 'key':
			guids_to_dot = {guid: rs.AddTextDot(skey, Polyline(mesh.strip_edge_midpoint_polyline(skey)).point(t = .5)) for guid, skey in guids_to_strip.items()}
		elif text == 'density':
			guids_to_dot = {guid: rs.AddTextDot(mesh.get_strip_density(skey), Polyline(mesh.strip_edge_midpoint_polyline(skey)).point(t = .5)) for guid, skey in guids_to_strip.items()}
		for guid, dot in guids_to_dot.items():
			rs.ObjectColor(dot, rs.ObjectColor(guid))

	# return polyline strip
	rs.EnableRedraw(True)
	skey = guids_to_strip.get(rs.GetObject('Get strip.', filter = 4), None)
	rs.EnableRedraw(False)

	# delete objects
	rs.DeleteObjects(guids_to_strip.keys())
	if text == 'key' or text == 'density':
		rs.DeleteObjects(guids_to_dot.values())

	return skey


def select_quad_mesh_strips(mesh, text='key'):
	"""Select quad mesh strips.

	Parameters
	----------
	mesh : QuadMesh, CoarseQuadMesh
		The quad mesh or coarse quad mesh.
	text : str
		Optional argument to show the strip key or density. The key by default.

	Returns
	-------
	strips : list
		The list of strip keys.
	"""

	strips = list(mesh.strips())
	skeys = []

	while True:

		skey = select_quad_mesh_strip(mesh, text=text)

		if skey is None:
			return skeys

		if skey in strips:
			skeys.append(skey)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
