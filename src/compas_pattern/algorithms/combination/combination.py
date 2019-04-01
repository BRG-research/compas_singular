from compas_pattern.datastructures.mesh_quad.grammar_pattern import edit_strips

__all__ = [
	'apply_rules'
]


def apply_rules(coarse_quad_mesh, rules):

	new_topology = coarse_quad_mesh.copy()
	new_topology.collect_strips()
	add_strip = [rule for rule in rules if len(rule) > 1]
	delete_strip = [rule[0] for rule in rules if len(rule) == 1]
	edit_strips(new_topology, add_strip, delete_strip)

	return new_topology


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
