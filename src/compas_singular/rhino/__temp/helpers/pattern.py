import compas

if compas.RHINO:
	import rhinoscriptsyntax as rs


def apply_conway_operator(singularity_mesh):
	conway_operators = {
		'back_to_seed',
		'conway_dual',
		'conway_join',
		'conway_ambo',
		'conway_kis',
		'conway_needle',
		'conway_zip',
		'conway_truncate',
		'conway_ortho',
		'conway_expand',
		'conway_gyro',
		'conway_snub',
		'conway_meta',
		'conway_bevel'
	}

	conway = {operator[7:]: operator for operator in conway_operators}

	operator = rs.GetString('select Conway operator', strings=conway.keys() + ['exit'])

	if operator == 'back_to_seed':
		singularity_mesh.polygonal_mesh = singularity_mesh.quad_mesh.copy()

	elif operator in conway and conway[operator] in globals() and str(conway[operator])[: 6] == 'conway':
		singularity_mesh.polygonal_mesh = globals()[conway[operator]](singularity_mesh.polygonal_mesh)

	return singularity_mesh

