import compas_rhino as rhino

try:
	import rhinoscriptsyntax as rs

except ImportError:
	import platform
	if platform.python_implementation() == 'IronPython':
		raise

from compas_pattern.geometry.metrics import minimum
from compas_pattern.geometry.metrics import maximum
from compas_pattern.geometry.metrics import mean
from compas_pattern.geometry.metrics import standard_deviation

from compas_pattern.geometry.metrics import mesh_edge_lengths
from compas_pattern.geometry.metrics import mesh_face_areas
from compas_pattern.geometry.metrics import mesh_face_aspect_ratios
from compas_pattern.geometry.metrics import mesh_face_skewnesses
from compas_pattern.geometry.metrics import mesh_face_curvatures
from compas_pattern.geometry.metrics import mesh_vertex_curvatures


__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
	'print_metrics',
]


def print_metrics(mesh):
	"""Print metrics value of a mesh.
	
	Parameters
	----------
	mesh : Mesh
		A mesh.

	Returns
	-------
	results: dict
		Dictionary of metric values {metric: value}.

	Raises
	------
	-

	"""
	operators = {
			'mesh_edge_lengths': mesh_edge_lengths, 
			'mesh_face_curvatures': mesh_face_curvatures,
			'mesh_face_skewnesses': mesh_face_skewnesses,
			'minimum': minimum,
			'maximum': maximum,
			'mean': mean,
			'standard_deviation': standard_deviation,
			 }

	default_metrics_bool = [('minimum edge_lengths', False),
			   ('maximum edge_lengths', False),
			   ('mean edge_lengths', False),
			   ('standard_deviation edge_lengths', True),
			   ('minimum face_curvatures', False),
			   ('maximum face_curvatures', True),
			   ('mean face_curvatures', False),
			   ('standard_deviation face_curvatures', False),
			   ('minimum face_skewnesses', False),
			   ('maximum face_skewnesses', False),
			   ('mean face_skewnesses', True),
			   ('standard_deviation face_skewnesses', False),
	]
	
	metrics_bool = rs.CheckListBox(default_metrics_bool, message = 'which metrics do you want to print?', title = 'metrics')

	results = {}
	for item in metrics_bool:
		metrics, boolean = item
		if boolean:
			metrics_1, metrics_2 = metrics.split(' ')
			result = operators[metrics_1](operators[metrics_2](mesh).values())
			results[metrics] = result

	# TO DO: add units
	for key, value in results.items():
		print key, ': ', value

	return results

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas