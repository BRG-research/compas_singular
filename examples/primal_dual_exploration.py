from math import pi

import rhinoscriptsyntax as rs

import compas_rhino as rhino

from compas.datastructures.mesh import Mesh

from compas_pattern.cad.rhino.utilities import draw_mesh
from compas_pattern.datastructures.mesh import mesh_centroid
from compas_pattern.datastructures.mesh import mesh_normal

from compas.topology import mesh_dual

from compas_pattern.cad.rhino.editing_artist import apply_rule
from compas_pattern.topology.global_propagation import mesh_propagation

from compas_pattern.algorithms.densification import densification

from compas_pattern.algorithms.patterning import patterning

from compas.geometry import centroid_points
from compas.geometry import rotate_points

from compas.geometry import distance_point_point

from compas.geometry.algorithms.smoothing import mesh_smooth_centroid
from compas.geometry.algorithms.smoothing import mesh_smooth_area
from compas_pattern.algorithms.smoothing import define_constraints
from compas_pattern.algorithms.smoothing import apply_constraints

def editing_primal_dual(primal, default_settings, curve_constraints, point_constraints):
    
    dx = default_settings['dx']
    dy = default_settings['dy']
    density = default_settings['density']
    pattern = default_settings['pattern']
    smoothing_iterations = default_settings['smoothing iterations']
    smoothing_damping = default_settings['smoothing damping']
    
    # grammar rules + propagation scheme
    rules = ['settings', 'face_opening', 'flat_corner_2', 'flat_corner_3', 'flat_corner_33', 'split_35', 'split_35_diag', 'split_26', 'simple_split', 'double_split', 'singular_boundary_1', 'singular_boundary_2', 'clear_faces', 'move_vertices', 'stop']
    
    primal_guid = draw_mesh(primal)
    
    dense_primal = densification(primal, 1, custom = False)
    
    # smooth
    rs.EnableRedraw(False)
    constraints = {}
    for pt in point_constraints:
        vertex = None
        min_dist = -1
        for vkey in dense_primal.vertices_on_boundary():
            dist = distance_point_point(rs.PointCoordinates(pt), dense_primal.vertex_coordinates(vkey))
            if min_dist < 0 or min_dist > dist:
                vertex = vkey
                min_dist = dist
        constraints[vertex] = ('point', rs.PointCoordinates(pt))
    for vkey in dense_primal.vertices_on_boundary():
        if vkey not in constraints:
            curve = None
            min_dist = -1
            for crv in curve_constraints:
                vkey_guid = rs.AddPoint(dense_primal.vertex_coordinates(vkey))
                t = rs.CurveClosestPoint(crv, vkey_guid)
                pt = rs.EvaluateCurve(crv, t)
                dist = distance_point_point(pt, dense_primal.vertex_coordinates(vkey))
                rs.DeleteObject(vkey_guid)
                if min_dist < 0 or min_dist > dist:
                    curve = crv
                    min_dist = dist
            constraints[vkey] = ('curve', curve)
    rs.EnableRedraw(True)
    
    mesh_smooth_area(dense_primal, kmax = smoothing_iterations, damping = smoothing_damping, callback = apply_constraints, callback_args = [dense_primal, constraints])
    
    
    dense_primal_guid = draw_mesh(dense_primal)
    rs.MoveObject(dense_primal_guid, [dx,0,0])
    
    dense_dual = mesh_dual(dense_primal, Mesh)
    rotate_mesh(dense_dual, pi / 2)
    rs.EnableRedraw(False)
    dense_dual_guid = draw_mesh(dense_dual)
    rs.MoveObject(dense_dual_guid, [2*dx,0,0])
    rs.EnableRedraw(True)
    
    # start editing
    count = 1000
    while count > 0:
        count -= 1
        
        primal.update_default_edge_attributes()
        
        #ask for rule
        rule = rs.GetString('rule?', strings = rules)
        
        # exit
        if rule == 'stop':
            break
        
        elif rule == 'settings':
            density, pattern, dx, dy, smoothing_iterations, smoothing_damping = rs.PropertyListBox(['density', 'pattern', 'dx', 'dy', 'smoothing iterations', 'smoothing damping'], [density, pattern, dx, dy, smoothing_iterations, smoothing_damping], title = 'settings')
            density = float(density)
            dx = float(dx)
            dy = float(dy)
            smoothing_iterations = int(smoothing_iterations)
            smoothing_damping = float(smoothing_damping)
            
        # apply editing rule
        elif rule in rules:
            regular_vertices = list(primal.vertices())
            apply_rule(primal, rule)
            #if rule != 'clear_faces':
            mesh_propagation(primal, regular_vertices)
        
        rs.DeleteObjects(primal_guid)
        rs.DeleteObjects(dense_primal_guid)
        rs.DeleteObjects(dense_dual_guid)
        
        primal_guid = draw_mesh(primal)
        
        for fkey in primal.faces():
            if len(primal.face_vertices(fkey)) != 4:
                rs.AddPoint(primal.face_centroid(fkey))
                
        dense_primal = densification(primal, density, custom = False)
        dense_primal = dense_primal.to_mesh()
        dense_primal = patterning(dense_primal, pattern)
        to_del = [vkey for vkey in dense_primal.vertices() if len(dense_primal.vertex_neighbours(vkey)) == 0]
        for vkey in to_del:
            del dense_primal.vertex[vkey]
        
        # smooth
        rs.EnableRedraw(False)
        constraints = {}
        for pt in point_constraints:
            vertex = None
            min_dist = -1
            for vkey in dense_primal.vertices_on_boundary():
                dist = distance_point_point(rs.PointCoordinates(pt), dense_primal.vertex_coordinates(vkey))
                if min_dist < 0 or min_dist > dist:
                    vertex = vkey
                    min_dist = dist
            constraints[vertex] = ('point', rs.PointCoordinates(pt))
        for vkey in dense_primal.vertices_on_boundary():
            if vkey not in constraints:
                curve = None
                min_dist = -1
                for crv in curve_constraints:
                    vkey_guid = rs.AddPoint(dense_primal.vertex_coordinates(vkey))
                    t = rs.CurveClosestPoint(crv, vkey_guid)
                    pt = rs.EvaluateCurve(crv, t)
                    dist = distance_point_point(pt, dense_primal.vertex_coordinates(vkey))
                    rs.DeleteObject(vkey_guid)
                    if min_dist < 0 or min_dist > dist:
                        curve = crv
                        min_dist = dist
                constraints[vkey] = ('curve', curve)
        rs.EnableRedraw(True)
        
        mesh_smooth_area(dense_primal, kmax = smoothing_iterations, damping = smoothing_damping, callback = apply_constraints, callback_args = [dense_primal, constraints])
        
        rs.EnableRedraw(False)
        dense_primal_guid = draw_mesh(dense_primal)
        rs.MoveObject(dense_primal_guid, [dx,0,0])
        rs.EnableRedraw(True)
        
        dense_dual = mesh_dual(dense_primal, Mesh)
        rotate_mesh(dense_dual, pi / 2)
        rs.EnableRedraw(False)
        dense_dual_guid = draw_mesh(dense_dual)
        rs.MoveObject(dense_dual_guid, [2*dx,0,0])
        rs.EnableRedraw(True)
            
    return primal, dense_primal, dense_dual

def rotate_mesh(mesh, angle):
    centroid = mesh_centroid(mesh)
    normal = mesh_normal(mesh)
    for vkey in mesh.vertices():
                xyz = rotate_points([mesh.vertex_coordinates(vkey)], normal, angle, centroid)
                x, y, z = xyz[0]
                attr = mesh.vertex[vkey]
                attr['x'] = x
                attr['y'] = y
                attr['z'] = z



default_settings = {'dx': 15, 'dy': 0, 'density': 1, 'pattern': 'seed', 'smoothing iterations': 20, 'smoothing damping': .5}

primal_guid = rs.GetObject('primal mesh', filter = 32)
primal = rhino.mesh_from_guid(Mesh, primal_guid)

curve_constraints = rs.GetObjects('curve constraits', filter = 4)
if curve_constraints is None:
    curve_constraints = []
point_constraints = rs.GetObjects('point constraints', filter = 1)
if point_constraints is None:
    point_constraints = []

rs.DeleteObjects(primal_guid)

editing_primal_dual(primal, default_settings, curve_constraints, point_constraints)
