from compas.datastructures.mesh import Mesh

from compas.geometry import circle_from_points

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
    'face_circle',
]

def face_circle(mesh, fkey):
    """Construct a circle from a triangle face.

    Parameters
    ----------
    mesh : Mesh
        A mesh.

    fkey: str
        Key of a triangle face.

    Returns
    -------
    circle: tuple or None
        Center, radius, normal of the circle.
        None if not triangle face.

    Raises
    ------
    -

    """

    face_vertices = mesh.face_vertices(fkey)
    if len(face_vertices) != 3:
        return None
    
    a, b, c = face_vertices
    a = mesh.vertex_coordinates(a)
    b = mesh.vertex_coordinates(b)
    c = mesh.vertex_coordinates(c)

    center, radius, normal = circle_from_points(a, b, c)
    return center, radius, normal


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    vertices = [[0,0,0], [1,0,0], [0,1,0]]
    face_vertices = [[0,1,2]]
    mesh = Mesh.from_vertices_and_faces(vertices, face_vertices)

    for fkey in mesh.faces():
        print face_circle(mesh, fkey)