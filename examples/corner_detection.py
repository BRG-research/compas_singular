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


# from compas_struct_ml.utilities import *
# from compas.geometry import angle_vectors

# vks_on_bnd = coarsemesh.vertices_on_boundary(ordered=True)
# eks_on_bnd = pairwise(vks_on_bnd, loop=True)
# eks_on_bnd_pairs = pairwise(eks_on_bnd, loop=True)

# TOL_ANG = 60
# angs = []
# for _ek0, _ek1 in eks_on_bnd_pairs:
#     _vec0 = coarsemesh.edge_direction(*_ek0)
#     _vec1 = coarsemesh.edge_direction(*_ek1)
#     angs.append(angle_vectors(_vec0, _vec1, deg=True))
# print(angs)

# inds = range(len(angs))
# inds = [_i for _i, _a in enumerate(angs) if _a > TOL_ANG]
# vks = [eks_on_bnd_pairs[_i][0][1] for _i in inds]

print(vks)

plotter = MeshPlotter(coarsemesh, figsize=(5, 5))
plotter.draw_edges()
plotter.draw_vertices(text='key', radius=0.03)
plotter.draw_faces()
plotter.show()



# densify
# coarsemesh.collect_strips()
# coarsemesh.set_strips_density_target(0.5)
# coarsemesh.densification()
# coarsemesh.get_quad_mesh()
