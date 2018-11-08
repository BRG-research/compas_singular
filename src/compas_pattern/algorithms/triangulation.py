from compas_pattern.datastructures.mesh import Mesh

from compas.topology import delaunay_from_points

from compas.utilities import geometric_key

from compas_pattern.topology.joining_welding import unweld_mesh_along_edge_path

import random

from compas.geometry import centroid_points
from compas.geometry import distance_point_point
from compas.geometry import add_vectors
from compas.geometry import bounding_box

from compas.geometry import is_point_in_polygon_xy
from compas.geometry import is_point_in_triangle_xy
from compas.geometry import is_point_in_circle_xy
from compas.geometry import circle_from_points_xy

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
    'triangulation',
]

def triangulation(boundary, holes = [], polyline_features = [], point_features = []):
    """Generates a trimmed Delaunay mesh on a closed outer boundary polyline with potential
    closed inner boundary polylines, polyline constraints and point constraints.

    Parameters
    ----------
    boundary : list
        List of vertices of the closed outer boundary polyline.
    holes : list
        List of lists of vertices of the closed inner boundary polylines.
    polyline_features : list
        List of lists of vertices of the feature polylines for constraints to the Delaunay triangulation.
    point_features : list
        List of points for constraints to the Delaunay triangulation.

    Returns
    -------
    delunay_mesh: Mesh

    Raises
    ------
    -

    """

    # topological cut along the feature polylines through unwelding
    vertex_map = {geometric_key(delaunay_mesh.vertex_coordinates(vkey)): vkey for vkey in delaunay_mesh.vertices()}

    edge_paths = []
    for polyline in polyline_features:
        edge_path = []
        vertex_path = [vertex_map[geometric_key([float(x), float(y), float(z)])] for x, y, z in polyline]
        for i in range(len(vertex_path) - 1):
            if vertex_path[i + 1] in delaunay_mesh.halfedge[vertex_path[i]]:
                edge_path.append([vertex_path[i], vertex_path[i + 1]])
        edge_paths.append(edge_path)

    for edge_path in edge_paths:
        unweld_mesh_along_edge_path(delaunay_mesh, edge_path)

    return delaunay_mesh

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas

    mesh = Mesh()
    mesh.add_vertex(x=0.,y=0.,z=0.)
    mesh.add_vertex(x=0.,y=1.,z=0.)
    mesh.add_vertex(x=1.,y=0.,z=0.)
    mesh.add_face([0,1,2])
    cl = type(mesh)
    print cl
    #l = type(mesh).__call__
    #print cl    
    #cl = type(mesh).name
    #print cl
    mesh = cl()
    print mesh
