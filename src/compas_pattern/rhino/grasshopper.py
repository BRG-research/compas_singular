from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

try:
	import rhinoscriptsyntax as rs
except ImportError:
	import compas
	compas.raise_if_ironpython()

import copy

from compas_pattern.datastructures import CoarseQuadMesh
from compas_pattern.datastructures import QuadMesh

from compas_pattern.algorithms import surface_discrete_mapping
from compas_pattern.algorithms import boundary_triangulation
from compas_pattern.algorithms import SkeletonDecomposition

from compas_pattern.datastructures.mesh_quad.grammar.add_strip import add_strip
from compas_pattern.datastructures.mesh_quad.grammar.delete_strip import delete_strip

from compas_pattern.datastructures import automated_smoothing_surface_constraints
from compas_pattern.datastructures import automated_smoothing_constraints
from compas_pattern.datastructures import constrained_smoothing

from compas.datastructures.mesh.conway import *

from compas_pattern.rhino import RhinoSurface
from compas_rhino.geometry import RhinoMesh
from compas_rhino.artists import MeshArtist

from Grasshopper.Kernel.Data import GH_Path
from Grasshopper import DataTree


__all__ = []


# ==============================================================================
# Input/ouput
# ==============================================================================


def gh_from_rhino_mesh(mesh_guid):
	rhino_mesh = RhinoMesh.from_guid(mesh_guid)
	vertices, faces = rhino_mesh.vertices, rhino_mesh.faces
	mesh = CoarseQuadMesh.from_vertices_and_faces(vertices, faces)
	return mesh


def gh_to_rhino_mesh(mesh):
	artist = MeshArtist(mesh)
	mesh_guid = artist.draw_mesh()
	return mesh_guid


# ==============================================================================
# Core data
# ==============================================================================


def gh_vertices(mesh):
	return [rs.AddPoint(mesh.vertex_coordinates(vkey)) for vkey in mesh.vertices()]


def gh_faces(mesh):
	face_vertices = DataTree[object]()
	for fkey in mesh.faces():
		path = GH_Path(fkey)
		face_vertices.AddRange(mesh.face_vertices(fkey), path)
	return face_vertices


def gh_edges(mesh):
	edge_vertices = DataTree[object]()
	for i, edge in enumerate(mesh.edges()):
		path = GH_Path(i)
		edge_vertices.AddRange(edge, path)
	return edge_vertices


def gh_singularities(quad_mesh):
	return quad_mesh.singularities()


def gh_strips(quad_mesh):
	strip_edges = DataTree[object]()
	strip_closed = DataTree[object]()
	for skey, edges in quad_mesh.strips(data=True):
		for i, edge in enumerate(edges):
			path = GH_Path(skey, i)
			strip_edges.AddRange(edge, path)
		path = GH_Path(skey)
		strip_closed.Add(quad_mesh.is_strip_closed(skey), path)
	return strip_edges, strip_closed


def gh_polyedges(quad_mesh):
	polyedge_vertices = DataTree[object]()
	polyedge_closed = DataTree[object]()
	for pkey, polyedge in quad_mesh.polyedges(data=True):
		path = GH_Path(pkey)
		polyedge_vertices.AddRange(polyedge, path)
		polyedge_closed.Add(quad_mesh.is_polyedge_closed(pkey), path)
	return polyedge_vertices, polyedge_closed


# ==============================================================================
# Data collection
# ==============================================================================


def gh_store_strips(quad_mesh):
	quad_mesh.collect_strips()
	return quad_mesh


def gh_store_polyedges(quad_mesh):
	quad_mesh.collect_polyedges()
	return quad_mesh


# ==============================================================================
# Edit
# ==============================================================================


def gh_add_strip(mesh, polyedge_to_add):
	add_strip(mesh, polyedge_to_add)
	return mesh


def gh_delete_strip(mesh, strip_to_delete):
	delete_strip(mesh, strip_to_delete)
	return mesh
	

# ==============================================================================
# Density
# ==============================================================================


def gh_coarsening(quad_mesh):
	return CoarseQuadMesh.from_quad_mesh(quad_mesh)


def gh_densifiying(coarse_quad_mesh, strips_subdivision):
	# input as list of valeu sorted per strip key or dictionary with right key as path?
	for skey, d in zip(coarse_quad_mesh.strips(), strips_subdivision):
		coarse_quad_mesh.set_strip_density(skey, d)
	coarse_quad_mesh.densification()
	return coarse_quad_mesh.get_quad_mesh()


# ==============================================================================
# Geometry
# ==============================================================================


def gh_constrained_smoothing(mesh, k=10, damping=0.5, surface_constraint=None, point_constraints=[]):
	constraints = {}
	surface = RhinoSurface.from_guid(surface_constraint)
	constraints.update(automated_smoothing_surface_constraints(mesh, surface))
	constraints.update(automated_smoothing_constraints(mesh, points=point_constraints))
	constrained_smoothing(mesh, k, damping, constraints, algorithm='area')
	return mesh


# ==============================================================================
# Tessellation
# ==============================================================================


def gh_conway(mesh, operator):
	conway_operators = {
		'dual':     mesh_conway_dual,
		'join':     mesh_conway_join,
		'ambo':     mesh_conway_ambo,
		'kis':      mesh_conway_kis,
		'needle':   mesh_conway_needle,
		'zip':      mesh_conway_zip,
		'truncate': mesh_conway_truncate,
		'ortho':    mesh_conway_ortho,
		'expand':   mesh_conway_expand,
		'gyro':     mesh_conway_gyro,
		'snub':     mesh_conway_snub,
		'meta':     mesh_conway_meta,
		'bevel':    mesh_conway_bevel
		}
	if operator not in conway_operators:
		return mesh
	else:
		return conway_operators[operator](mesh)


# ==============================================================================
# Decomposition
# ==============================================================================


def gh_surface_decomposition(surface_guid, accuracy_value, point_guids, curve_guids):

	if point_guids == [None]:
		point_guids = []
	if curve_guids == [None]:
		curve_guids = []

	outer_boundary, inner_boundaries, polyline_features, point_features = surface_discrete_mapping(surface_guid, accuracy_value, crv_guids = curve_guids, pt_guids = point_guids)
	tri_mesh = boundary_triangulation(outer_boundary, inner_boundaries, polyline_features, point_features)
	decomposition = SkeletonDecomposition.from_mesh(tri_mesh)
	quad_mesh = decomposition.decomposition_mesh(point_features)
	RhinoSurface.from_guid(surface_guid).mesh_uv_to_xyz(quad_mesh)
	return quad_mesh


def gh_mesh_decomposition(quad_mesh):
	decomposition_polyedges = DataTree[object]()
	for i, polyedge in enumerate(quad_mesh.singularity_polyedge_decomposition()):
		path = GH_Path(i)
		decomposition_polyedges.AddRange(polyedge, path)
	return decomposition_polyedges


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
