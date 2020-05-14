from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

try:
	import rhinoscriptsyntax as rs
except ImportError:
	import compas
	compas.raise_if_ironpython()

from copy import deepcopy

from singular.datastructures import QuadMesh, CoarseQuadMesh, CoarsePseudoQuadMesh

from singular.algorithms import surface_discrete_mapping, boundary_triangulation, SkeletonDecomposition

from singular.datastructures.mesh_quad.grammar.add_strip import add_strips
from singular.datastructures.mesh_quad.grammar.delete_strip import delete_strips

from singular.datastructures import mesh_move_vertices_by
from singular.datastructures import constrained_smoothing

from compas.datastructures.mesh.conway import *

from singular.rhino import RhinoSurface
from compas_rhino.geometry import RhinoMesh
from compas_rhino.artists import MeshArtist

from Grasshopper.Kernel.Data import GH_Path
from Grasshopper import DataTree


__all__ = []


# ==============================================================================
# From/to Rhino
# ==============================================================================


def gh_from_rhino_mesh(mesh_guid, pole_point_guid):
	rhino_mesh = RhinoMesh.from_guid(mesh_guid)
	vertices, faces = rhino_mesh.vertices, rhino_mesh.faces
	# warning if ambiguous selection of poles
	return CoarseQuadMesh.from_vertices_and_faces_with_poles(vertices, faces, poles)


def gh_to_rhino_mesh(mesh):
	artist = MeshArtist(mesh)
	mesh_guid = artist.draw_mesh()
	return mesh_guid

def gh_from_rhino_lines(mesh, max):

    from compas.datastructures import Network
    from compas.datastructures import network_find_cycles
    network = Network.from_lines(lines, precision=precision)
    vertices = network.to_points()
    faces = [face_vertices for face_vertices in network_find_cycles(network) if len(face_vertices) <=4]
    mesh = CoarseQuadMesh.from_vertices_and_faces(vertices, faces)
    if delete_boundary_face:
        mesh.delete_face(0)
        mesh.cull_vertices()
    return mesh



# ==============================================================================
# Mesh data
# ==============================================================================


def gh_mesh_vertices(mesh):
	return [rs.AddPoint(mesh.vertex_coordinates(vkey)) for vkey in mesh.vertices()]


def gh_mesh_faces(mesh):
	key_to_index = mesh.key_index()
	face_vertices = DataTree[object]()
	face_polylines = DataTree[object]()
	for fkey in mesh.faces():
		path = GH_Path(fkey)
		face_vertices.AddRange([key_to_index[vkey] for vkey in mesh.face_vertices(fkey)], path)
		face_coordinates = mesh.face_coordinates(fkey)
		face_polylines.Add(rs.AddPolyline(face_coordinates + face_coordinates[:1]), path)
	return face_vertices


def gh_mesh_edges(mesh):
	key_to_index = mesh.key_index()
	edge_vertices = DataTree[object]()
	edge_lines = DataTree[object]()
	for i, (u, v) in enumerate(mesh.edges()):
		path = GH_Path(i)
		edge_vertices.AddRange([key_to_index[vkey] for vkey in (u, v)], path)
		edge_lines.Add(rs.AddLine(mesh.vertex_coordinates(u), mesh.vertex_coordinates(v)), path)
	return edge_vertices


def gh_mesh_is_element_on_boundary(mesh):
	vertex_on_boundary = [mesh.is_vertex_on_boundary(vkey) for vkey in mesh.vertices()]
	face_on_boundary = [mesh.is_face_on_boundary(fkey) for fkey in mesh.faces()]
	edge_on_boundary = [mesh.is_edge_on_boundary(u, v) for u, v in mesh.edges()]
	return vertex_on_boundary, face_on_boundary, edge_on_boundary

def gh_mesh_normals(mesh):
	vertex_normals = [mesh.vertex_normals(vkey) for vkey in mesh.vertices()]
	face_normals = [mesh.face_normals(fkey) for fkey in mesh.faces()]
	return vertex_normals, face_normals


# ==============================================================================
# Quad mesh data
# ==============================================================================


def gh_quad_mesh_singularities(quad_mesh):
	key_to_index = quad_mesh.key_index()
	singularity_indices = [key_to_index[vkey] for vkey in quad_mesh.singularities()]
	singularity_coordinates = [quad_mesh.vertex_coordinates(vkey) for vkey in quad_mesh.singularities()]
	return singularity_indices, singularity_coordinates


def gh_quad_mesh_strips(quad_mesh):
	quad_mesh.collect_strips()
	key_to_index = quad_mesh.key_index()
	strip_edges = DataTree[object]()
	strip_lines = DataTree[object]()
	strip_closed = DataTree[object]()
	for skey, edges in quad_mesh.strips(data=True):
		for i, (u, v) in enumerate(edges):
			path = GH_Path(skey, i)
			strip_edges.AddRange([key_to_index[vkey] for vkey in (u, v)], path)
			strip_lines.Add(rs.AddLine(mesh.vertex_coordinates(u), mesh.vertex_coordinates(v)), path)
		path = GH_Path(skey)
		strip_closed.Add(quad_mesh.is_strip_closed(skey), path)
	return strip_edges, strip_lines, strip_closed


def gh_quad_mesh_polyedges(quad_mesh):
	quad_mesh.collect_polyedges()
	key_to_index = quad_mesh.key_index()
	polyedge_vertices = DataTree[object]()
	polyedge_polyline = DataTree[object]()
	polyedge_closed = DataTree[object]()
	for pkey, polyedge in quad_mesh.polyedges(data=True):
		path = GH_Path(pkey)
		polyedge_vertices.AddRange([key_to_index[vkey] for vkey in polyedge], path)
		polyedge_polyline.Add(rs.AddPolyline([quad_mesh.vertex_coordinates(vkey) for vkey in polyedge]), path)
		polyedge_closed.Add(quad_mesh.is_polyedge_closed(pkey), path)
	return polyedge_vertices, polyedge_closed


def gh_store_quad_mesh_strips(quad_mesh):
	quad_mesh.collect_strips()
	return quad_mesh


def gh_store_quad_mesh_edge_polyedge(quad_mesh, u, v):
	polyedge = quad_mesh.collect_polyedge(u, v)
	polyline = rs.AddPolyline([quad_mesh.vertex_coordinates(vkey) for vkey in polyedge])
	return polyedge, polyline

def gh_get_quad_mesh_edge_strip(quad_mesh, u, v):
	strip_edges = DataTree[object]()
	strip_lines = DataTree[object]()
	for i, (w, x) in enumerate(quad_mesh.collect_strip(u, v)):
		path = GH_Path(i)
		strip_edges.AddRange([w, x], path)
		strip_lines.Add(rs.AddLine(quad_mesh.vertex_coordinates(w), quad_mesh.vertex_coordinates(x)))
	return strip_edges, strip_lines

# ==============================================================================
# Topology
# ==============================================================================


def gh_add_delete_strips(mesh, strips_to_add, strips_to_delete):
	index_to_key = {index: key for index, key in enumerate(mesh.vertices())}
	strip_index_to_key = {index: key for index, key in enumerate(mesh.strips())}
	mesh_2 = deepcopy(mesh)
	strips_to_add_lists = [[key for key in polyedge] for polyedge in strips_to_add.Branches]
	add_strips(mesh_2, strips_to_add_lists)
	delete_strips(mesh_2, [strip_index_to_key[index] for index in strips_to_delete])
	return mesh_2


def gh_add_strips(mesh, strips_to_add):
	mesh_2 = deepcopy(mesh)
	strips_to_add_lists = [[key for key in polyedge] for polyedge in strips_to_add.Branches]
	add_strips(mesh_2, strips_to_add_lists)
	return mesh_2


def gh_delete_strips(mesh, strips_to_delete):
	index_to_key = {index: key for index, key in enumerate(mesh.vertices())}
	strip_index_to_key = {index: key for index, key in enumerate(mesh.strips())}
	mesh_2 = deepcopy(mesh)
	delete_strips(mesh_2, [strip_index_to_key[index] for index in strips_to_delete])
	return mesh_2
	

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


# ==============================================================================
# Density
# ==============================================================================


def gh_coarsening(quad_mesh):
	return CoarseQuadMesh.from_quad_mesh(quad_mesh)


def gh_densifiying(coarse_quad_mesh, strips_subdivision):
	for skey, d in zip(coarse_quad_mesh.strips(), strips_subdivision):
		coarse_quad_mesh.set_strip_density(skey, d)
	coarse_quad_mesh.densification()
	return coarse_quad_mesh.get_quad_mesh()


# ==============================================================================
# Geometry
# ==============================================================================


def gh_move_vertices(mesh, vertex_indices, vectors):
	mesh_2 = deepcopy(mesh)
	index_to_key = {index: key for index, key in enumerate(mesh.vertices())}
	key_to_vector = {index_to_key[index]: vector for index, vector in zip(vertex_indices, vectors)}
	mesh_move_vertices_by(mesh_2, key_to_vector)
	return mesh_2


def gh_constrained_smoothing(mesh, k=10, damping=0.5, vertex_indices= [], guid_constraints=[]):
	mesh_2 = deepcopy(mesh)
	index_to_key = {index: key for index, key in enumerate(mesh.vertices())}
	vkey_to_guid_constraints = {index_to_key[index]: constraint for index, constraint in zip(vertex_indices, guid_constraints)}
	constrained_smoothing(mesh_2, k, damping, vkey_to_guid_constraints, algorithm='area')
	return mesh_2


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
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
