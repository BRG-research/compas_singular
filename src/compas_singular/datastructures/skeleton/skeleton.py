from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from compas.datastructures import network_polylines
from compas.datastructures import trimesh_face_circle
from compas.utilities import geometric_key

from ..mesh import Mesh
from ..network import Network


__all__ = ["Skeleton"]


class Skeleton(Mesh):
    """Skeleton class for the generation of the topological skeleton or medial axis from a Delaunay mesh.

    References
    ----------
    .. [1] Harry Blum. 1967. *A transformation for extracting new descriptors of shape*.
           Models for Perception of Speech and Visual Forms, pages 362--380.
           Available at http://pageperso.lif.univ-mrs.fr/~edouard.thiel/rech/1967-blum.pdf.
    .. [2] Punam K. Saha, Gunilla Borgefors, and Gabriella Sanniti di Baja. 2016. *A survey on skeletonization algorithms and their applications*.
           Pattern Recognition Letters, volume 76, pages 3--12.
           Available at https://www.sciencedirect.com/science/article/abs/pii/S0167865515001233.
    """

    def __init__(self):
        super(Skeleton, self).__init__()

    @classmethod
    def from_mesh(cls, mesh):
        """Construct a Skeleton object from a Mesh.

        Returns
        -------
        Skeleton
            A skeleton object.

        """
        return cls.from_vertices_and_faces(*mesh.to_vertices_and_faces())

    def singular_faces(self):
        """Get the indices of the singular faces in the Delaunay mesh, i.e. the ones with three neighbours.

        Returns
        -------
        list
            List of face keys.

        """
        return [fkey for fkey in self.faces() if len(self.face_neighbors(fkey)) == 3]

    def singular_points(self):
        """Get the XYZ-coordinates of the singular points of the topological skeleton, i.e. the face circumcentre of the singular faces.

        Returns
        -------
        list
            List of point XYZ-coordinates.

        """
        return [
            trimesh_face_circle(self, fkey)[0] for fkey in self.singular_faces()
        ]

    def lines(self):
        """Get the lines forming the topological skeleton, i.e. the lines connecting the circumcentres of adjacent faces.

        Returns
        -------
        list
            List of lines as tuples of pairs XYZ-coordinates.

        """
        return [
            (trimesh_face_circle(self, fkey)[0], trimesh_face_circle(self, nbr)[0])
            for fkey in self.faces()
            for nbr in self.face_neighbors(fkey)
            if fkey < nbr
            and geometric_key(trimesh_face_circle(self, fkey)[0])
            != geometric_key(trimesh_face_circle(self, nbr)[0])
        ]

    def branches(self):
        """Get the branch polylines of the topological skeleton as polylines connecting singular points.

        Returns
        -------
        list
            List of polylines as tuples of XYZ-coordinates.

        """
        return network_polylines(Network.from_lines(self.lines()))


# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
