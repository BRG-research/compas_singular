import rhinoscriptsyntax as rs

import compas_rhino as rhino

from compas.datastructures.mesh import Mesh

from compas_pattern.cad.rhino.utilities import draw_mesh

from compas_pattern.cad.rhino.spatial_NURBS_input_to_planar_discrete_output import spatial_NURBS_input_to_planar_discrete_output
from compas_pattern.algorithms.planar_polyline_boundaries_to_delaunay import planar_polyline_boundaries_to_delaunay
from compas_pattern.cad.rhino.spatial_NURBS_input_to_planar_discrete_output import mapping_point_to_surface

from compas_pattern.topology.patches_to_mesh import patches_to_mesh_old
from compas_pattern.algorithms.delaunay_medial_axis_patch_decomposition import delaunay_medial_axis_patch_decomposition
from compas_pattern.algorithms.conforming_initial_patch_decomposition import conforming_initial_patch_decomposition

from compas_pattern.algorithms.coarse_to_dense_mesh import quad_mesh_densification

from compas_pattern.topology.conway_operators import conway_dual
from compas_pattern.topology.conway_operators import conway_join
from compas_pattern.topology.conway_operators import conway_ambo
from compas_pattern.topology.conway_operators import conway_kis
from compas_pattern.topology.conway_operators import conway_needle

from compas.geometry.algorithms.smoothing import mesh_smooth_centroid
from compas.geometry.algorithms.smoothing import mesh_smooth_area
from compas_pattern.algorithms.constrained_smoothing import define_constraints
from compas_pattern.algorithms.constrained_smoothing import apply_constraints

def add_layer_structure():
    layers = ['shape_and_features', 'quad_patch_decomposition', 'quad_mesh', 'pattern_topology', 'pattern_geometry']
    
    for layer in layers:
        rs.AddLayer(layer)
        rs.LayerVisible(layer, visible = False)
    
    rs.LayerVisible(layers[-1], visible = True)
    
    return 0

def start():
    
    # shape and features
    surface_guid = rs.GetObject('select surface', filter = 8)
    rs.ObjectLayer(surface_guid, 'shape_and_features')
    curve_features_guids = rs.GetObjects('select curve features', filter = 4)
    if curve_features_guids is None:
        curve_features_guids = []
    rs.ObjectLayer(curve_features_guids, 'shape_and_features')
    point_features_guids = rs.GetObjects('select point features', filter = 1)
    if point_features_guids is None:
        point_features_guids = []
    rs.ObjectLayer(point_features_guids, 'shape_and_features')
    
    # quad patch decomposition
    discretisation = rs.GetReal('discretisation', number = 1)
    rs.EnableRedraw(False)
    
    planar_boundary_polyline, planar_hole_polylines, planar_polyline_features, planar_point_features = spatial_NURBS_input_to_planar_discrete_output(discretisation, surface_guid, curve_features_guids = curve_features_guids, point_features_guids = point_features_guids)
    
    delaunay_mesh = planar_polyline_boundaries_to_delaunay(planar_boundary_polyline, holes = planar_hole_polylines, polyline_features = planar_polyline_features, point_features = planar_point_features)
    
    medial_branches, boundary_polylines = delaunay_medial_axis_patch_decomposition(delaunay_mesh)
    
    patch_decomposition = patches_to_mesh_old(boundary_polylines, medial_branches)
    
    quad_patch_decomposition = conforming_initial_patch_decomposition(patch_decomposition, planar_point_features = planar_point_features, planar_polyline_features = planar_polyline_features)
    
    for vkey in quad_patch_decomposition.vertices():
        uv0 = quad_patch_decomposition.vertex_coordinates(vkey)
        x, y, z = mapping_point_to_surface(uv0, surface_guid)
        attr = quad_patch_decomposition.vertex[vkey]
        attr['x'] = x
        attr['y'] = y
        attr['z'] = z
    
    quad_patch_decomposition_guid = draw_mesh(quad_patch_decomposition)
    rs.ObjectLayer(quad_patch_decomposition_guid, layer = 'quad_patch_decomposition')
    
    if not quad_patch_decomposition.is_quadmesh():
        print 'non quad patch decomposition'
        return
    
    # quad mesh
    rs.EnableRedraw(True)
    target_length = rs.GetReal('target length for densification', number = 1)
    rs.EnableRedraw(False)
    
    quad_mesh = quad_mesh_densification(quad_patch_decomposition, target_length)
    
    quad_mesh_guid = draw_mesh(quad_mesh)
    rs.ObjectLayer(quad_mesh_guid, layer = 'quad_mesh')
    
    # pattern topology
    rs.EnableRedraw(True)
    conway_rule = rs.GetString('pattern conversion')
    rs.EnableRedraw(False)
    
    if conway_rule == 'dual':
        conway_dual(quad_mesh)
    elif conway_rule == 'join':
        conway_join(quad_mesh)
    elif conway_rule == 'ambo':
        conway_ambo(quad_mesh)
    elif conway_rule == 'kis':
        conway_kis(quad_mesh)
    elif conway_rule == 'needle':
        conway_needle(quad_mesh)
    
    pattern_topology = quad_mesh.copy()
    
    is_polygonal = False
    for fkey in pattern_topology.faces():
        if len(pattern_topology.face_vertices(fkey)) > 4:
            is_polygonal = True
    
    if not is_polygonal:
        pattern_topology_guid = draw_mesh(pattern_topology)
        rs.ObjectLayer(pattern_topology_guid, layer = 'pattern_topology')
    else:
        edges = []
        for u, v in pattern_topology.edges():
            u_xyz = pattern_topology.vertex_coordinates(u)
            v_xyz = pattern_topology.vertex_coordinates(v)
            edges.append(rs.AddLine(u_xyz, v_xyz))
        rs.AddGroup('pattern_topology')
        rs.AddObjectsToGroup(edges, 'pattern_topology')
    
    #pattern geometry
    pattern_geometry = pattern_topology.copy()
    
    rs.EnableRedraw(True)
    smoothing_iterations = rs.GetInteger('number of iterations for smoothing', number = 20)
    damping_value = rs.GetReal('damping value for smoothing', number = .5)
    rs.EnableRedraw(False)
    
    constraints, surface_boundaries = define_constraints(pattern_geometry, surface_guid, curve_constraints = curve_features_guids, point_constraints = point_features_guids)
    fixed_vertices = [vkey for vkey, constraint in constraints.items() if constraint[0] == 'surface_corner']
    mesh_smooth_area(pattern_geometry, fixed = fixed_vertices, kmax = smoothing_iterations, damping = damping_value, callback = apply_constraints, callback_args = [pattern_geometry, constraints])
    rs.DeleteObjects(surface_boundaries)
    
    if not is_polygonal:
        pattern_geometry_guid = draw_mesh(pattern_geometry)
        rs.ObjectLayer(pattern_geometry_guid, layer = 'pattern_geometry')
    else:
        edges = []
        for u, v in pattern_geometry.edges():
            u_xyz = pattern_geometry.vertex_coordinates(u)
            v_xyz = pattern_geometry.vertex_coordinates(v)
            edges.append(rs.AddLine(u_xyz, v_xyz))
        rs.AddGroup('pattern_geometry')
        rs.AddObjectsToGroup(edges, 'pattern_geometry')
    
    rs.EnableRedraw(True)

add_layer_structure()
start()