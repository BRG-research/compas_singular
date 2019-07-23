import itertools as it
import operator as op
from math import ceil

from compas_pattern.algorithms.exploration.turtle import Turtle
from compas_pattern.algorithms.exploration.enumeration import collect_polyedges
from compas_pattern.datastructures.mesh_quad.grammar_pattern import delete_strip
from compas_pattern.datastructures.mesh_quad.grammar_pattern import add_strip
from compas_pattern.datastructures.mesh_quad.grammar_pattern import add_and_delete_strips

from compas.geometry import bounding_box
from compas.geometry import add_vectors
from compas.geometry import subtract_vectors

from compas_pattern.geometry.arrays import rectangular_array
from compas_pattern.datastructures.mesh.operations import mesh_move_by

from compas_rhino.artists import MeshArtist

try:
	import rhinoscriptsyntax as rs

except ImportError:
	import platform
	if platform.python_implementation() == 'IronPython':
		raise

__all__ = ['Explorator']

class Explorator:

	def __init__(self, mesh):
		self.mesh = mesh
		
		self.saved_meshes = {}
		
		self.suggested_delete_meshes = {}
		self.suggested_add_meshes = {}
		
		self.processing_func = None
		self.evaluation_func = None
		
		self.combine_rules = True
		
		self.guid_to_mesh_current = {}
		self.guid_to_mesh_saved = {}
		self.guid_to_mesh_suggested = {}

		self.mesh_to_perf = {}
		
		self.dx = 10.0
		self.dy = 10.0

		self.settings = {'add': {'total': 20, 'part_random': .5, 'max_path_length': 20}}

	def set_processing_func(self, func):
		self.processing_func = func

	def set_evaluation_func(self, func):
		self.evaluation_func = func

	def set_scales(self):
		mesh = self.mesh
		box = bounding_box([mesh.vertex_coordinates(vkey) for vkey in mesh.vertices()])
		self.dx = box[2][0] - box[0][0]
		self.dy = box[2][1] - box[0][1]

	# ==============================================================================
	# suggest
	# ==============================================================================

	def suggest_delete_rules(self):
		self.mesh.collect_strips()
		for skey in self.mesh.strips():
			mesh_2 = self.mesh.copy()
			delete_strip(mesh_2, skey)
			self.suggested_delete_meshes.update({mesh_2: skey})

	def suggest_add_rules(self):
		turtle = Turtle(self.mesh)
		polyedges_enum, polyedges_rand = collect_polyedges(turtle, **self.settings['add'])
		for polyedge in polyedges_enum | polyedges_rand:
			mesh_2 = self.mesh.copy()
			try:
				add_strip(mesh_2, polyedge)
				self.suggested_add_meshes.update({mesh_2: polyedge})
			except:
				pass

	def select_rules(self, meshes):

		add_rules = [self.suggested_add_meshes[mesh] for mesh in meshes if mesh in self.suggested_add_meshes]
		delete_rules = [self.suggested_delete_meshes[mesh] for mesh in meshes if mesh in self.suggested_delete_meshes]
		
		return add_rules, delete_rules

	def apply_rules(self, add_rules, delete_rules):

		if not self.combine_rules:
			mesh = self.mesh.copy()
			add_and_delete_strips(mesh, add_rules, delete_rules)
			self.saved_meshes.update({mesh: None})
			self.mesh = mesh
		
		else:
			rules = add_rules + delete_rules
			for k in range(1, len(rules) + 1):
				for combination_rules in it.combinations(rules, k):
					add = [rule for rule in combination_rules if type(rule) != int]
					delete = [rule for rule in combination_rules if type(rule) == int]
					mesh = self.mesh.copy()
					add_and_delete_strips(mesh, add, delete)
					self.saved_meshes.update({mesh: None})
					if k == len(rules):
						self.mesh = mesh.copy()

		self.suggested_delete_meshes = {}
		self.suggested_add_meshes = {}

	def select_suggested_meshes(self):
		guids = rs.GetObjects('get meshes', filter=32)
		return [self.guid_to_mesh_suggested[guid] for guid in guids]

	def modify_add_settings(self):
		keys = self.settings['add'].keys()
		values = self.settings['add'].values()
		new_values = rs.PropertyListBox(keys, values, message='suggested addition rules', title='exploration settings')
		self.settings['add'].update({key: float(value) for key, value in zip(keys, new_values)})

	# ==============================================================================
	# move
	# ==============================================================================

	def move_saved_meshes(self):

		n = len(self.saved_meshes)
		nx, ny = int(ceil(n / (n ** .5))), int(ceil(n ** .5))
		k = 1.5
		dx, dy = self.dx * k, self.dy * k
		d = [0.0, (ny + 1) * dy, 0.0]
		anchor = add_vectors(self.mesh.centroid(), d)
		array = rectangular_array(nx, ny, dx, - dy, anchor=anchor)
		for i, mesh in enumerate(self.saved_meshes):
			mesh_move_by(mesh, subtract_vectors(array[i], mesh.centroid()))

	def move_suggested_meshes(self):
		
		n = len(self.suggested_delete_meshes) + len(self.suggested_add_meshes)
		nx, ny = int(ceil(n / (n ** .5))), int(ceil(n ** .5)) 
		dx, dy = self.dx * 1.5, self.dy * 1.5
		d = [0.0, - 2 * dy, 0.0]
		anchor = add_vectors(self.mesh.centroid(), d)
		array = rectangular_array(nx, ny, dx, - dy, anchor=anchor)
		for i, mesh in enumerate(self.suggested_delete_meshes.keys() + self.suggested_add_meshes.keys()):
			mesh_move_by(mesh, subtract_vectors(array[i], mesh.centroid()))

	# ==============================================================================
	# draw
	# ==============================================================================

	def undraw_current_mesh(self):
		rs.DeleteObjects(self.guid_to_mesh_current.keys())
		self.guid_to_mesh_current = {}

	def undraw_saved_mesh(self):
		rs.DeleteObjects(self.guid_to_mesh_saved.keys())
		self.guid_to_mesh_saved = {}

	def undraw_suggested_meshes(self):
		rs.DeleteObjects(self.guid_to_mesh_suggested.keys())
		self.guid_to_mesh_suggested = {}

	def redraw_current_mesh(self):
		self.undraw_current_mesh()
		guid = MeshArtist(self.processing_func(self.mesh)).draw_mesh()
		self.guid_to_mesh_current[guid] = self.mesh

	def redraw_saved_meshes(self):
		self.undraw_saved_mesh()
		for mesh in self.saved_meshes.keys():
			guid = MeshArtist(self.processing_func(mesh)).draw_mesh()
			self.guid_to_mesh_saved[guid] = mesh

	def redraw_suggested_meshes(self):
		self.undraw_suggested_meshes()
		for mesh in self.suggested_delete_meshes.keys() + self.suggested_add_meshes.keys():
			guid = MeshArtist(self.processing_func(mesh)).draw_mesh()
			self.guid_to_mesh_suggested[guid] = mesh

	# def remove_saved_meshes(self, meshes):
	# 	for mesh in meshes:
	# 		if mesh in self.saved_meshes:
	# 			del self.saved_meshes[mesh]

	# def remove_worst_meshes(self, k=0.5):
	# 	sorted_meshes = sorted(self.saved_meshes.items(), key=op.itemgetter(1))
	# 	n = len(sorted_meshes)
	# 	for mesh, perf in sorted_meshes[:ceil(k * n)]:
	# 		del self.saved_meshes[mesh]

	# ==============================================================================
	# evaluate
	# ==============================================================================

	def evaluate(self):

		guid_to_mesh = {}
		guid_to_mesh.update(self.guid_to_mesh_current)
		guid_to_mesh.update(self.guid_to_mesh_saved)
		guid_to_mesh.update(self.guid_to_mesh_suggested)

		mesh_to_perf = {mesh: self.evaluation_func(mesh) for guid, mesh in guid_to_mesh.items()}

		min_perf = min(mesh_to_perf.values())
		max_perf = max(mesh_to_perf.values())

		for guid, mesh in guid_to_mesh.items():
			perf = mesh_to_perf[mesh]
			k = (perf - min_perf) / (max_perf - min_perf)
			rgb = [255 * k, 255 * (1 - k), 0.0]
			rs.ObjectColor(guid, rgb)


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	pass
