import math

from compas.datastructures.mesh import Mesh

from compas.geometry import centroid_points

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
    'template_disc',
    'template_disc_advanced',
    'template_sphere',
    'template_torus',
]

def template_disc(X = 1, Y = 1):
    """Generate a template coarse quad mesh with the topology of a disc.

    Parameters
    ----------
    X : real
        Length along X-axis.
    Y : real
        Length along Y-axis.

    Returns
    -------
    vertices : list
        Vertices of the template coarse quad mesh for a disc.
    faces_vertices : list
        Faces of the template coarse quad mesh for a disc.


    """


    a = [0, 0, 0]
    b = [X, 0, 0]
    c = [X, Y, 0]
    d = [0, Y, 0]

    vertices = [a, b, c, d]

    faces = [[a, b, c, d] ]

    face_vertices = []
    for face in faces:
        to_add = [vertices.index(vertex) for vertex in face]
        face_vertices.append(to_add)

    return vertices, face_vertices

def template_disc_advanced(X = 1, Y = 1, singularities_at_corner = ['False', 'False', 'False', 'False']):
    """Generate an advanced template coarse quad mesh with the topology of a disc.

    Parameters
    ----------
    X : real
        Length along X-axis.
    Y : real
        Length along Y-axis.
    singularity_at_corner: list
        Position of the four singularities close to the corners as booleans.

    Returns
    -------
    vertices : list
        Vertices of the template quad mesh for a disc.
    faces_vertices : list
        Faces of the template quad mesh for a disc.

    """

    types = singularities_at_corner

    a = [0, 0, 0]
    d = [X, 0, 0]
    p = [X, Y, 0]
    m = [0, Y, 0]

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

def template_sphere(X = 1, Y = 1, Z = 1):
    """Generate a template coarse quad mesh with the topology of a sphere.

    Parameters
    ----------
    X : real
        Length along X-axis.
    Y : real
        Length along Y-axis.
    Z : real
        Length along Z-axis.

    Returns
    -------
    vertices : list
        Vertices of the template coarse quad mesh for a sphere.
    faces_vertices : list
        Faces of the template coarse quad mesh for a sphere.

    """


    a = [0, 0, 0]
    b = [X, 0, 0]
    c = [X, Y, 0]
    d = [0, Y, 0]
    e = [0, 0, Z]
    f = [X, 0, Z]
    g = [X, Y, Z]
    h = [0, Y, Z]

    vertices = [a, b, c, d, e, f, g, h]

    faces = [[a, b, f, e], [b, c, g, f], [c, d, h, g], [d, a, e, h], [e, f, g, h], [d, c, b, a] ]

    face_vertices = []
    for face in faces:
        to_add = [vertices.index(vertex) for vertex in face]
        face_vertices.append(to_add)

    return vertices, face_vertices

def template_torus(X = 1, Y = 1, Z = 1, R = .25):
    """Generate a template coarse quad mesh with the topology of a torus.

    Parameters
    ----------
    X : real
        Length along X-axis.
    Y : real
        Length along Y-axis.
    Z : real
        Length along Z-axis.
    R : real
        Radius of the handle.

    Returns
    -------
    vertices : list
        Vertices of the template coarse quad mesh for a torus.
    faces_vertices : list
        Faces of the template coarse quad mesh for a torus.

    """


    a = [0, 0, 0]
    b = [X, 0, 0]
    c = [X, Y, 0]
    d = [0, Y, 0]
    e = [0, 0, Z]
    f = [X, 0, Z]
    g = [X, Y, Z]
    h = [0, Y, Z]
    i = [R, R, 0]
    j = [X - R, R, 0]
    k = [X - R, Y - R, 0]
    l = [R, Y - R, 0]
    m = [R, R, Z]
    n = [X - R, R, Z]
    o = [X - R, Y - R, Z]
    p = [R, Y - R, Z]

    vertices = [a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p]

    faces = [[a, b, f, e], [b, c, g, f], [c, d, h, g], [d, a, e, h], [e, f, n, m], [f, g, o, n], [g, h, p, o], [h, e, m, p], [i, j, b, a], [j, k, c, b], [k, l, d, c], [l, i, a, d], [m, n, j, i], [n, o, k, j], [o, p, l, k], [p, m, i, l] ]

    face_vertices = []
    for face in faces:
        to_add = [vertices.index(vertex) for vertex in face]
        face_vertices.append(to_add)

    return vertices, face_vertices

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas

    vertices, faces = template_disc_advanced()
    mesh = Mesh.from_vertices_and_faces(vertices, faces)

    print mesh
