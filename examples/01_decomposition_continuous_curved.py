try:
    import rhinoscriptsyntax as rs
except ImportError:
    compas.raise_if_ironpython()

from compas_pattern.algorithms import surface_discrete_mapping
from compas_pattern.algorithms import boundary_triangulation
from compas_pattern.algorithms import SkeletonDecomposition
from compas_pattern.algorithms import decomposition_mesh
from compas_rhino.artists import MeshArtist

# draw your own surfaces, curves and points or get them from examples/data/01_decomposition.3dm

# get input data
srf_guid = rs.GetObject('Rhino surface to decompose', filter=8) or []
crv_guids = rs.GetObjects('Rhino curves to integrate', filter=4) or []
pt_guids = rs.GetObjects('Rhino points to integrate', filter=1) or []

discretisation = rs.GetReal('Value for precision - between 1 and 5 percent of scale', number=1, minimum=0)

# get outer boundary polyline, inner boundary polylines, polyline features and point features by mapping curved surface to plan and discretising its boundaries and features
outer_boundary, inner_boundaries, polyline_features, point_features = surface_discrete_mapping(srf_guid, discretisation, crv_guids = crv_guids, pt_guids = pt_guids)

# Delaunay triangulation of the surface formed by the planar polylines using the points as Delaunay vertices
mesh = boundary_triangulation(outer_boundary, inner_boundaries, polyline_features, point_features)

# start instance for skeleton-based decomposition
decomposition = SkeletonDecomposition.from_mesh(mesh)

# build decomposition mesh
mesh = decomposition_mesh(decomposition, srf_guid, point_features)

# draw decomposition mesh
MeshArtist(mesh).draw_mesh()
