from compas.datastructures.mesh import Mesh

from compas.topology import delaunay_from_points

from compas_pattern.datastructures.mesh import face_circle

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
    'medial_axis',
]

def medial_axis(delaunay_mesh):
    """Construct the medial axis from a Delaunay mesh.

    Parameters
    ----------
    delaunay_mesh : Mesh
        Delaunay mesh.

    Returns
    -------
    medial_branches: list, None
        List of polylines as lists of vertices forming the branches of the medial axis.
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
    # the reference point is the circumcentre except for 1-valency singularities that is their 2-valency vertex
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
            if branch_path[0] < branch_path[-1] or (branch_path[0] == branch_path[-1] and branch_path[1] < branch_path[-2]):
                branch_paths.append(branch_path)

    # create polylines by converting paths of faces into series of reference points
    medial_branches = [[reference_points[fkey] for fkey in branch_path] for branch_path in branch_paths]
  
    return medial_branches

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
