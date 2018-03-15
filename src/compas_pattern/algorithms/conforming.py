from compas.datastructures.mesh import Mesh

from compas.utilities import geometric_key

#from compas_pattern.topology.consistency import quad_tri_1
#from compas_pattern.topology.consistency import mix_quad_1
#from compas_pattern.topology.consistency import penta_quad_1
#from compas_pattern.topology.consistency import hexa_quad_1
#from compas_pattern.topology.consistency import poly_poly_1
#from compas_pattern.topology.consistency import quad_mix_1

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
    'conforming',
]


def conforming(patch_decomposition, delaunay_mesh, medial_branches, boundary_polylines, feature_points = [], feature_polylines = []):
    # convert tri faces [a, b, c] into quad faces [a, b, c, c]
    
    # collect pole locations
    poles = []
    poles += [geometric_key(pt) for pt in feature_points]
    for polyline in feature_polylines:
        poles += [geometric_key(polyline[0]), geometric_key(polyline[-1])]

    # modify tri faces into quad faces with a double vertex as pole point
    for fkey in patch_decomposition.faces():
        face_vertices = patch_decomposition.face_vertices(fkey)
        if len(face_vertices) == 3:
            # find pole location
            pole = None
            for vkey in face_vertices:
                geom_key = geometric_key(patch_decomposition.vertex_coordinates(vkey))
                if geom_key in poles:
                    pole = vkey
                    break
            # modify face
            if pole is not None:
                new_face_vertices = face_vertices[:]
                idx = new_face_vertices.index(vkey)
                new_face_vertices.insert(idx, vkey)
                patch_decomposition.delete_face(fkey)
                patch_decomposition.add_face(new_face_vertices, fkey)

    return patch_decomposition

def conforming_old(mesh, planar_point_features = None, planar_polyline_features = None):
    """Transform the initial patch decomposition in a valid quad patch decomposition. Potentially with pseudo-quads.
    1. Remove tri patches that sould not be pseudo-quad patches due to insufficient refinement.
    2. Propagate T-junctions from polyline features
    3. Ensure at least one tri patch at the non-boundary extremities of polyline features.
    4. Enforce an edge at concavities
    5. Convert tri patches into quad patches with double vertex at pole location [a, b, c] -> [a, a, b, c]
    
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

    if planar_polyline_features is not None:
        # store vertex keys on the polyline feature using the map of geometric keys
        feature_map = [geometric_key(vkey) for polyline in planar_polyline_features for vkey in polyline]
        vertices_on_feature = [vkey for vkey in mesh.vertices() if geometric_key(mesh.vertex_coordinates(vkey)) in feature_map]

        # dictionary mapping vertex geometric keys to vertex indices
        vertex_map = {geometric_key(mesh.vertex_coordinates(vkey)): vkey for vkey in mesh.vertices()}

        # list of edges on curve features
        polyline_keys = [[geometric_key(vkey) for vkey in polyline] for polyline in planar_polyline_features]
        feature_edges = []
        for u, v in mesh.edges():
            u_key = geometric_key(mesh.vertex_coordinates(u))
            v_key = geometric_key(mesh.vertex_coordinates(v))
            for polyline in polyline_keys:
                if u_key in polyline and v_key in polyline:
                    feature_edges.append((u, v))
                    break

        # 2.
        # store face keys along the polyline
        faces_along_feature = []
        for vkey in vertices_on_feature:
            for fkey in mesh.vertex_faces(vkey):
                if fkey not in faces_along_feature:
                    faces_along_feature.append(fkey)

        for fkey in faces_along_feature:
            # check if face has not been deleted in-between
            if fkey not in list(mesh.faces()):
                continue
            face_vertices = mesh.face_vertices(fkey)
            # check if not quad patch
            if len(face_vertices) > 4:
                for u, v in mesh.face_halfedges(fkey):
                    # check where to make the split
                    if u not in vertices_on_feature and v in vertices_on_feature:
                        vkey = mesh.face_vertex_descendant(fkey, v)
                        wkey = poly_poly_1(mesh, fkey, vkey)
                        faces_along_feature.append(mesh.halfedge[wkey][vkey])
                        # update feature_edges
                        b = mesh.face_vertex_descendant(mesh.halfedge[vkey][wkey], wkey)
                        c = mesh.face_vertex_ancestor(mesh.halfedge[wkey][vkey], wkey)
                        if (b, c) in feature_edges or (c, b) in feature_edges:
                            if (b, c) in feature_edges:
                                feature_edges.remove((b, c))
                            else:
                                feature_edges.remove((c, b))
                            feature_edges.append((b, wkey))
                            feature_edges.append((wkey, c))
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
                                    # update feature_edges
                                    b = mesh.face_vertex_descendant(mesh.halfedge[vkey][wkey], wkey)
                                    c = mesh.face_vertex_ancestor(mesh.halfedge[wkey][vkey], wkey)
                                    if (b, c) in feature_edges or (c, b) in feature_edges:
                                        if (b, c) in feature_edges:
                                            feature_edges.remove((b, c))
                                        else:
                                            feature_edges.remove((c, b))
                                        feature_edges.append((b, wkey))
                                        feature_edges.append((wkey, c))
                                    # add to faces along feature to check
                                    faces_along_feature.append(mesh.halfedge[vkey][wkey])
                                    faces_along_feature.append(mesh.halfedge[wkey][vkey])
                                    continue
                                elif len(mesh.face_vertices(next_fkey)) == 6:
                                    vkey = wkey
                                    wkey = hexa_quad_1(mesh, next_fkey, wkey)
                                    # add to faces along feature to check
                                    faces_along_feature.append(mesh.halfedge[vkey][wkey])
                                    faces_along_feature.append(mesh.halfedge[wkey][vkey])
                                    break
                                elif len(mesh.face_vertices(next_fkey)) == 4:
                                        vkey = wkey
                                        wkey = quad_tri_1(mesh, next_fkey, wkey)
                                        # add to faces along feature to check
                                        faces_along_feature.append(mesh.halfedge[vkey][wkey])
                                        faces_along_feature.append(mesh.halfedge[wkey][vkey])
                                        break
                            break

        # 3.
        vertex_map = {geometric_key(mesh.vertex_coordinates(vkey)): vkey for vkey in mesh.vertices()}
        for polyline in planar_polyline_features:
            for v in [polyline[0], polyline[-1]]:
                v = vertex_map[geometric_key(v)]
                if not mesh.is_vertex_on_boundary(v):
                    vertex_faces = mesh.vertex_faces(v)
                    is_pole = False
                    for fkey in vertex_faces:
                        if len(mesh.face_vertices(fkey)) == 3:
                            is_pole = True
                            break
                    if not is_pole:
                        nbrs = mesh.vertex_neighbours(v)
                        if len(nbrs) == 2:
                            if (v, nbrs[0]) or (nbrs[0], v) in feature_edges:
                                u = nbrs[0]
                            elif (v, nbrs[1]) or (nbrs[1], v) in feature_edges:
                                u = nbrs[1]
                            else:
                                u = None
                            fkey_1 = mesh.halfedge[u][v]
                            e1 = quad_mix_1(mesh, fkey_1, v, u)
                            fkey_2 = mesh.halfedge[v][u]
                            e2 = quad_mix_1(mesh, fkey_2, v, u)
                            # propagate until boundary or closed loop
                            vkey = v
                            is_loop = False
                            wkey = e1
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
                                        # update feature_edges
                                        b = mesh.face_vertex_descendant(mesh.halfedge[vkey][wkey], wkey)
                                        c = mesh.face_vertex_ancestor(mesh.halfedge[wkey][vkey], wkey)
                                        if (b, c) in feature_edges or (c, b) in feature_edges:
                                            if (b, c) in feature_edges:
                                                feature_edges.remove((b, c))
                                            else:
                                                feature_edges.remove((c, b))
                                            feature_edges.append((b, wkey))
                                            feature_edges.append((wkey, c))
                                        # add to faces along feature to check
                                        continue
                                    elif len(mesh.face_vertices(next_fkey)) == 6:
                                        vkey = wkey
                                        wkey = hexa_quad_1(mesh, next_fkey, wkey)
                                        if wkey == e2:
                                            is_loop = True
                                        break
                                    elif len(mesh.face_vertices(next_fkey)) == 4:
                                        vkey = wkey
                                        wkey = quad_tri_1(mesh, next_fkey, wkey)
                                        if wkey == e2:
                                            is_loop = True
                                        break
                                break
                            # if not loop, propaget in other direction
                            if not is_loop:
                                vkey = v
                                wkey = e2
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
                                            # add to faces along feature to check
                                            continue
                                        elif len(mesh.face_vertices(next_fkey)) == 6:
                                            vkey = wkey
                                            wkey = hexa_quad_1(mesh, next_fkey, wkey)
                                            if wkey == e2:
                                                is_loop = True
                                            break
                                        elif len(mesh.face_vertices(next_fkey)) == 4:
                                            quad_tri_1(mesh, next_fkey, wkey)
                                            break
                                    break

    # 4

    # 5
    # collect pole points
    poles = []
    if planar_point_features is not None:
        poles += [geometric_key(pt) for pt in planar_point_features]
    if planar_polyline_features is not None:
        for polyline in planar_polyline_features:
            poles += [geometric_key(polyline[0]), geometric_key(polyline[-1])]

    # modify tri faces into quad faces with a double vertex as pole point
    for fkey in mesh.faces():
        face_vertices = mesh.face_vertices(fkey)
        if len(face_vertices) == 3:
            # find pole location
            pole = None
            for vkey in face_vertices:
                geom_key = geometric_key(mesh.vertex_coordinates(vkey))
                if geom_key in poles:
                    pole = vkey
                    break
            # modify face
            if pole is not None:
                new_face_vertices = face_vertices[:]
                idx = new_face_vertices.index(vkey)
                new_face_vertices.insert(idx, vkey)
                mesh.delete_face(fkey)
                mesh.add_face(new_face_vertices, fkey)

    return mesh

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
