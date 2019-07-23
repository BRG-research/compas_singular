from compas.geometry import add_vectors

__all__ = ['rectangular_array']


def rectangular_array(nx, ny, dx, dy, anchor=[0.0, 0.0, 0.0]):

	pts = []
	for y in range(ny):
		for x in range(nx):
			pts.append(add_vectors(anchor, [x * dx, y * dy, 0.0]))

	return pts

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	print(rectangular_array(4, 2, 10.0, 0.5, anchor=[1.0, -1.0, 0.0]))