import math

from compas_pattern.utilities.math import avrg
from compas_pattern.utilities.math import st_dev

import compas

try:
	import rhinoscriptsyntax as rs

except ImportError:
		compas.raise_if_ironpython()

from compas_pattern.datastructures.mesh_quad_coarse import CoarseQuadMesh
from compas_pattern.datastructures.mesh_quad import QuadMesh

from compas_pattern.cad.rhino.artist import select_mesh_strip
from compas_pattern.cad.rhino.artist import select_mesh_strips
from compas_pattern.cad.rhino.artist import select_mesh_polyedge

from compas_pattern.topology.grammar import add_strip
from compas_pattern.topology.grammar import delete_strips
from compas_pattern.topology.grammar import split_strip
from compas_pattern.topology.grammar import strips_to_split_to_preserve_boundaries_before_deleting_strips

from compas.topology import *

from compas_pattern.algorithms.skeletonisation import surface_skeleton_decomposition_mesh
from compas_pattern.algorithms.smoothing import constrained_smoothing

from compas_rhino.helpers import mesh_draw_edges
from compas_rhino.helpers import mesh_select_edges
from compas_pattern.cad.rhino.utilities import draw_mesh

from compas.geometry import Polyline

from compas_rhino.geometry import RhinoPoint
from compas_pattern.cad.rhino.objects.curve import RhinoCurve
from compas_pattern.cad.rhino.objects.surface import RhinoSurface
from compas_rhino.geometry import RhinoMesh

from compas_pattern.cad.rhino.smoothing_constraints import automated_smoothing_surface_constraints
from compas_pattern.cad.rhino.smoothing_constraints import automated_smoothing_constraints
from compas_pattern.cad.rhino.smoothing_constraints import customized_smoothing_constraints
from compas_pattern.cad.rhino.smoothing_constraints import display_smoothing_constraints

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
	'explore_pattern',
	'editing_topology',
	'editing_density'
	'editing_symmetry',
	'editing_geometry_smoothing',
	'evaluate_pattern'
]

def explore_pattern():
	"""Explore a pattern, its topology (singularities, densities and symmetries) and its geoemtry (via smoothing).

	"""

	pattern_from = rs.GetString('pattern from?', strings = ['coarse_quad_mesh', 'quad_mesh', 'surface'])
	
	if pattern_from == 'coarse_quad_mesh':
		guid = rs.GetObject('get coarse quad mesh', filter = 32)
		coarse_quad_mesh = CoarseQuadMesh.from_vertices_and_faces(*RhinoMesh.from_guid(guid).get_vertices_and_faces())
		coarse_quad_mesh.init_strip_density()
		coarse_quad_mesh.quad_mesh = coarse_quad_mesh.copy()
		coarse_quad_mesh.polygonal_mesh = coarse_quad_mesh.copy()
	elif pattern_from == 'quad_mesh':
		guid = rs.GetObject('get quad mesh', filter = 32)
		coarse_quad_mesh = CoarseQuadMesh.from_quad_mesh(QuadMesh.from_vertices_and_faces(*RhinoMesh.from_guid(guid).get_vertices_and_faces()))
	elif pattern_from == 'surface':
		guid = rs.GetObject('get surface', filter = 8)
		coarse_quad_mesh = surface_skeleton_decomposition_mesh(guid, rs.GetReal('precision', number = 1.))
		coarse_quad_mesh.init_strip_density()
		coarse_quad_mesh.quad_mesh = coarse_quad_mesh.copy()
		coarse_quad_mesh.polygonal_mesh = coarse_quad_mesh.copy()
	else:
		return 0
	
	while True:

		edit = rs.GetString('edit pattern?', strings = ['topology', 'density', 'symmetry', 'geometry', 'evaluate', 'exit'])

		if type(guid) == list:
			rs.DeleteObjects(guid)
		else:
			rs.DeleteObject(guid)

		if edit is None or edit == 'exit':
			return draw_mesh(coarse_quad_mesh.polygonal_mesh)

		if edit == 'topology':
			editing_topology(coarse_quad_mesh)
			coarse_quad_mesh.densification()
			coarse_quad_mesh.polygonal_mesh = coarse_quad_mesh.quad_mesh.copy()

		elif edit == 'density':
			editing_density(coarse_quad_mesh)
			coarse_quad_mesh.polygonal_mesh = coarse_quad_mesh.quad_mesh.copy()

		elif edit == 'symmetry':
			editing_symmetry(coarse_quad_mesh)

		elif edit == 'geometry':
			editing_geometry_smoothing(coarse_quad_mesh)

		guid = draw_mesh(coarse_quad_mesh.polygonal_mesh)
		rs.EnableRedraw(True)
		rs.EnableRedraw(False)

		if edit == 'evaluate':
			evaluate_pattern(coarse_quad_mesh.polygonal_mesh)

def editing_topology(coarse_quad_mesh):
	"""Edit the topology of a pattern, i.e. its singularities, via its strips.

	Parameters
	----------
	coarse_quad_mesh : CoarseQuadMesh
		The pattern to edit.

	"""

	while True:

		# update drawing
		guid = draw_mesh(coarse_quad_mesh)
		rs.EnableRedraw(True)
		rs.EnableRedraw(False)

		# choose operation
		operation = rs.GetString('edit strip topology?', strings = ['add', 'delete', 'split', 'exit'])
		
		# stop if asked
		if operation is None or operation == 'exit':
			rs.DeleteObject(guid)
			break

		# apply operation
		if operation == 'add':
			skey = add_strip(coarse_quad_mesh, select_mesh_polyedge(coarse_quad_mesh))
			coarse_quad_mesh.set_strip_density(skey, 1)
		
		elif operation == 'delete':
			skeys = set(select_mesh_strips(coarse_quad_mesh))
			to_split = strips_to_split_to_preserve_boundaries_before_deleting_strips(coarse_quad_mesh, skeys)
			for skey, n in to_split.items():
				skey_1, skey_2 = split_strip(coarse_quad_mesh, skey)
				d = int(math.ceil(float(coarse_quad_mesh.get_strip_density(skey)) / 2.))
				coarse_quad_mesh.set_strip_density(skey_1, d)
				coarse_quad_mesh.set_strip_density(skey_2, d)
			delete_strips(coarse_quad_mesh, skeys)

		elif operation == 'split':
			skey = select_mesh_strip(coarse_quad_mesh)
			skey_1, skey_2 = split_strip(coarse_quad_mesh, skey)
			# update data
			d = int(math.ceil(float(coarse_quad_mesh.get_strip_density(skey)) / 2.))
			coarse_quad_mesh.set_strip_density(skey_1, d)
			coarse_quad_mesh.set_strip_density(skey_2, d)
		
		# delete drawing
		rs.DeleteObject(guid)

def editing_density(coarse_quad_mesh):
	"""Edit the density of a pattern via its strip densities.

	Parameters
	----------
	coarse_quad_mesh : CoarseQuadMesh
		The pattern to edit.

	"""

	while True:

		# update drawing
		guid = draw_mesh(coarse_quad_mesh.quad_mesh)
		rs.EnableRedraw(True)
		rs.EnableRedraw(False)

		# choose operation
		operation = rs.GetString('edit strip density?', strings = ['local_value', 'global_value', 'local_target', 'global_target', 'exit'])

		# stop if asked
		if operation is None or operation == 'exit':
			rs.DeleteObjects(guid)
			break
			
		# get operation parameters
		if 'local' in operation:
			skey = select_mesh_strip(coarse_quad_mesh, show_density = True)

		if 'value' in operation:
			d = rs.GetInteger('density value', number = 3, minimum = 1)
		elif 'target' in operation:
			t = rs.GetReal('density target', number = 1.)

		# apply operation
		if operation == 'local_value':
			coarse_quad_mesh.set_strip_density(skey, d)

		elif operation == 'global_value':
			coarse_quad_mesh.set_strips_density(d)

		elif operation == 'local_target':
			coarse_quad_mesh.set_strip_density_target(skey, t)

		elif operation == 'global_target':
			coarse_quad_mesh.set_strips_density_target(t)
		
		# update data
		coarse_quad_mesh.densification()

		# delete drawing
		rs.DeleteObjects(guid)

def editing_symmetry(coarse_quad_mesh):
	"""Edit the symmetry of a pattern via Conway operators.

	Parameters
	----------
	coarse_quad_mesh : CoarseQuadMesh
		The pattern to edit.

	"""

	conway_operators = {
		'conway_seed',
		'conway_dual',
		'conway_join',
		'conway_ambo',
		'conway_kis',
		'conway_needle',
		'conway_zip',
		'conway_truncate',
		'conway_ortho',
		'conway_expand',
		'conway_gyro',
		'conway_snub',
		'conway_meta',
		'conway_bevel'
	}
	
	conway = {operator[7 :]: operator for operator in conway_operators}

	while True:

		rs.EnableRedraw(False)
		guid = draw_mesh(coarse_quad_mesh.polygonal_mesh)
		rs.EnableRedraw(True)

		operator = rs.GetString('edit symmetry?', strings = conway.keys() + ['exit'])

		if operator is None or operator == 'exit':
			if type(guid) == list:
				rs.DeleteObjects(guid)
			else:
				rs.DeleteObject(guid)
			return coarse_quad_mesh.polygonal_mesh

		elif operator == 'seed':
			coarse_quad_mesh.polygonal_mesh = coarse_quad_mesh.quad_mesh.copy()

		elif operator in conway and conway[operator] in globals() and str(conway[operator])[: 6] == 'conway':
			coarse_quad_mesh.polygonal_mesh = globals()[conway[operator]](coarse_quad_mesh.polygonal_mesh)

		if type(guid) == list:
			rs.DeleteObjects(guid)
		else:
			rs.DeleteObject(guid)

def editing_geometry_smoothing(coarse_quad_mesh):
	"""Edit the geometry of a pattern with smoothing.

	Parameters
	----------
	coarse_quad_mesh : CoarseQuadMesh
		The pattern to edit.

	"""

	mesh_to_smooth = rs.GetString('mesh to smooth?', strings = ['polygonal_mesh', 'quad_mesh'])
	if mesh_to_smooth == 'polygonal_mesh':
		mesh = coarse_quad_mesh.polygonal_mesh
	elif mesh_to_smooth == 'quad_mesh':
		mesh = coarse_quad_mesh.quad_mesh

	settings = {'iterations': 50, 'damping': .5, 'constraints': {}}

	while True:

		rs.EnableRedraw(False)
		guid = draw_mesh(mesh)
		rs.EnableRedraw(True)

		operation = rs.GetString('edit smoothing settings?', strings = ['smooth', 'iterations', 'damping', 'constraints', 'exit'])

		if operation is None or operation == 'exit':
			if type(guid) == list:
				rs.DeleteObjects(guid)
			else:
				rs.DeleteObject(guid)
			break

		elif operation == 'iterations':
			settings[operation] = rs.GetInteger('iterations', number = settings[operation], minimum = 0)

		elif operation == 'damping':
			settings[operation] = rs.GetReal('damping', number = settings[operation], minimum = 0., maximum = 1.)

		elif operation == 'constraints':
			count = 100
			while count:
				count -= 1
				guids = display_smoothing_constraints(mesh, settings[operation])
				constraint_type = rs.GetString('type of constraints?', strings = ['surface', 'automated', 'customised', 'reset', 'exit'])
				rs.DeleteObjects(guids)
				if constraint_type == 'surface':
					settings[operation] = automated_smoothing_surface_constraints(mesh, RhinoSurface(rs.GetObject('surface constraints', filter = 8)))
				elif constraint_type == 'automated':
					object_constraints = rs.GetObjects('object constraints')
					point_constraints = [obj for obj in object_constraints if rs.ObjectType(obj) == 1]
					curve_constraints = [RhinoCurve(obj) for obj in object_constraints if rs.ObjectType(obj) == 4]
					surface_constraint = [RhinoSurface(obj) for obj in object_constraints if rs.ObjectType(obj) == 8]
					if len(surface_constraint) > 1:
						print 'More than one surface constraint! Only the first one is taken into account.'
					if len(surface_constraint) == 0:
						surface_constraint = None
					else:
						surface_constraint = surface_constraint[0]
					settings[operation] = automated_smoothing_constraints(mesh, point_constraints, curve_constraints, surface_constraint)
				elif constraint_type == 'customised':
					settings[operation] = customized_smoothing_constraints(mesh, settings[operation])
				elif constraint_type == 'reset':
					settings[operation] = {}
				else:
					break
				
		elif operation == 'smooth':
			constrained_smoothing(mesh, kmax = settings['iterations'], damping = settings['damping'], constraints = settings['constraints'], algorithm = 'area')

		if type(guid) == list:
			rs.DeleteObjects(guid)
		else:
			rs.DeleteObject(guid)

def evaluate_pattern(mesh):
	"""Evaluate the properties of a mesh.

	Parameters
	----------
	mesh : Mesh
		The mesh to evaluate.

	"""

	while True:

		metric_type = rs.GetString('evaluate pattern property?', strings = ['topology', 'geometry', 'exit'])

		if metric_type is None or metric_type == 'exit':
			break

		if metric_type == 'topology':
			metric = rs.GetString('evaluate topological property?', strings = ['euler', 'genus', 'boundaries'])
			if metric == 'euler':
				print 'euler: ', mesh.euler()
			elif metric == 'genus':
				print 'genus: ', mesh.genus()
			elif metric == 'boundaries':
				print 'boundaries: ', len(mesh.boundaries())

		elif metric_type == 'geometry':
			metric = rs.GetString('evaluate geometrical property?', strings = ['edge_length', 'face_area', 'face_aspect_ratio', 'face_skewness', 'face_curvature', 'vertex_curvature'])

			aspect = rs.GetString('evaluate geometrical property?', strings = ['all', 'min', 'max', 'average', 'standard_deviation', 'specific'])

			if metric == 'edge_length':
				if aspect == 'specific':
					guids = mesh_draw_edges(mesh)
					edges = mesh_select_edges(mesh)
					rs.DeleteObjects(guids)
					print [mesh.edge_length(*edge) for edge in edges]
				else:
					edge_lengths = [mesh.edge_length(*edge) for edge in mesh.edges()]
					if aspect == 'all':
						print edge_lengths
					elif aspect == 'min':
						print min(edge_lengths)
					elif aspect == 'max':
						print max(edge_lengths)
					elif aspect == 'average':
						print avrg(edge_lengths)
					elif aspect == 'standard_deviation':
						print st_dev(edge_lengths)
				
# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
