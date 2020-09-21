from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.geometry import Polyline
from compas.geometry import length_vector
from compas.geometry import cross_vectors
from compas.geometry import subtract_vectors


__all__ = [
    'Polyline'
]


class Polyline(Polyline):

    def __init__(self, points):
        super(Polyline, self).__init__(points)

    def vertex_curvature(self, i):
        """Discrete polyline curvature.

        Parameters
        ----------
        i : int
            Vertex index.

        Returns
        -------
        curvature : float, None
            Curvature at the vertex.
            None if index out of range

        References
        ----------
        .. [1] Lionel Du Peloux. Modeling of bending-torsion couplings in active-bending structures.
               Application to the design of elastic gridshells. PhD thesis, Universite Paris Est, Ecole des Ponts ParisTech. 2017.
               Available at: https://tel.archives-ouvertes.fr/tel-01757782/document.

        """

        n = len(self.points)

        if i < 0 or i > n - 1:
            return None

        if i == 0 or i == n - 1:
            return 0.0

        a, b, c = self.points[i - 1: i + 2]
        ab = subtract_vectors(b, a)
        bc = subtract_vectors(c, b)
        ac = subtract_vectors(c, a)

        return 2 * length_vector(cross_vectors(ab, bc)) / (length_vector(ac) * length_vector(ab) * length_vector(bc))


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass

    # import compas

    # points = [[0.0, 0.0, 0.0], [1.0, 5.0, 0.0], [2.0, 0.0, 0.0], [3.0, -5.0, 0.0], [4.0, 0.0, 0.0]]
    # polyline = Polyline(points)

    # for i in range(len(points)):
    #     print(polyline.vertex_curvature(i))
