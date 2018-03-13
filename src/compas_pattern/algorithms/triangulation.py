from compas.datastructures.mesh import Mesh

from compas.topology import delaunay_from_points

from compas.utilities import geometric_key

from compas_pattern.topology.unwelding import unweld_mesh_along_edge_path

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

    # get polyline points for Delaunay triangulation
    delaunay_points = []
    delaunay_points += boundary + point_features
    for polyline in holes:
        delaunay_points += polyline
    for polyline in polyline_features:
        delaunay_points += polyline

    # remove duplicates based on their geometric keys
    delaunay_point_map = {}
    for point in delaunay_points:
        geom_key = geometric_key(point)
        if geom_key not in delaunay_point_map:
            delaunay_point_map[geom_key] = point
    delaunay_points = list(delaunay_point_map.values())

    holes = [hole[: -1] for hole in holes]
    
    # generate Delaunay mesh
    delaunay_faces = delaunay_from_points(delaunay_points, boundary = boundary[: -1], holes = holes)
    delaunay_mesh = Mesh.from_vertices_and_faces(delaunay_points, delaunay_faces)

    # topological cut along the feature polylines through unwelding
    vertex_map = {geometric_key(delaunay_mesh.vertex_coordinates(vkey)): vkey for vkey in delaunay_mesh.vertices()}

    edge_paths = []
    for polyline in polyline_features:
        edge_path = []
        vertex_path = [vertex_map[geometric_key(point)] for point in polyline]
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
