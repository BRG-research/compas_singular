import math

from compas.datastructures.mesh import Mesh

from compas.geometry import centroid_points

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
    'template',
]

def template(points = [ [0,0,0] , [1,0,0] , [1,1,0] , [0,1,0] ], types = ['False', 'False', 'False', 'False']):
    """Generate a template quad mesh based on four points with specific locations and types. type = 'True': singular ; type = 'False': regular.

    Parameters
    ----------
    points : list
        Four points.
    types: list
        Four types 'True' or 'False'.

    Returns
    -------
    vertices : list
        Vertices of the template quad mesh.
    faces_vertices : list
        Faces of the template quad mesh.

    Raises
    ------
    -

    """

    a, d, p, m = points
    b = list(centroid_points([a, a, a, d]))
    c = list(centroid_points([a, d, d, d]))
    h = list(centroid_points([d, d, d, p]))
    l = list(centroid_points([d, p, p, p]))
    o = list(centroid_points([p, p, p, m]))
    n = list(centroid_points([p, m, m, m]))
    i = list(centroid_points([m, m, m, a]))
    e = list(centroid_points([m, a, a, a]))
    f = list(centroid_points([e, e, e, h]))
    g = list(centroid_points([e, h, h, h]))
    j = list(centroid_points([i, i, i, l]))
    k = list(centroid_points([i, l, l, l]))

    vertices = [a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p]
    a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p = range(len(vertices))

    face_vertices = [[f, g, k, j]]

    if types[0] == 'True':
        face_vertices.append([a, b, f, e])
    if types[1] == 'True':
        face_vertices.append([c, d, h, g])
    if types[2] == 'True':
        face_vertices.append([k, l, p, o])
    if types[3] == 'True':
        face_vertices.append([i, j, n , m])

    if types[0 : 2] == ['False','False']:
        face_vertices.append([a, d, g, f])
    elif types[0 : 2] == ['True','False']:
        face_vertices.append([b, d, g, f])
    elif types[0 : 2] == ['False','True']:
        face_vertices.append([a, c, g, f])
    else:
        face_vertices.append([b, c, g, f])

    if types[1 : 3] == ['False','False']:
        face_vertices.append([d, p, k, g])
    elif types[1 : 3] == ['True','False']:
        face_vertices.append([h, p, k , g])
    elif types[1 : 3] == ['False','True']:
        face_vertices.append([d, l, k, g])
    else:
        face_vertices.append([h, l, k , g])

    if types[2 : 4] == ['False','False']:
        face_vertices.append([p, m, j, k])
    elif types[2 : 4] == ['True','False']:
        face_vertices.append([o, m, j, k])
    elif types[2 : 4] == ['False','True']:
        face_vertices.append([p, n, j, k])
    else:
        face_vertices.append([o, n, j, k])

    if types[3 : 4] + types[0 : 1] == ['False','False']:
        face_vertices.append([m, a, f, j])
    elif types[3 : 4] + types[0 : 1] == ['True','False']:
        face_vertices.append([i, a, f, j])
    elif types[3 : 4] + types[0 : 1] == ['False','True']:
        face_vertices.append([m, e, f, j])
    else:
        face_vertices.append([i, e, f, j])
    
    return vertices, face_vertices

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas

    vertices, faces = template()
    mesh = Mesh.from_vertices_and_faces(vertices, faces)

    print mesh
