import math

from compas.datastructures.mesh import Mesh

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
    'template',
]

def template(corners = [False, False, False, False]):
    """Subdivide a polygon face into quads which used to be a quad with four original vertices.
    Subdivision is valid only if opposite edges have the same number of points or if one only has two.
    "len(ab) = len(cd) or len(ab) = 2 or len(cd) = 2"

    Parameters
    ----------
    mesh : Mesh
        A quad mesh.
    fkey: int
        Key of face to subdivide.
    regular_vertices: list
        List of four face vertex indices.

    Returns
    -------
    mesh : mesh, None
        The modified quad mesh.
        None if face was an original quad face with four original vertices or if subdivision if not valid.

    Raises
    ------
    -

    """

    vertices = [[float(i) / 3, float(j) / 3, 0] for j in range(4) for i in range(4)]
    a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p = range(len(vertices))

    face_vertices = [[f, g, k, j]]

    if corners[0] == 1:
        face_vertices.append([a, b, f, e])
    if corners[1] == 1:
        face_vertices.append([c, d, h, g])
    if corners[2] == 1:
        face_vertices.append([k, l, p, o])
    if corners[3] == 1:
        face_vertices.append([i, j, n , m])

    if corners[0 : 2] == [0,0]:
        face_vertices.append([a, d, g, f])
    elif corners[0 : 2] == [1,0]:
        face_vertices.append([b, d, g, f])
    elif corners[0 : 2] == [0,1]:
        face_vertices.append([a, c, g, f])
    else:
        face_vertices.append([b, c, g, f])

    if corners[1 : 3] == [0,0]:
        face_vertices.append([d, p, k, g])
    elif corners[1 : 3] == [1,0]:
        face_vertices.append([h, p, k , g])
    elif corners[1 : 3] == [0,1]:
        face_vertices.append([d, l, k, g])
    else:
        face_vertices.append([h, l, k , g])

    if corners[2 : 4] == [0,0]:
        face_vertices.append([p, m, j, k])
    elif corners[2 : 4] == [1,0]:
        face_vertices.append([o, m, j, k])
    elif corners[2 : 4] == [0,1]:
        face_vertices.append([p, n, j, k])
    else:
        face_vertices.append([o, n, j, k])

    if corners[3 : 4] + corners[0 : 1] == [0,0]:
        face_vertices.append([m, a, f, j])
    elif corners[3 : 4] + corners[0 : 1] == [1,0]:
        face_vertices.append([i, a, f, j])
    elif corners[3 : 4] + corners[0 : 1] == [0,1]:
        face_vertices.append([m, e, f, j])
    else:
        face_vertices.append([i, e, f, j])

    mesh = Mesh.from_vertices_and_faces(vertices, face_vertices)

    mesh.cull_vertices()
    
    return mesh

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas

    combinations = [[0,0,0,0], [1,0,0,0], [0,1,0,0], [0,0,1,0], [0,0,0,1], [1,1,0,0], [1,0,1,0], [1,0,0,1], [0,1,1,0], [0,1,0,1], [0,0,1,1], [1,1,1,0], [1,1,0,1], [1,0,1,1], [0,1,1,1], [1,1,1,1]]

    for i, combination in enumerate(combinations):
        mesh = template(combination)
        print mesh

