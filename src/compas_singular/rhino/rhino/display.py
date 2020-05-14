import compas

try:
    import rhinoscriptsyntax as rs

except ImportError:
    compas.raise_if_ironpython()



def change_display(compas_singularity_mesh):

	display_mesh = rs.GetString('display...', strings=['compas_singularity_mesh', 'density_mesh', 'pattern'])

	if display_mesh == 'compas_singularity_mesh':
		draw_mesh(compas_singularity_mesh)

	elif display_mesh == 'density_mesh':
		draw_mesh(compas_singularity_mesh.quad_mesh)

	elif display_mesh == 'pattern':
		draw_mesh(compas_singularity_mesh.polygonal_mesh)
