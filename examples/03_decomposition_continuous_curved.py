from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.datastructures import Mesh
from compas.rpc import Proxy
from compas.utilities import geometric_key
from compas.utilities import linspace

import compas_rhino
from compas_rhino.artists import MeshArtist
from compas_rhino.geometry import RhinoPoint

from compas_singular.algorithms import SkeletonDecomposition
from compas_singular.algorithms import boundary_triangulation
from compas_singular.rhino import RhinoSurface
from compas_singular.rhino import RhinoCurve
from compas_singular.rhino import automated_smoothing_surface_constraints
from compas_singular.rhino import automated_smoothing_constraints
from compas_singular.rhino import constrained_smoothing

proxy = Proxy("compas.geometry")
delaunay = proxy.delaunay_from_points_numpy

# ==============================================================================
# Input
# ==============================================================================

# Get input data.
srf_guid = compas_rhino.select_surface("Select a surface to decompose.")
crv_guids = compas_rhino.select_curves("Select curves to include in the decomposition.")
pt_guids = compas_rhino.select_points("Select points to include in the decomposition.")

# Wrap the inputs.
surface = RhinoSurface.from_guid(srf_guid)
curves = [RhinoCurve.from_guid(guid) for guid in crv_guids]
points = [RhinoPoint.from_guid(guid) for guid in pt_guids]

# Compute the feature discretisation length.
box = compas_rhino.rs.BoundingBox([srf_guid])
diagonal = compas_rhino.rs.Distance(box[0], box[6])
D = 0.01 * diagonal

# Get the target length for the final quad mesh.
L = compas_rhino.rs.GetReal("Define the target edge length of the pattern.", 1.0)

# Process the input surface.
result = surface.discrete_mapping(D, crv_guids=crv_guids, pt_guids=pt_guids)
outer_boundary, inner_boundaries, polyline_features, point_features = result

# ==============================================================================
# Generate pattern
# ==============================================================================

# Triangulate the input surface.
trimesh = boundary_triangulation(*result, delaunay=delaunay)

# Make a decomposition mesh from the triangulation.
decomposition = SkeletonDecomposition.from_mesh(trimesh)

# Generate a coarse mesh from the decomposition.
coarsemesh = decomposition.decomposition_mesh(point_features)

# Map coarse mesh edges to surface curve discretisations.
gkey_vertex = {geometric_key(coarsemesh.vertex_coordinates(vertex)): vertex for vertex in coarsemesh.vertices()}
edge_curve = {}
for polyline in decomposition.polylines:
    curve = compas_rhino.rs.AddInterpCrvOnSrfUV(srf_guid, [point[:2] for point in polyline])
    u = gkey_vertex[geometric_key(polyline[0])]
    v = gkey_vertex[geometric_key(polyline[-1])]
    edge_curve[u, v] = [
        compas_rhino.rs.EvaluateCurve(curve, compas_rhino.rs.CurveParameter(curve, t))
        for t in linspace(0, 1, 100)]
    compas_rhino.delete_object(curve)

# Densify the coarse mesh
coarsemesh.collect_strips()
coarsemesh.set_strips_density_target(L)
coarsemesh.densification(edges_to_curves=edge_curve)
densemesh = coarsemesh.get_quad_mesh()

# Remap the meshes back onto the surface
surface.mesh_uv_to_xyz(trimesh)
surface.mesh_uv_to_xyz(coarsemesh)

# ==============================================================================
# Postprocess the result
# ==============================================================================

mesh = Mesh.from_vertices_and_faces(*densemesh.to_vertices_and_faces())

# Constrain mesh components to the feature geometry.
constraints = automated_smoothing_surface_constraints(mesh, surface)
constraints.update(
    automated_smoothing_constraints(mesh, rhinopoints=points, rhinocurves=curves))

# Smooth with constraints.
constrained_smoothing(
    mesh, kmax=100, damping=0.5, constraints=constraints, algorithm="area")

# ==============================================================================
# Visualization
# ==============================================================================

artist = MeshArtist(trimesh, layer="Singular::Triangulation")
artist.clear_layer()
artist.draw_mesh()

artist = MeshArtist(coarsemesh, layer="Singular::CoarseMesh")
artist.clear_layer()
artist.draw_mesh()

artist = MeshArtist(densemesh, layer="Singular::DenseMesh")
artist.clear_layer()
artist.draw_mesh()

artist = MeshArtist(mesh, layer="Singular::SmoothMesh")
artist.clear_layer()
artist.draw_mesh()
