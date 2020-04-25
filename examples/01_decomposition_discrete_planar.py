import json

from compas_pattern.algorithms import boundary_triangulation
from compas_pattern.algorithms import SkeletonDecomposition

from compas_plotters.meshplotter import MeshPlotter

# read input data
filepath = 'data/01_decomposition.json'
with open(filepath, 'r') as fp:
        data = json.load(fp)

# get outer boundary polyline, inner boundary polylines, polyline features and point features
outer_boundary, inner_boundaries, polyline_features, point_features = data

# Delaunay triangulation of the surface formed by the planar polylines using the points as Delaunay vertices
mesh = boundary_triangulation(outer_boundary, inner_boundaries, polyline_features, point_features, src='numpy')

# start instance for skeleton-based decomposition
decomposition = SkeletonDecomposition.from_mesh(mesh)

# # build decomposition mesh
mesh = decomposition.decomposition_mesh(point_features)

# plot decomposition mesh
plotter = MeshPlotter(mesh, figsize=(5, 5))
plotter.draw_edges()
plotter.draw_vertices()
plotter.draw_faces()
plotter.show()
