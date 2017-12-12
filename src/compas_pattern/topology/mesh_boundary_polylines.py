from compas.datastructures.mesh import Mesh

from compas.topology import delaunay_from_points

from compas_pattern.datastructures.mesh import face_circle

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2014, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
    'mesh_boundaries',
]

def mesh_boundaries(mesh):
    """Extract mesh outer and inner boundaries as lists of vertices. Extension of vertices_on_boundary(self, ordered = True) for several boundaries.

    Parameters
    ----------
    mesh : Mesh
        Mesh.

    Returns
    -------
    boundaries: list
        List of polylines as lists of vertices forming the boundaries.

    Raises
    ------
    -

    """

    boundary_vertices = set()
    for vkey, nbrs in iter(mesh.halfedge.items()):
        for nbr, face in iter(nbrs.items()):
            if face is None:
                boundary_vertices.add(vkey)
                boundary_vertices.add(nbr)

    boundary_vertices = list(boundary_vertices)

    boundaries = []
    while len(boundary_vertices) > 0:
        boundary = [boundary_vertices.pop()]

        while 1:
            for nbr, fkey in iter(mesh.halfedge[boundary[-1]].items()):
                if fkey is None:
                    boundary.append(nbr)
                    break

            if boundary[0] == boundary[-1]:
                boundaries.append(boundary)
                break
            else:
                boundary_vertices.remove(boundary[-1])

    return boundaries



# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas

    vertices = [[0.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 2.0, 0.0], [0.0, 3.0, 0.0], [0.0, 4.0, 0.0], [0.0, 5.0, 0.0], [1.0, 0.0, 0.0], [1.0, 1.0, 0.0], [1.0, 2.0, 0.0], [1.0, 3.0, 0.0], [1.0, 4.0, 0.0], [1.0, 5.0, 0.0], [2.0, 0.0, 0.0], [2.0, 1.0, 0.0], [2.0, 2.0, 0.0], [2.0, 3.0, 0.0], [2.0, 4.0, 0.0], [2.0, 5.0, 0.0], [3.0, 0.0, 0.0], [3.0, 1.0, 0.0], [3.0, 2.0, 0.0], [3.0, 3.0, 0.0], [3.0, 4.0, 0.0], [3.0, 5.0, 0.0], [4.0, 0.0, 0.0], [4.0, 1.0, 0.0], [4.0, 2.0, 0.0], [4.0, 3.0, 0.0], [4.0, 4.0, 0.0], [4.0, 5.0, 0.0], [5.0, 0.0, 0.0], [5.0, 1.0, 0.0], [5.0, 2.0, 0.0], [5.0, 3.0, 0.0], [5.0, 4.0, 0.0], [5.0, 5.0, 0.0]]
    face_vertices = [[7, 1, 0, 6], [8, 2, 1, 7], [9, 3, 2, 8], [10, 4, 3, 9], [11, 5, 4, 10], [13, 7, 6, 12], [14, 8, 7, 13], [16, 10, 9, 15], [17, 11, 10, 16], [19, 13, 12, 18], [20, 14, 13, 19], [21, 15, 14, 20], [22, 16, 15, 21], [23, 17, 16, 22], [25, 19, 18, 24], [26, 20, 19, 25], [27, 21, 20, 26], [28, 22, 21, 27], [29, 23, 22, 28], [31, 25, 24, 30], [32, 26, 25, 31], [33, 27, 26, 32], [34, 28, 27, 33], [35, 29, 28, 34]]
    mesh = Mesh.from_vertices_and_faces(vertices, face_vertices)

    print mesh_boundaries(mesh)