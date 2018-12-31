try:
	import rhinoscriptsyntax as rs

except ImportError:
	import platform
	if platform.python_implementation() == 'IronPython':
		raise

import compas_rhino as rhino
import compas_rhino.artists as rhino_artist
import compas_rhino.helpers as rhino_helper

from compas_pattern.datastructures.mesh import Mesh

from compas.geometry import Polyline
from compas.geometry import scale_vector

from compas_pattern.topology.grammar import add_handle

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
	'select_mesh_polyedge',
	'select_mesh_strip',
	'select_mesh_strips',
	'add_handle_artist',
	'add_handles_artist'
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
	count = mesh.number_of_vertices() + 1
	while count > 0:
		count -= 1

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
		
	rs.DeleteLayer('mesh_artist')

	return polyedge

def select_mesh_strip(mesh, show_density = False):
	"""Select quad mesh strip.

	Parameters
	----------
	mesh : Mesh
		The mesh.
	show_density : bool
		Optional argument to show strip density parameter. False by default.

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
	guids_to_strip = {rs.AddPolyline(mesh.strip_edge_polyline(skey)): skey for skey in mesh.strips()}
	for guid, skey in guids_to_strip.items():
		rs.ObjectColor(guid, strip_to_color[skey])
		rs.CurveArrows(guid, arrow_style = 3)

	# show strip density parameters
	if show_density:
		guids_to_dot = {guid: rs.AddTextDot(mesh.get_strip_density(skey), Polyline(mesh.strip_edge_polyline(skey)).point(t = .5)) for guid, skey in guids_to_strip.items()}
		for guid, dot in guids_to_dot.items():
			rs.ObjectColor(dot, rs.ObjectColor(guid))

	# return polyline strip
	rs.EnableRedraw(True)
 	skey = guids_to_strip.get(rs.GetObject('Get strip.', filter = 4), None)
 	rs.EnableRedraw(False)

 	# delete objects
 	rs.DeleteObjects(guids_to_strip.keys())
 	if show_density:
 		rs.DeleteObjects(guids_to_dot.values())
 	
 	return skey

def select_mesh_strips(mesh, show_density = False):
	"""Select quad mesh strips.

	Parameters
	----------
	mesh : Mesh
		The mesh.
	show_density : bool
		Optional argument to show strip density parameter. False by default.

	Returns
	-------
	hashable
		The strip key.

	"""

	strips = list(mesh.strips())
	skeys = []

	while True:
		
		skey = select_mesh_strip(mesh, show_density = show_density)

		if skey is None:
			return skeys

		if skey in strips:
			skeys.append(skey)

def add_handle_artist(mesh, extremity = False):
	"""Select two mesh faces and add handle.

	Parameters
	----------
	mesh : Mesh
		The mesh.
    extremity : bool
        Add rings of faces at the extremitites. Default is False.

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
			fkeys = add_handle(mesh, fkey_1, fkey_2, extremity)

		else:
			fkeys = []
	else:
		fkeys = []

	artist.clear()
	rs.DeleteLayer('mesh_artist')

	return fkeys

def add_handles_artist(mesh, extremity = False):
	"""Select multiple paris of mesh faces and add handles.

	Parameters
	----------
	mesh : Mesh
		The mesh.
    extremity : bool
        Add rings of faces at the extremitites. Default is False.

	Returns
	-------
	fkeys
		The new face keys from the handles.

	"""

	all_fkeys = []

	while True:
		fkeys = add_handle_artist(mesh, extremity)
		if fkeys == []:
			break
		else:
			all_fkeys += fkeys

	return all_fkeys

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas