from compas.datastructures.mesh import Mesh

from compas.topology import mesh_flip_cycles

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
    'tri_quad_to_quad_quad',
]


def tri_quad_to_quad_quad(mesh, fkey_tri, fkey_quad, vkey):
    """Convert a tri face adjacent to a quad face into two quad faces with same keys by adding a new vertex.
    Does not inherit attributes.
    
    [a, b, c] + [c, d, e, a] -> [a, b, c, f] + [c, d, e, f]

    Parameters
    ----------
    mesh : Mesh
        A mesh.
    fkey_tri: int
        Key of tri face.
    fkey_quad: int
        Key of quad face adjacent to tri face.
    vkey: int
        Key of vertex in adjacent to tri face and quad face.

    Returns
    -------
    mesh : Mesh, None
        The modified mesh.
        None if the tri face is not a tri, if the quad face is not a quad or if not adjacent to the tri face or if the vertex is not adjacent to both faces.

    Raises
    ------
    -

    """

    # check validity of rule
    if len(mesh.face_vertices(fkey_tri)) != 3:
        return None
    if len(mesh.face_vertices(fkey_quad)) != 4:
        return None
    if fkey_quad not in mesh.face_neighbours(fkey_tri):
        return None
    if vkey not in mesh.face_vertices(fkey_tri) or vkey not in mesh.face_vertices(fkey_quad):
        return None

    # flip cyles in faces dpeending on position of vkey
    flip = False
    u = vkey
    v = mesh.face_vertex_descendant(fkey_tri, u)
    if mesh.halfedge[v][u] == fkey_quad:
        flip = True
        mesh_flip_cycles(mesh)

    # itemise vertices
    a = vkey
    b = mesh.face_vertex_descendant(fkey_tri, a)
    c = mesh.face_vertex_descendant(fkey_tri, b)
    d = mesh.face_vertex_descendant(fkey_quad, c)
    e = mesh.face_vertex_descendant(fkey_quad, d)

    # create new vertex
    x, y, z = mesh.edge_midpoint(d, a)
    f = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})

    # delete old faces
    mesh.delete_face(fkey_tri)
    mesh.delete_face(fkey_quad)

    # create new faces
    mesh.add_face([a, b, c, f], fkey_tri)
    mesh.add_face([c, d, e, f], fkey_quad)

    # reflip cycles in faces
    if flip:
        mesh_flip_cycles(mesh)

    return 0




# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas

