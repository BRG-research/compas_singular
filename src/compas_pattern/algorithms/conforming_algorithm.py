from compas.datastructures.mesh import Mesh

from compas_pattern.topology.grammar_rules import tri_quad_to_quad_quad


__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
    'conforming_initial_patch_decomposition',
]

def conforming_initial_patch_decomposition(mesh):
    """Transform the initial patch decomposition in a valid quad patch decomposition. Potentially with pseudo-quads.
    1. Remove tri patches that sould not be pseudo-quad patches.

    Parameters
    ----------
    mesh : Mesh
        The mesh of the patch decomposition.

    Returns
    -------
    mesh: Mesh

    Raises
    ------
    -

    """

    boundary_vertices = mesh.vertices_on_boundary()
    count = mesh.number_of_faces()
    # as long as a conforming rule can be applied, try again
    while count > 0:
        count -= 1
        # look for a tri face adjacent to a quad face
        for fkey_tri in mesh.faces():
            if len(mesh.face_vertices(fkey_tri)) == 3:
                for c, a in mesh.face_halfedges(fkey_tri):
                    fkey_quad = mesh.halfedge[a][c]
                    if len(mesh.face_vertices(fkey_quad)) == 4:
                        b = mesh.face_vertex_descendant(fkey_tri, a)
                        d = mesh.face_vertex_descendant(fkey_quad, c)
                        e = mesh.face_vertex_descendant(fkey_quad, d)
                        # only two valid possibilities: a and e are the only ones on the boundary or c and d are the only ones on the boundary
                        if a in boundary_vertices and b not in boundary_vertices and c not in boundary_vertices and d not in boundary_vertices and e in boundary_vertices:
                            tri_quad_to_quad_quad(mesh, fkey_tri, fkey_quad, a)
                            continue
                        elif a not in boundary_vertices and b not in boundary_vertices and c in boundary_vertices and d in boundary_vertices and e not in boundary_vertices:
                            tri_quad_to_quad_quad(mesh, fkey_tri, fkey_quad, c)                              
                            continue
        break

    return mesh


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
