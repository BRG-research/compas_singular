from compas_pattern.datastructures.mesh_quad_coarse.mesh_quad_coarse import CoarseQuadMesh
from compas_pattern.algorithms.exploration.explorator import Explorator
from compas_rhino.artists import MeshArtist
from compas_rhino.helpers import mesh_from_guid

try:
	import rhinoscriptsyntax as rs

except ImportError:
	import platform
	if platform.python_implementation() == 'IronPython':
		raise

__all__ = [
	'explore',
	'dummy_processing_func',
	'dummy_evaluation_func',
	]


def dummy_processing_func(mesh):
	return mesh


def dummy_evaluation_func(mesh):
	return 1

def explore(processing_func=dummy_processing_func, evaluation_func=dummy_evaluation_func):

	guid = rs.GetObject('get mesh', filter=32)
	mesh = mesh_from_guid(CoarseQuadMesh, guid)

	explorator = Explorator(mesh)
	explorator.set_processing_func(processing_func)
	explorator.set_evaluation_func(evaluation_func)
	explorator.set_scales()

	explorator.modify_add_settings()

	rs.EnableRedraw(False)
	rs.DeleteObject(guid)
	explorator.redraw_current_mesh()
	rs.EnableRedraw(True)

	count = 20
	while count:
		count -= 1

		explorator.suggest_delete_rules()
		explorator.suggest_add_rules()

		explorator.move_suggested_meshes()
		rs.EnableRedraw(False)
		explorator.redraw_suggested_meshes()
		explorator.evaluate()
		rs.EnableRedraw(True)

		meshes = explorator.select_suggested_meshes()
		add_rules, delete_rules = explorator.select_rules(meshes)
		explorator.apply_rules(add_rules, delete_rules)

		explorator.move_saved_meshes()
		rs.EnableRedraw(False)
		explorator.undraw_suggested_meshes()
		explorator.redraw_current_mesh()
		explorator.redraw_saved_meshes()
		explorator.evaluate()
		rs.EnableRedraw(True)

		if rs.GetString('continue?', 'No', ['Yes', 'No']) != 'Yes':
		 	break
		 
		explorator.modify_add_settings()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	pass
