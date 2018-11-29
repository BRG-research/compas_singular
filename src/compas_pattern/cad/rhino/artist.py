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

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
	'select_mesh_polyedge',
	'select_mesh_strip'
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

def select_mesh_strip(mesh):
	"""Select quad mesh strip.

	Parameters
	----------
	mesh : Mesh
		The mesh.

	Returns
	-------
	hashable
		The strip key.

	"""
	
	n = mesh.number_of_strips()

	# different colors per strip
	strip_to_color = {skey: [255 * float(i) / (n - 1)] * 3 for i, skey in enumerate(mesh.strips())}

	# add strip polylines with colors and arrows
	guids_to_strip = {rs.AddPolyline(mesh.strip_edge_polyline(skey)): skey for skey in mesh.strips()}
	for guid, skey in guids_to_strip.items():
		rs.ObjectColor(guid, strip_to_color[skey])
		rs.CurveArrows(guid, arrow_style = 3)
	
	# return polyline strip
	rs.EnableRedraw(True)
 	skey =  guids_to_strip[rs.GetObject('Get strip.', filter = 4)]
 	rs.EnableRedraw(False)
 	rs.DeleteObjects(guids_to_strip.keys())
 	return skey


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas