import compas

if compas.RHINO:
	import rhinoscriptsyntax as rs

from compas_singular.rhino.artist import select_quad_mesh_strips


def modify_density(singularity_mesh):

	skeys = select_mesh_strips(singularity_mesh, show_density=True)

	densification_type = rs.GetString('densify based on...?', strings=['density_value', 'target_edge_length', 'target_face_number'])

	if densification_type == 'density_value':
		d = rs.GetInteger('density value', number=3, minimum=1)
		singularity_mesh.set_strips_density(d, skeys)

	elif densification_type == 'target_edge_length':
		t = rs.GetReal('target edge length', number=1.)
		singularity_mesh.set_strip_density_target(t, skeys)

	elif densification_type == 'target_face_number':
		nb_faces = rs.GetInteger('target face number', number=100, minimum=1)
		singularity_mesh.set_strips_density_equal_face_target(nb_faces)

	return singularity_mesh


def update_density(singularity_mesh):

	singularity_mesh.densification()

	return singularity_mesh
