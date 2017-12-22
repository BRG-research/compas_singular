def start():
    
    import sys
    
    import rhinoscriptsyntax as rs
    
    import compas_rhino as rhino
    
    from compas.datastructures.mesh import Mesh
    
    # collect spatial shape: surface + features
    surface_guid = rs.GetObject('select surface', filter = 8)
    curve_features_guids = rs.GetObjects('select curve features', filter = 4)
    if curve_features_guids is None:
        curve_features_guids = []
    point_features_guids = rs.GetObjects('select point features', filter = 1)
    if point_features_guids is None:
        point_features_guids = []
    
    # parameterisation from spatial to planar
    from compas_pattern.cad.rhino.spatial_NURBS_input_to_planar_discrete_output import spatial_NURBS_input_to_planar_discrete_output
    
    discretisation = rs.GetReal('discretisation', number = 1)
    
    rs.EnableRedraw(False)
    output = spatial_NURBS_input_to_planar_discrete_output(discretisation, surface_guid, curve_features_guids = curve_features_guids, point_features_guids = point_features_guids)
    
    planar_boundary_polyline, planar_hole_polylines, planar_polyline_features, planar_point_features = output
    
    planar_boundary_polyline_guid = rs.AddPolyline(planar_boundary_polyline)
    rs.AddLayer('boundary_polyline_planar')
    guids = rs.ObjectsByLayer('boundary_polyline_planar')
    rs.DeleteObjects(guids)
    rs.ObjectLayer(planar_boundary_polyline_guid, layer = 'boundary_polyline_planar')
    
    planar_hole_polylines_guid = [rs.AddPolyline(hole) for hole in planar_hole_polylines]
    rs.AddLayer('hole_polyline_planar')
    guids = rs.ObjectsByLayer('hole_polyline_planar')
    rs.DeleteObjects(guids)
    rs.ObjectLayer(planar_hole_polylines_guid, layer = 'hole_polyline_planar')
    
    planar_polyline_features_guid = [rs.AddPolyline(feature) for feature in planar_polyline_features]
    rs.AddLayer('feature_polyline_planar')
    guids = rs.ObjectsByLayer('feature_polyline_planar')
    rs.DeleteObjects(guids)
    rs.ObjectLayer(planar_polyline_features_guid, layer = 'feature_polyline_planar')
    
    planar_point_features_guid = [rs.AddPoint(point) for point in planar_point_features]
    rs.AddLayer('feature_point_planar')
    guids = rs.ObjectsByLayer('feature_point_planar')
    rs.DeleteObjects(guids)
    rs.ObjectLayer(planar_point_features_guid, layer = 'feature_point_planar')
    
    rs.EnableRedraw(True)
    
    bool = rs.GetInteger(message = 'generate Delaunay mesh?', number = 1, minimum = 0, maximum = 1)
    if not bool:
        return
        
    rs.LayerVisible('boundary_polyline_planar', visible = False)
    rs.LayerVisible('hole_polyline_planar', visible = False)
    rs.LayerVisible('feature_polyline_planar', visible = False)
    rs.LayerVisible('feature_point_planar', visible = False)
    
    # generate specific Delaunay mesh from planar shape and features
    from compas_pattern.algorithms.planar_polyline_boundaries_to_delaunay import planar_polyline_boundaries_to_delaunay
    from compas_pattern.cad.rhino.spatial_NURBS_input_to_planar_discrete_output import mapping_point_to_surface
    
    rs.EnableRedraw(False)
    
    delaunay_mesh = planar_polyline_boundaries_to_delaunay(planar_boundary_polyline, holes = planar_hole_polylines, polyline_features = planar_polyline_features, point_features = planar_point_features)
    
    vertices = [delaunay_mesh.vertex_coordinates(vkey) for vkey in delaunay_mesh.vertices()]
    face_vertices = [delaunay_mesh.face_vertices(fkey) for fkey in delaunay_mesh.faces()]
    delaunay_mesh_guid = rhino.utilities.drawing.xdraw_mesh(vertices, face_vertices, None, None)
    rs.AddLayer('delaunay_mesh')
    guids = rs.ObjectsByLayer('delaunay_mesh')
    rs.DeleteObjects(guids)
    rs.ObjectLayer(delaunay_mesh_guid, layer = 'delaunay_mesh')
    
    rs.EnableRedraw(True)
    
    bool = rs.GetInteger(message = 'generate patch decomposition?', number = 1, minimum = 0, maximum = 1)
    if not bool:
        return
    
    rs.LayerVisible('delaunay_mesh', visible = False)
    
    # patch polylines from Delaunay mesh
    from compas_pattern.algorithms.delaunay_medial_axis_patch_decomposition import delaunay_medial_axis_patch_decomposition
    
    rs.EnableRedraw(False)
    
    medial_branches, boundary_polylines = delaunay_medial_axis_patch_decomposition(delaunay_mesh)
    patch_decomposition = medial_branches + boundary_polylines
    
    rs.AddLayer('patch_decomposition')
    guids = rs.ObjectsByLayer('patch_decomposition')
    rs.DeleteObjects(guids)
    rs.ObjectLayer(delaunay_mesh_guid, layer = 'delaunay_mesh')
    for vertices in patch_decomposition:
        guid = rs.AddPolyline(vertices)
        rs.ObjectLayer(guid, layer = 'patch_decomposition')
    
    rs.EnableRedraw(True)
    
    bool = rs.GetInteger(message = 'generate control mesh?', number = 1, minimum = 0, maximum = 1)
    if not bool:
        return
    
    rs.LayerVisible('patch_decomposition', visible = False)
    
    # conversion patch polylines to control mesh
    from compas_pattern.topology.patches_to_mesh import patches_to_mesh_old
    
    rs.EnableRedraw(False)
    
    mesh = patches_to_mesh_old(boundary_polylines, medial_branches)
    
    vertices = [mesh.vertex_coordinates(vkey) for vkey in mesh.vertices()]
    face_vertices = [mesh.face_vertices(fkey) for fkey in mesh.faces()]
    mesh_guid = rhino.utilities.drawing.xdraw_mesh(vertices, face_vertices, None, None)
    rs.AddLayer('control_mesh')
    guids = rs.ObjectsByLayer('control_mesh')
    rs.DeleteObjects(guids)
    rs.ObjectLayer(mesh_guid, layer = 'control_mesh')
    
    rs.EnableRedraw(True)
    
    bool = rs.GetInteger(message = 'generate quad patch decomposition?', number = 1, minimum = 0, maximum = 1)
    if not bool:
        return
    
    rs.LayerVisible('control_mesh', visible = False)
    
    # patch decomposition to valid quad patch decomposition with potential pseudo-quads
    from compas_pattern.algorithms.conforming_initial_patch_decomposition import conforming_initial_patch_decomposition
    
    rs.EnableRedraw(False)
    
    conform_mesh = conforming_initial_patch_decomposition(mesh, planar_polyline_features = planar_polyline_features)
    
    bool = rs.GetInteger(message = 'remap on surface?', number = 0, minimum = 0, maximum = 1)
    if bool:
        for vkey in conform_mesh.vertices():
            uv0 = conform_mesh.vertex_coordinates(vkey)
            x, y, z = mapping_point_to_surface(uv0, surface_guid)
            attr = conform_mesh.vertex[vkey]
            attr['x'] = x
            attr['y'] = y
            attr['z'] = z
    
    vertices = [conform_mesh.vertex_coordinates(vkey) for vkey in conform_mesh.vertices()]
    face_vertices = [conform_mesh.face_vertices(fkey) for fkey in conform_mesh.faces()]
    conform_mesh_guid = rhino.utilities.drawing.xdraw_mesh(vertices, face_vertices, None, None)
    edges = []
    #for u,v in conform_mesh.edges():
    #    edges.append(rs.AddLine(conform_mesh.vertex_coordinates(u), conform_mesh.vertex_coordinates(v)))
    rs.AddLayer('conform_mesh')
    guids = rs.ObjectsByLayer('conform_mesh')
    rs.DeleteObjects(guids)
    rs.ObjectLayer(conform_mesh_guid, layer = 'conform_mesh')
    #rs.ObjectLayer(edges, layer = 'conform_mesh')
    
    rs.EnableRedraw(True)
    
    bool = rs.GetInteger(message = 'go to next step?', number = 1, minimum = 0, maximum = 1)
    if not bool:
        return
     
    rs.LayerVisible('conform_mesh', visible = False)
    
    
    
    
    # possibility to apply grammar rules
    
    mesh = conform_mesh
    
    from compas_pattern.topology.grammar_rules import quad_to_two_quads_diagonal
    #for vkey in mesh.vertices_on_boundary():
    #    vertex_faces = mesh.vertex_faces(vkey)
    #    if len(vertex_faces) == 1:
    #        fkey = vertex_faces[0]
    #        quad_to_two_quads_diagonal(mesh, fkey, vkey)
    
    from compas_pattern.topology.grammar_rules import quad_to_two_quads
    from compas_pattern.topology.conforming_operations import penta_to_quads
    from compas_pattern.topology.conforming_operations import hexa_to_quads
    
    rs.EnableRedraw(False)
    
    artist = rhino.MeshArtist(mesh, layer='MeshArtist')
    artist.clear_layer()
    
    #artist.draw_vertexlabels()
    #artist.redraw()
    
    artist.draw_facelabels()
    artist.redraw()
    fkey = rhino.mesh_select_face(mesh, message = 'face to split')
    artist.clear_layer()
    artist.redraw()
    
    artist.draw_edgelabels()
    artist.redraw()
    ukey, vkey = rhino.mesh_select_edge(mesh, message = 'edge of the face along which to split')
    artist.clear_layer()
    artist.redraw()
    
    rs.EnableRedraw(False)
    
    e, f = quad_to_two_quads(mesh, fkey, ukey, vkey)
    fkey = mesh.halfedge[e][f]
    vkey = f
    count = mesh.number_of_faces()
    while count > 0:
        count -= 1
        ukey = mesh.face_vertex_descendant(fkey, vkey)
        if vkey in mesh.halfedge[ukey] and mesh.halfedge[ukey][vkey] is not None:
            fkey = mesh.halfedge[ukey][vkey]
            if len(mesh.face_vertices(fkey)) == 5:
                wkey = penta_to_quads(mesh, fkey, vkey)
                fkey = mesh.halfedge[vkey][wkey]
                vkey = wkey
                continue
            if len(mesh.face_vertices(fkey)) == 6:
                hexa_to_quads(mesh, fkey, vkey)
                break
        break
    fkey = mesh.halfedge[f][e]
    vkey = e
    count = mesh.number_of_faces()
    while count > 0:
        count -= 1
        ukey = mesh.face_vertex_descendant(fkey, vkey)
        if vkey in mesh.halfedge[ukey] and mesh.halfedge[ukey][vkey] is not None and len(mesh.face_vertices(mesh.halfedge[ukey][vkey])) != 4:
            fkey = mesh.halfedge[ukey][vkey]
            if len(mesh.face_vertices(fkey)) == 5:
                wkey = penta_to_quads(mesh, fkey, vkey)
                fkey = mesh.halfedge[vkey][wkey]
                vkey = wkey
                continue
            if len(mesh.face_vertices(fkey)) == 6:
                hexa_to_quads(mesh, fkey, vkey)
                break
        break
    
    vertices = [mesh.vertex_coordinates(vkey) for vkey in mesh.vertices()]
    face_vertices = [mesh.face_vertices(fkey) for fkey in mesh.faces()]
    mesh_guid = rhino.utilities.drawing.xdraw_mesh(vertices, face_vertices, None, None)
    rs.AddLayer('edited_mesh')
    rs.ObjectLayer(mesh_guid, layer = 'edited_mesh')
    
    
    rs.EnableRedraw(True)
    
    # mesh densification
    
    # mapping and smoothing on spatial shape
    
    # conversion to pattern

start()