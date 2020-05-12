import compas

try:
    import rhinoscriptsyntax as rs

except ImportError:
    compas.raise_if_ironpython()



def change_display(singularity_mesh):

	display_mesh = rs.GetString('display...', strings=['singularity_mesh', 'density_mesh', 'pattern'])

	if display_mesh == 'singularity_mesh':
		draw_mesh(singularity_mesh)

	elif display_mesh == 'density_mesh':
		draw_mesh(singularity_mesh.quad_mesh)

	elif display_mesh == 'pattern':
		draw_mesh(singularity_mesh.polygonal_mesh)
