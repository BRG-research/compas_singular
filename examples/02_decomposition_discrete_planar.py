import os
import json

from compas_singular.algorithms import boundary_triangulation
from compas_singular.algorithms import SkeletonDecomposition
from compas_plotters.meshplotter import MeshPlotter

HERE = os.path.dirname(__file__)
FILE = os.path.join(HERE, 'data/01_decomposition.json')

# read input data
with open(FILE, 'r') as f:
    data = json.load(f)

# get outer boundary polyline, inner boundary polylines, polyline features and point features
outer_boundary, inner_boundaries, polyline_features, point_features = data

# Delaunay triangulation of the surface formed by the planar polylines using the points as Delaunay vertices
trimesh = boundary_triangulation(outer_boundary, inner_boundaries, polyline_features, point_features)

# start instance for skeleton-based decomposition
decomposition = SkeletonDecomposition.from_mesh(trimesh)

# build decomposition mesh
coarsemesh = decomposition.decomposition_mesh(point_features)

# densify
coarsemesh.collect_strips()
coarsemesh.set_strips_density_target(0.5)
coarsemesh.densification()
densemesh = coarsemesh.get_quad_mesh()

# plot decomposition mesh
plotter = MeshPlotter(densemesh, figsize=(5, 5))
plotter.draw_edges()
plotter.draw_vertices(radius=0.03)
plotter.draw_faces()
plotter.show()
