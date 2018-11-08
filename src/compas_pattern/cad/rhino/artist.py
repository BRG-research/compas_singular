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
	"""Select polyedge vertices via artist.

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
		artist.draw_vertexlabels(text = {key: str(key) for key in vkey_candidates if key not in polyedge[1:]})
		artist.redraw()
		vkey = rhino_helper.mesh_select_vertex(mesh, message = 'vertex')

		artist.clear_layer()
		artist.redraw()
		
		# stop if no vertex is added
		if vkey is None:
			break

		# add vertex to polyedge
		polyedge.append(vkey)

		# stop if polyedge is closed
		if len(polyedge) != 1 and vkey == polyedge[0]:
			break
		
	rs.DeleteLayer('mesh_artist')

	return polyedge

def select_mesh_strip(mesh):
	return 0

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas