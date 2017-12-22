from compas.datastructures.mesh import Mesh

from compas.utilities import geometric_key

from compas_pattern.topology.grammar_rules import mix_quad_1
from compas_pattern.topology.grammar_rules import penta_quad_1
from compas_pattern.topology.grammar_rules import hexa_quad_1
from compas_pattern.topology.grammar_rules import poly_poly_1

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
    'conforming_initial_patch_decomposition',
]

def conforming_initial_patch_decomposition(mesh, planar_polyline_features = None):
    """Transform the initial patch decomposition in a valid quad patch decomposition. Potentially with pseudo-quads.
    1. Remove tri patches that sould not be pseudo-quad patches due to insufficient refinement.
    2. Propagate T-junctions from polyline features
    
    Parameters
    ----------
    mesh : Mesh
        The mesh of the patch decomposition.
    planar_polyline_features : list
        The planar polylines features as lists of vertices from which to propagate T-junctions.

    Returns
    -------
    mesh: Mesh

    Raises
    ------
    -

    """

    # 1.
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

    # 2.
    if planar_polyline_features is not None:
        # store vertex keys on the polyline feature using the map of geometric keys
        feature_map = [geometric_key(vkey) for polyline in planar_polyline_features for vkey in polyline]
        vertices_on_feature = [vkey for vkey in mesh.vertices() if geometric_key(mesh.vertex_coordinates(vkey)) in feature_map]

        # store face keys along the polyline
        faces_along_feature = []
        for vkey in vertices_on_feature:
            for fkey in mesh.vertex_faces(vkey):
                if fkey not in faces_along_feature:
                    faces_along_feature.append(fkey)

        for fkey in faces_along_feature:
            face_vertices = mesh.face_vertices(fkey)
            if len(face_vertices) > 4:
                for u, v in mesh.face_halfedges(fkey):
                    if u not in vertices_on_feature and v in vertices_on_feature:
                        vkey = mesh.face_vertex_descendant(fkey, v)
                        wkey = poly_poly_1(mesh, fkey, vkey)
                        faces_along_feature.append(mesh.halfedge[wkey][vkey])
                        # propagate until boundary or closed loop
                        count = mesh.number_of_faces()
                        while count > 0:
                            count -= 1
                            next_fkey = mesh.halfedge[vkey][wkey]
                            ukey = mesh.face_vertex_descendant(next_fkey, wkey)
                            if wkey in mesh.halfedge[ukey] and mesh.halfedge[ukey][wkey] is not None:
                                next_fkey = mesh.halfedge[ukey][wkey]
                                if len(mesh.face_vertices(next_fkey)) == 5:
                                    vkey = wkey
                                    wkey = penta_quad_1(mesh, next_fkey, wkey)
                                    continue
                                if len(mesh.face_vertices(next_fkey)) == 6:
                                    hexa_quad_1(mesh, next_fkey, wkey)
                                    break
                            break



    return mesh

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
