import rhinoscriptsyntax as rs

import compas_rhino as rhino

from compas.datastructures.mesh import Mesh
from compas_pattern.datastructures.pseudo_quad_mesh import PseudoQuadMesh
from compas_pattern.datastructures.pseudo_quad_mesh import pqm_from_mesh

from compas_pattern.cad.rhino.utilities import draw_mesh

from compas_pattern.cad.rhino.discrete_planar_mapping import discrete_planar_mapping
from compas_pattern.algorithms.planar_polyline_boundaries_to_delaunay import planar_polyline_boundaries_to_delaunay

from compas_pattern.topology.patch_datastructure import patch_datastructure_old
from compas_pattern.algorithms.delaunay_medial_axis_patch_decomposition import delaunay_medial_axis_patch_decomposition
from compas_pattern.algorithms.conforming_initial_patch_decomposition import conforming_initial_patch_decomposition

from compas_pattern.algorithms.coarse_to_dense_mesh import quad_mesh_densification

from compas_pattern.topology.conway_operators import conway_dual
from compas_pattern.topology.conway_operators import conway_join
from compas_pattern.topology.conway_operators import conway_ambo
from compas_pattern.topology.conway_operators import conway_kis
from compas_pattern.topology.conway_operators import conway_needle
from compas_pattern.topology.conway_operators import conway_gyro

from compas.geometry.algorithms.smoothing import mesh_smooth_centroid
from compas.geometry.algorithms.smoothing import mesh_smooth_area
from compas_pattern.algorithms.constrained_smoothing import define_constraints
from compas_pattern.algorithms.constrained_smoothing import apply_constraints

def add_layer_structure():
    layers = ['shape_and_features', 'coarse_quad_mesh', 'quad_mesh', 'pattern_topology', 'pattern_geometry']
    
    for layer in layers:
        rs.AddLayer(layer)
        objects = rs.ObjectsByLayer(layer)
        rs.DeleteObjects(objects)
        rs.LayerVisible(layer, visible = False)
    
    rs.LayerVisible(layers[-1], visible = True)
    
    return 0

def start():
    
    # shape and features
    surface_guid = rs.GetObject('select surface', filter = 8)
    surface_guid = rs.CopyObject(surface_guid)
    rs.ObjectLayer(surface_guid, 'shape_and_features')
    curve_features_guids = rs.GetObjects('select curve features', filter = 4)
    if curve_features_guids is None:
        curve_features_guids = []
    curve_features_guids = rs.CopyObjects(curve_features_guids)
    rs.ObjectLayer(curve_features_guids, 'shape_and_features')
    point_features_guids = rs.GetObjects('select point features', filter = 1)
    if point_features_guids is None:
        point_features_guids = []
    point_features_guids = rs.CopyObjects(point_features_guids)
    rs.ObjectLayer(point_features_guids, 'shape_and_features')
    
    # quad patch decomposition
    discretisation = rs.GetReal('discretisation', number = 1)
    rs.EnableRedraw(False)
    
    planar_boundary_polyline, planar_hole_polylines, planar_polyline_features, planar_point_features = discrete_planar_mapping(discretisation, surface_guid, curve_features_guids = curve_features_guids, point_features_guids = point_features_guids)
    
    delaunay_mesh = planar_polyline_boundaries_to_delaunay(planar_boundary_polyline, holes = planar_hole_polylines, polyline_features = planar_polyline_features, point_features = planar_point_features)
    #draw_mesh(delaunay_mesh)
    
    medial_branches, boundary_polylines = delaunay_medial_axis_patch_decomposition(delaunay_mesh)
    patch_curves = medial_branches + boundary_polylines
    
    patch_decomposition = patch_datastructure_old(PseudoQuadMesh, boundary_polylines, medial_branches)
    
    coarse_quad_mesh = conforming_initial_patch_decomposition(patch_decomposition, planar_point_features = planar_point_features, planar_polyline_features = planar_polyline_features)
    
    for vkey in coarse_quad_mesh.vertices():
        u, v, w = coarse_quad_mesh.vertex_coordinates(vkey)
        x, y, z = rs.EvaluateSurface(surface_guid, u, v)
        attr = coarse_quad_mesh.vertex[vkey]
        attr['x'] = x
        attr['y'] = y
        attr['z'] = z
    
    coarse_quad_mesh_guid = draw_mesh(coarse_quad_mesh)
    rs.ObjectLayer(coarse_quad_mesh_guid, layer = 'coarse_quad_mesh')
    
    if not coarse_quad_mesh.is_quadmesh():
        print 'non quad patch decomposition'
        for fkey in coarse_quad_mesh.faces():
            fv = coarse_quad_mesh.face_vertices(fkey)
            if len(fv) != 4:
                print fv
        return
    
    # quad mesh
    rs.EnableRedraw(True)
    target_length = rs.GetReal('target length for densification', number = 1)
    
    poles = rs.GetObjects('pole points', filter = 1)
    rs.EnableRedraw(False)
    
    if poles is None:
        poles = []
    poles = [rs.PointCoordinates(pole) for pole in poles]
    
    vertices, face_vertices = pqm_from_mesh(coarse_quad_mesh, poles)
    
    coarse_quad_mesh = PseudoQuadMesh.from_vertices_and_faces(vertices, face_vertices)
    
    quad_mesh = quad_mesh_densification(coarse_quad_mesh, target_length)
    
    quad_mesh_guid = draw_mesh(quad_mesh)
    rs.ObjectLayer(quad_mesh_guid, layer = 'quad_mesh')
    
    # pattern topology
    rs.EnableRedraw(True)
    conway_rule = rs.GetString('pattern conversion? dual, join, ambo, kis, needle, gyro or nothing')
    rs.EnableRedraw(False)
    
    pattern_topology = quad_mesh.to_mesh()
    
    if conway_rule == 'dual':
        conway_dual(pattern_topology)
    elif conway_rule == 'join':
        conway_join(pattern_topology)
    elif conway_rule == 'ambo':
        conway_ambo(pattern_topology)
    elif conway_rule == 'kis':
        conway_kis(pattern_topology)
    elif conway_rule == 'needle':
        conway_needle(pattern_topology)
    elif conway_rule == 'gyro':
        orientation = rs.GetString('left or right?')
        conway_gyro(pattern_topology, orientation)
    
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
            if u_xyz != v_xyz:
                edges.append(rs.AddLine(u_xyz, v_xyz))
        rs.AddGroup('pattern_topology')
        rs.AddObjectsToGroup(edges, 'pattern_topology')
        rs.ObjectLayer(edges, layer = 'pattern_topology')
    
    #pattern geometry
    pattern_geometry = pattern_topology.copy()
    
    rs.EnableRedraw(True)
    smoothing_iterations = rs.GetInteger('number of iterations for smoothing', number = 20)
    damping_value = rs.GetReal('damping value for smoothing', number = .5)
    rs.EnableRedraw(False)
    
    constraints, surface_boundaries = define_constraints(pattern_geometry, surface_guid, curve_constraints = curve_features_guids, point_constraints = point_features_guids)
    fixed_vertices = [vkey for vkey, constraint in constraints.items() if constraint[0] == 'point']
    
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
            if u_xyz != v_xyz:
                edges.append(rs.AddLine(u_xyz, v_xyz))
        rs.AddGroup('pattern_geometry')
        rs.AddObjectsToGroup(edges, 'pattern_geometry')
        rs.ObjectLayer(edges, layer = 'pattern_geometry')
    
    rs.EnableRedraw(True)

add_layer_structure()
start()