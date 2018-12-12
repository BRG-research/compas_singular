__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
	'binomial_coefficient'
]

def binomial_coefficient(n, k):
	"""Binomial coefficient (n k), i.e. the number of possible combinations to select k elements among n ones.

	Parameters
	----------
	n : int
		Number of elements.
	k : int
		Number of selected elements.

	Returns
	-------
	x : int
		The number of possible combinations.

	"""

	k = min(k, n - k)
	x = 1
	y = 1
	i = n - k + 1

	while i <= n:
		x = (x * i) // y
		y += 1
		i += 1
	
	return x

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
