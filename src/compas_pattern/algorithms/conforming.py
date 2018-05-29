from compas.datastructures.mesh import Mesh

from math import acos
from math import asin
from math import pi
from math import floor

from compas.utilities import geometric_key

from compas.geometry import subtract_vectors
from compas.geometry import normalize_vector
from compas.geometry import dot_vectors
from compas.geometry import cross_vectors
from compas.geometry import area_polygon
from compas.geometry import normal_polygon

from compas_pattern.geometry.utilities import polyline_point

from compas_pattern.topology.grammar import simple_split
from compas_pattern.topology.grammar import remove_tri

from compas_pattern.topology.global_propagation import face_propagation
from compas_pattern.topology.global_propagation import mesh_propagation

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


def conforming(patch_decomposition, delaunay_mesh, medial_branches, boundary_polylines, edges_to_polyline, feature_points = [], feature_polylines = []):
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



    # remove remaining tri faces that are not pseudo quads
    # loop over boundary vertices
    boundary_vertices = patch_decomposition.vertices_on_boundary()
    for vkey in boundary_vertices:
        vertex_faces = patch_decomposition.vertex_faces(vkey, ordered = True)
        vertex_neighbours = patch_decomposition.vertex_neighbours(vkey, ordered = True)
        for fkey in vertex_faces:
            # apply changes if there is an adjacent tri face (pseudo-quads are already transformed)
            if len(patch_decomposition.face_vertices(fkey)) == 3:
                # remove quad faces at each extremity
                tri_faces = vertex_faces[1 : -1]
                vertex_left = vertex_neighbours[-1]
                vertex_right = vertex_neighbours[0]
                new_vertices = []
                n = len(tri_faces)
                m = int(floor((n + 1) / 2))
                # add new vertices on the adjacent boundary edges depending on the number of triangles to modify
                vertices_left = [patch_decomposition.edge_point(vertex_left, vkey, t = .9 + float(i) / float(m) * .1) for i in range(m)]
                vertices_left = [patch_decomposition.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z}) for x, y, z in vertices_left]
                vertices_right = [patch_decomposition.edge_point(vertex_right, vkey, t = .9 + float(i) / float(m) * .1) for i in range(m)]
                vertices_right = [patch_decomposition.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z}) for x, y, z in vertices_right]
                vertex_centre = []
                # add existing vertex if there is an even number of triangles
                if n % 2 == 0:
                    vertex_centre = [vkey]
                vertices = vertices_right + vertex_centre + list(reversed(vertices_left))
                # modfiy the triangle face vertices
                for i, fkey in enumerate(tri_faces):
                    face_vertices = patch_decomposition.face_vertices(fkey)[:]
                    idx = face_vertices.index(vkey)
                    face_vertices.insert(idx, vertices[i + 1])
                    face_vertices.insert(idx, vertices[i])
                    del face_vertices[idx + 2 - len(face_vertices)]
                    patch_decomposition.delete_face(fkey)
                    patch_decomposition.add_face(face_vertices, fkey)
                # update quad face on the left
                fkey_left = vertex_faces[-1]
                face_vertices = patch_decomposition.face_vertices(fkey_left)[:]
                idx = face_vertices.index(vkey)
                face_vertices[idx] = vertices[-1]
                patch_decomposition.delete_face(fkey_left)
                patch_decomposition.add_face(face_vertices, fkey_left)
                # update quad face on the right
                fkey_right = vertex_faces[0]
                face_vertices = patch_decomposition.face_vertices(fkey_right)[:]
                idx = face_vertices.index(vkey)
                face_vertices[idx] = vertices[0]
                patch_decomposition.delete_face(fkey_right)
                patch_decomposition.add_face(face_vertices, fkey_right)
                break


    for key, item in edges_to_polyline.items():
        print key, item

    # subidive low quality faces using reference to initial edge polyline 
    faces = list(patch_decomposition.faces())
    while len(faces) > 0:
        fkey = faces.pop()
        # face values
        face_normal = patch_decomposition.face_normal(fkey)
        face_area = patch_decomposition.face_area(fkey)
        face_vertices = patch_decomposition.face_vertices(fkey)
        # collect initial polylines
        polylines = []
        for i in range(len(face_vertices)):
            # exception for pseudo-quads with poles
            if face_vertices[i - 1] != face_vertices[i]:
                print fkey, face_vertices[i - 1], face_vertices[i]
                polylines.append(edges_to_polyline[(face_vertices[i - 1], face_vertices[i])])
        # patch values
        polygon = []
        for polyline in polylines:
            polygon += polyline[: -1]
        patch_area = area_polygon(polygon)
        patch_normal = normal_polygon(polygon)
        signed_face_area = dot_vectors(face_normal, patch_normal) / abs(dot_vectors(face_normal, patch_normal)) * face_area
        # if degenerated face compared to patch, modify
        if signed_face_area < 0.1 * patch_area:
            print fkey
            for u, v in patch_decomposition.face_halfedges(fkey):
                # collect vertices
                if patch_decomposition.is_edge_on_boundary(u, v):
                    w = patch_decomposition.face_vertex_descendant(fkey, v)
                    x = patch_decomposition.face_vertex_descendant(fkey, w)
                    fkey_bis = patch_decomposition.halfedge[x][w]
                    if fkey_bis in faces:
                        faces.remove(fkey_bis)
                    z = patch_decomposition.face_vertex_descendant(fkey_bis, w)
                    y = patch_decomposition.face_vertex_descendant(fkey_bis, z)
                    # add new vertices on polylines
                    xa, ya, za = polyline_point(edges_to_polyline[(u, v)], t = .5, snap_to_point = True)
                    a = patch_decomposition.add_vertex(attr_dict = {'x': xa, 'y': ya, 'z': za})                
                    xb, yb, zb = polyline_point(edges_to_polyline[(w, x)], t = .5, snap_to_point = True)
                    b = patch_decomposition.add_vertex(attr_dict = {'x': xb, 'y': yb, 'z': zb})  
                    xc, yc, zc = polyline_point(edges_to_polyline[(z, y)], t = .5, snap_to_point = True)
                    c = patch_decomposition.add_vertex(attr_dict = {'x': xc, 'y': yc, 'z': zc})
                    # update edges to polylines
                    # uv -> ua + av (and flipped)
                    polyline_uv = edges_to_polyline[(u, v)]
                    del edges_to_polyline[(u, v)]
                    del edges_to_polyline[(v, u)]
                    idx_a = polyline_uv.index([xa, ya, za])
                    edges_to_polyline[(u, a)] = polyline_uv[: idx_a + 1]
                    edges_to_polyline[(a, u)] = list(reversed(polyline_uv[: idx_a + 1]))
                    edges_to_polyline[(a, v)] = polyline_uv[idx_a :]
                    edges_to_polyline[(v, a)] = list(reversed(polyline_uv[idx_a :]))
                    # wx -> wb + bx (and flipped)
                    polyline_wx = edges_to_polyline[(w, x)]
                    del edges_to_polyline[(w, x)]
                    del edges_to_polyline[(x, w)]
                    idx_b = polyline_wx.index([xb, yb, zb])
                    edges_to_polyline[(w, b)] = polyline_wx[: idx_b + 1]
                    edges_to_polyline[(b, w)] = list(reversed(polyline_wx[: idx_b + 1]))
                    edges_to_polyline[(b, x)] = polyline_wx[idx_b :]
                    edges_to_polyline[(x, b)] = list(reversed(polyline_wx[idx_b :]))
                    # zy -> zc + yc (and flipped)
                    polyline_zy = edges_to_polyline[(z, y)]
                    del edges_to_polyline[(z, y)]
                    del edges_to_polyline[(y, z)]
                    idx_c = polyline_zy.index([xc, yc, zc])
                    edges_to_polyline[(z, c)] = polyline_zy[: idx_c + 1]
                    edges_to_polyline[(c, z)] = list(reversed(polyline_zy[: idx_c + 1]))
                    edges_to_polyline[(c, y)] = polyline_zy[idx_c :]
                    edges_to_polyline[(y, c)] = list(reversed(polyline_zy[idx_c :]))
                    # + ab + bc (and flipped)
                    edges_to_polyline[(a, b)] = [patch_decomposition.vertex_coordinates(a), patch_decomposition.vertex_coordinates(b)]
                    edges_to_polyline[(b, a)] = [patch_decomposition.vertex_coordinates(b), patch_decomposition.vertex_coordinates(a)]
                    edges_to_polyline[(b, c)] = [patch_decomposition.vertex_coordinates(b), patch_decomposition.vertex_coordinates(c)]
                    edges_to_polyline[(c, b)] = [patch_decomposition.vertex_coordinates(c), patch_decomposition.vertex_coordinates(b)]
                    # delete faces
                    patch_decomposition.delete_face(fkey)
                    patch_decomposition.delete_face(fkey_bis)
                    # add new faces
                    face_1 = patch_decomposition.add_face([u, a, b, x])
                    face_2 = patch_decomposition.add_face([a, v, w, b])
                    face_3 = patch_decomposition.add_face([b, w, z, c])
                    face_4 = patch_decomposition.add_face([b, c, y, x])
                    faces += [face_1, face_2, face_3, face_4]
                    break

    return patch_decomposition







    # propagate across curve features
    if feature_polylines is not None:
        # store vertex keys on the polyline feature using the map of geometric keys
        feature_map = [geometric_key(vkey) for polyline in feature_polylines for vkey in polyline]
        vertices_on_feature = [vkey for vkey in patch_decomposition.vertices() if geometric_key(patch_decomposition.vertex_coordinates(vkey)) in feature_map]

        # dictionary mapping vertex geometric keys to vertex indices
        vertex_map = {geometric_key(patch_decomposition.vertex_coordinates(vkey)): vkey for vkey in patch_decomposition.vertices()}

        # list of edges on curve features
        polyline_keys = [[geometric_key(vkey) for vkey in polyline] for polyline in feature_polylines]
        feature_edges = []
        for u, v in patch_decomposition.edges():
            u_key = geometric_key(patch_decomposition.vertex_coordinates(u))
            v_key = geometric_key(patch_decomposition.vertex_coordinates(v))
            for polyline in polyline_keys:
                if u_key in polyline and v_key in polyline:
                    feature_edges.append((u, v))
                    break

        # store face keys along the polyline
        faces_along_feature = []
        for vkey in vertices_on_feature:
            for fkey in patch_decomposition.vertex_faces(vkey):
                if fkey not in faces_along_feature:
                    faces_along_feature.append(fkey)

        for fkey in faces_along_feature:
            # check if face has not been deleted in-between
            if fkey not in list(patch_decomposition.faces()):
                continue
            face_vertices = patch_decomposition.face_vertices(fkey)
            # check if not quad patch
            if len(face_vertices) > 4:
                print 'to split'
                for u, v in patch_decomposition.face_halfedges(fkey):
                    # check where to make the split
                    if u not in vertices_on_feature and v in vertices_on_feature:
                        vkey = patch_decomposition.face_vertex_descendant(fkey, v)
                        wkey = poly_poly_1(patch_decomposition, fkey, vkey)
                        faces_along_feature.append(patch_decomposition.halfedge[wkey][vkey])
                        # update feature_edges
                        b = patch_decomposition.face_vertex_descendant(patch_decomposition.halfedge[vkey][wkey], wkey)
                        c = patch_decomposition.face_vertex_ancestor(patch_decomposition.halfedge[wkey][vkey], wkey)
                        if (b, c) in feature_edges or (c, b) in feature_edges:
                            if (b, c) in feature_edges:
                                feature_edges.remove((b, c))
                            else:
                                feature_edges.remove((c, b))
                            feature_edges.append((b, wkey))
                            feature_edges.append((wkey, c))
                        # propagate until boundary or closed loop
                        count = patch_decomposition.number_of_faces()
                        while count > 0:
                            count -= 1
                            next_fkey = patch_decomposition.halfedge[vkey][wkey]
                            ukey = patch_decomposition.face_vertex_descendant(next_fkey, wkey)
                            if wkey in patch_decomposition.halfedge[ukey] and patch_decomposition.halfedge[ukey][wkey] is not None:
                                next_fkey = patch_decomposition.halfedge[ukey][wkey]
                                if len(patch_decomposition.face_vertices(next_fkey)) == 5:
                                    vkey = wkey
                                    old_neighbours = patch_decomposition.vertex_neighbours(vkey)
                                    #wkey = penta_quad_1(patch_decomposition, next_fkey, wkey)
                                    original_vertices = patch_decomposition.face_vertices(next_fkey)
                                    original_vertices.remove(vkey)
                                    face_propagation(patch_decomposition, next_fkey, original_vertices)
                                    new_neighbours = patch_decomposition.vertex_neighbours(vkey)
                                    for nbr in new_neighbours:
                                        if nbr not in old_neighbours:
                                            wkey = nbr
                                            break
                                    # update feature_edges
                                    b = patch_decomposition.face_vertex_descendant(patch_decomposition.halfedge[vkey][wkey], wkey)
                                    c = patch_decomposition.face_vertex_ancestor(patch_decomposition.halfedge[wkey][vkey], wkey)
                                    if (b, c) in feature_edges or (c, b) in feature_edges:
                                        if (b, c) in feature_edges:
                                            feature_edges.remove((b, c))
                                        else:
                                            feature_edges.remove((c, b))
                                        feature_edges.append((b, wkey))
                                        feature_edges.append((wkey, c))
                                    # add to faces along feature to check
                                    faces_along_feature.append(patch_decomposition.halfedge[vkey][wkey])
                                    faces_along_feature.append(patch_decomposition.halfedge[wkey][vkey])
                                    continue
                                elif len(patch_decomposition.face_vertices(next_fkey)) == 6:
                                    vkey = wkey
                                    face_vertices =  patch_decomposition.face_vertices(next_fkey)
                                    idx = face_vertices.index(vkey)
                                    wkey = face_vertices[idx - 3]
                                    #wkey = hexa_quad_1(patch_decomposition, next_fkey, wkey)
                                    original_vertices = patch_decomposition.face_vertices(next_fkey)
                                    original_vertices.remove(vkey)
                                    original_vertices.remove(wkey)
                                    face_propagation(patch_decomposition, next_fkey, original_vertices)
                                    # add to faces along feature to check
                                    faces_along_feature.append(patch_decomposition.halfedge[vkey][wkey])
                                    faces_along_feature.append(patch_decomposition.halfedge[wkey][vkey])
                                    break
                                #elif len(patch_decomposition.face_vertices(next_fkey)) == 4:
                                #        vkey = wkey
                                #        wkey = quad_tri_1(patch_decomposition, next_fkey, wkey)
                                #        # add to faces along feature to check
                                #        faces_along_feature.append(patch_decomposition.halfedge[vkey][wkey])
                                #        faces_along_feature.append(patch_decomposition.halfedge[wkey][vkey])
                                #        break
                            break


    # curves = medial_branches + boundary_polylines
    # #curve_map = {curve: (geometric_key(curve[0]), geometric_key(curve[-1])) for curve in curves}
    # #extremities = list(curve_map.items())
    # extremities = [(geometric_key(curve[0]), geometric_key(curve[-1])) for curve in curves]
    # print len(extremities)
    # initial_vertices = list(patch_decomposition.vertices())

    # # split degenerated faces
    # splits = []
    # for fkey in patch_decomposition.faces():
        # a, b, c, d = [patch_decomposition.vertex_coordinates(vkey) for vkey in patch_decomposition.face_vertices(fkey)]
        # ab = normalize_vector(subtract_vectors(b, a))
        # bc = normalize_vector(subtract_vectors(c, b))
        # cd = normalize_vector(subtract_vectors(d, c))
        # da = normalize_vector(subtract_vectors(a, d))
        # cross = cross_vectors(ab, cd)
        # print cross

        # length = (ab[0] ** 2 + ab[1] ** 2) ** .5
        # costheta = ab[0] / length
        # sintheta = ab[1] / length
        # if asin(sintheta) != 0 :
        #     ab_angle = asin(sintheta) / abs(asin(sintheta)) * acos(costheta)
        # else:
        #     ab_angle = acos(costheta)
        # if ab_angle < 0:
        #     ab_angle += 2 * pi

        # length = (cd[0] ** 2 + cd[1] ** 2) ** .5
        # costheta = cd[0] / length
        # sintheta = cd[1] / length
        # if asin(sintheta) != 0 :
        #     cd_angle = asin(sintheta) / abs(asin(sintheta)) * acos(costheta)
        # else:
        #     cd_angle = acos(costheta)
        # if cd_angle < 0:
        #     cd_angle += 2 * pi

        #print cd_angle - ab_angle

    #     split = False
    #     for u, v in patch_decomposition.face_halfedges(fkey):
    #         u_key = geometric_key(patch_decomposition.vertex_coordinates(u))
    #         v_key = geometric_key(patch_decomposition.vertex_coordinates(v))
    #         count = extremities.count((u_key, v_key)) + extremities.count((v_key, u_key))
    #         print count
    #         splits.append([fkey, [u, v]])
    #         split = True
    #         break
    #     if split:
    #         break
    # for fkey, edge in splits:
    #     simple_split(patch_decomposition, fkey, edge)

    # mesh_propagation(patch_decomposition, initial_vertices)

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
