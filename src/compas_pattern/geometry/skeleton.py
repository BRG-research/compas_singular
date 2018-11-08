from compas_pattern.datastructures.mesh import Mesh

from compas_pattern.geometry.join import join_lines_to_polylines

from compas.utilities import geometric_key

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
    'Skeleton',
]

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

    def singular_faces(self):
        return [fkey for fkey in self.faces() if len(self.face_neighbors(fkey)) == 3]

    def singular_points(self):
        return [self.face_circle(fkey)[0] for fkey in self.singular_faces()]
        
    def lines(self):
        return [(self.face_circle(fkey)[0], self.face_circle(nbr)[0]) for fkey in self.faces() for nbr in self.face_neighbors(fkey) if fkey < nbr and geometric_key(self.face_circle(fkey)[0]) != geometric_key(self.face_circle(nbr)[0])]

    def branches(self):
        return join_lines_to_polylines(self.lines())

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
