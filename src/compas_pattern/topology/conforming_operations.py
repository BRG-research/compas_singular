from compas.datastructures.mesh import Mesh

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
    'triangle_to_quad',
]


def triangle_to_quad(mesh, fkey, vkey):
    """Convert a tri face in a quad face by duplicating a vertex on the boundary.

    Parameters
    ----------
    mesh : Mesh
        A mesh.

    fkey: int
        Key of the face to change.

    vkey: int
        Key of the vertex to duplicate.

    Returns
    -------
    mesh : Mesh, None
        The modified mesh.
        None if the face is not a tri or if the vertex is not on the boundary.

    Raises
    ------
    -

    """
    
    # return None if the face is not a tri or if the vertex is not on the boundary
    if len(mesh.face_vertices) != 3 or not mesh.is_vertex_on_boundary(vkey):
        return None

    # modify face and its neighbours




# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas

