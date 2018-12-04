from math import degrees
from math import acos
from math import pi

from compas_pattern.datastructures.mesh import Mesh

from compas.geometry import length_vector
from compas.geometry import dot_vectors
from compas.geometry import cross_vectors
from compas.geometry import subtract_vectors
from compas.geometry import distance_line_line
from compas.geometry import distance_point_point
from compas.geometry import angle_points
from compas.geometry import normalize_vector

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
]


class Polyline(Polyline):

	def __init__(self, guid):
		super(Polyline, self).__init__(points) 

	def curvature(self):
		"""Discrete polyline curvature.


		Parameters
		----------
		polyline: list
			A list of points

		Returns
		-------
		polyline_curvatures_list: list
			List of curvatures per vertex per polyline []curvature].

		Raises
		------
		-

		 References
	    ----------
	    .. [1] Lionel Du Peloux. Modeling of bending-torsion couplings in active-bending structures. Application to the design of elastic gridshells. PhD thesis, Université Paris Est, École des Ponts ParisTech. 2017.
	           Available at: https://tel.archives-ouvertes.fr/tel-01757782/document.

		"""

		points = self.points
		curvatures = []

		for i in range(len(points)):
		
			if i == 0 or i == len(points) - 1:
				curvatures.append(0)
		
			else:
				a, b, c = points[i - 1 : i + 2]
				ab = subtract_vectors(b, a)
				bc = subtract_vectors(c, b)
				ac = subtract_vectors(c, a)

				curvatures.append(2 * length_vector(cross_vectors(ab, bc)) / (length_vector(ac) * length_vector(ab) * length_vector(bc)))

		return curvatures

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
