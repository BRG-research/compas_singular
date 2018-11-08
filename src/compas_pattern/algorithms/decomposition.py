from compas_pattern.datastructures.mesh import Mesh

from compas.topology import delaunay_from_points

from compas.utilities import geometric_key

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
    'decomposition',
]

def decomposition(delaunay_mesh):
    """Constructs a patch decomposition from a Delaunay mesh based on pruning and grafting of its medial axis.

    Parameters
    ----------
    delaunay_mesh : Mesh
        Delaunay mesh.

    Returns
    -------
    patch_decomposition: list, None
        List of polylines as lists of points forming the inner and outer polylines of the patch decomposition.
        Return None if input mesh is not a trimesh.

    Raises
    ------
    -

    """


    # create geometric map of split vertices to recollect all vertices with same geometric key
    # necessary because of curve features and unwelded paths of delaunay_mesh
    map_split_vertices = [geometric_key(delaunay_mesh.vertex_coordinates(vkey)) for vkey in culled_split_vertices]
    split_vertices = [vkey for vkey in delaunay_mesh.vertices() if geometric_key(delaunay_mesh.vertex_coordinates(vkey)) in map_split_vertices]

    # collect boundary polylines with splits
    split_boundaries = []
    while len(split_vertices) > 0:
        start = split_vertices.pop()
        # exception if split vertex corresponds to a non-boundary point feature
        if not delaunay_mesh.is_vertex_on_boundary(start):
            continue
        polyline = [start]

        while 1:
            for nbr, fkey in iter(delaunay_mesh.halfedge[polyline[-1]].items()):
                if fkey is None:
                    polyline.append(nbr)
                    break

            # end of boundary element
            if start == polyline[-1]:
                split_boundaries.append(polyline)
                break
            # end of boundary subelement
            elif polyline[-1] in split_vertices:
                split_boundaries.append(polyline)
                split_vertices.remove(polyline[-1])
                polyline = polyline[-1 :]

    # convert list of vertices into list of points
    boundary_polylines = [ [delaunay_mesh.vertex_coordinates(vkey) for vkey in split_boundary]for split_boundary in split_boundaries]
    
    # remove duplicate boundaries due to curve features and unwelded delaunay mesh
    culled_boundary_polylines = []
    for polyline_1 in boundary_polylines:
        add = True
        for polyline_2 in culled_boundary_polylines:
            if polyline_1 == polyline_2:
                add = False
                break
            polyline_1.reverse()
            if polyline_1 == polyline_2:
                add = False
                break
        if add:
            culled_boundary_polylines.append(polyline_1)

    return medial_branches, culled_boundary_polylines

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
    