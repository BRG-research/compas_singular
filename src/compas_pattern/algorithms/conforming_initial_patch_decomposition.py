from compas.datastructures.mesh import Mesh

from compas_pattern.topology.grammar_rules import mix_quad_1
from compas_pattern.topology.grammar_rules import poly_poly_1

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
    2. Propagate T-junctions from curve features
    
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
    restart = True
    while count > 0 and restart:
        restart = False
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
                            mix_quad_1(mesh, fkey_tri, fkey_quad, a)
                            restart = True
                            break
                        elif a not in boundary_vertices and b not in boundary_vertices and c in boundary_vertices and d in boundary_vertices and e not in boundary_vertices:
                            mix_quad_1(mesh, fkey_tri, fkey_quad, c) 
                            restart = True                             
                            break
                if restart:
                    break


    # count = mesh.number_of_faces()
    # # as long as a conforming rule can be applied, try again
    # restart = True
    # while count > 0 and restart:
    #     restart = False
    #     count -= 1
    #     # look for penta, hexa or more faces with two consecutive vertices of valency higher than three
    #     for fkey in mesh.faces():
    #         if len(mesh.face_vertices(fkey)) > 3:
    #             face_vertices = mesh.face_vertices(fkey)
    #             b, c = None, None
    #             for i in range(len(face_vertices)):
    #                 u = face_vertices[i - 1]
    #                 v = face_vertices[i]
    #                 if len(mesh.vertex_neighbours(u)) != 3 and len(mesh.vertex_neighbours(v)) != 3:
    #                     b, c = u, v
    #                     d = mesh.face_vertex_descendant(fkey, c)
    #                     e = mesh.face_vertex_descendant(fkey, d)
    #                     print fkey
    #                     poly_poly_1(mesh, fkey, e)
    #                     restart = True
    #                     break
    #             if restart:
    #                 break

    return mesh

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
