from compas.datastructures.mesh import Mesh

from compas.topology import delaunay_from_points

from compas.utilities import geometric_key

from compas_pattern.datastructures.mesh import face_circle

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

    # return None if not a trimesh
    if not delaunay_mesh.is_trimesh():
        return None

    # collect 3-neighbour and 1-neighbour singularities as dictionary {fkey: nb neighbour}
    # collect reference points for polylines as dictionary {fkey: ref point}
    # the reference point is the circumcentre except for 1-neighbour singularities that is their 2-valency vertex
    singularities = {}
    reference_points = {}
    for fkey in delaunay_mesh.faces():
        nb_nbrs = len(delaunay_mesh.face_neighbours(fkey))
        if nb_nbrs == 3:
            singularities[fkey] = 3 
            reference_points[fkey] = face_circle(delaunay_mesh,fkey)[0]
        elif nb_nbrs == 1:
            singularities[fkey] = 1
            # find vertex with no other adjacent faces, i.e. with valency two
            for vkey in delaunay_mesh.face_vertices(fkey):
                if delaunay_mesh.vertex_degree(vkey) == 2:
                    reference_points[fkey] = delaunay_mesh.vertex_coordinates(vkey)
                    break
        else:
            reference_points[fkey] = face_circle(delaunay_mesh,fkey)[0]

    # collect branch paths that span from one singularity to another as series of faces
    branch_paths = []
    for singularity in singularities:
        for nbr in delaunay_mesh.face_neighbours(singularity):
            # start a potential new branch based on a singularity u and a neighbour v
            branch_path = []
            u, v = singularity, nbr
            branch_path = [u, v]
            count = delaunay_mesh.number_of_faces()
            end_loop = False
            # end loop only if reaches another singularity
            while not end_loop and count > 0:
                count -= 1
                if v not in singularities:
                    face_nbrs = delaunay_mesh.face_neighbours(v)
                    w = face_nbrs[face_nbrs.index(u) - 1]
                    branch_path.append(w)
                    u, v = v, w
                else:
                    end_loop = True
            # avoid duplicates by adding only one branch direction using following exclusion rules:
            # if not loop, add if first key smaller than last key
            # if loop, add if second key is smaller than second last key
            # PRUNING: do not add if the branch starts or ends from a 1-neighbour face 
            if branch_path[0] < branch_path[-1] or (branch_path[0] == branch_path[-1] and branch_path[1] < branch_path[-2]):
                if singularities[branch_path[0]] == 3 and singularities[branch_path[-1]] == 3:
                    branch_paths.append(branch_path)

    # create polylines by converting paths of faces into series of reference points
    medial_branches = [[reference_points[fkey] for fkey in branch_path] for branch_path in branch_paths]
    
    # GRAFTING
    for singularity in singularities:
        if singularities[singularity] == 3:
            for vkey in delaunay_mesh.face_vertices(singularity):
                medial_branches.append([reference_points[singularity], delaunay_mesh.vertex_coordinates(vkey)])

    # collect boundary polylines with splits at corner vertices and singularity vertices based on the Delaunay mesh
    
    #corner_vertices = [vkey for vkey in delaunay_mesh.face_vertices(fkey) for fkey, nb_nbrs in singularities.items() if nb_nbrs == 1 and delaunay_mesh.vertex_degree(vkey) == 2]
    corner_vertices = []
    for fkey, nb_nbrs in singularities.items():
        if nb_nbrs == 1:
            for vkey in delaunay_mesh.face_vertices(fkey):
                if delaunay_mesh.vertex_degree(vkey) == 2:
                    corner_vertices.append(vkey)
    
    #singularity_vertices = [vkey for vkey in delaunay_mesh.face_vertices(fkey) for fkey, nb_nbrs in singularities.items() if nb_nbrs == 3]
    singularity_vertices = []
    for fkey, nb_nbrs in singularities.items():
        if nb_nbrs == 3:
            singularity_vertices += delaunay_mesh.face_vertices(fkey)
    
    # remove duplicates
    split_vertices = corner_vertices + singularity_vertices
    culled_split_vertices = []
    for vkey in split_vertices:
        if vkey not in culled_split_vertices:
            culled_split_vertices.append(vkey)

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
    