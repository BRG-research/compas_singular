import itertools

from compas_pattern.datastructures.mesh_quad_coarse.mesh_quad_coarse import CoarseQuadMesh

__all__ = [
	'Combining'
]


class Combining(CoarseQuadMesh):

	addition_rules = []
	deletion_rules = []
	combination_rules = []
	interpolation_rules = {}

	def set_addition_rules(self, fmax=None):
		"""All rules adding exactly one strip.
		Optional maximum on the length (number of faces) of the added strip.

		Parameters
		----------
		fmax : int, optional
			An optional maximum length (number of faces) on the length of the added strip.
			Default is None.

		"""

		for polyedge in self.open_boundary_polyedges_no_duplicates(fmax):
			self.addition_rules.append(polyedge)
	
	def set_deletion_rules(self):
		"""All rules deleting exactly one strip.

		"""
		
		self.collect_strips()
		for skey in self.strips():
			self.deletion_rules.append(skey)

	def combine_rules(self, addition_rules, deletion_rules):

		self.combination_rules.append((addition_rules + deletion_rules))

	def interpolate_rules(self):

		all_rules = set([rule for combination in self.combination_rules for rule in combination])

		for k in range(1, len(all_rules)):
			for subcombination in itertools.combinations(all_rules, k):
				weights = tuple([sum([rule in combination for rule in subcombination]) for combination in self.combination_rules])
				if weights in self.interpolation_rules:
					self.interpolation_rules[weights].append(subcombination)
				else:
					self.interpolation_rules[weights] = [subcombination]


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
	import compas_pattern
	from compas_pattern.datastructures.mesh_quad_coarse.mesh_quad_coarse import CoarseQuadMesh

	combinator = Combining.from_json(compas_pattern.get('mesh_freeform_1_coarse.json'))

	combinator.set_addition_rules(fmax = 3)	
	combinator.set_deletion_rules()

	combinator.combine_rules(combinator.addition_rules[:0], combinator.deletion_rules[:2])
	combinator.combine_rules(combinator.addition_rules[:0], combinator.deletion_rules[2:4])
	combinator.interpolate_rules()

	#print combinator.interpolation_rules
