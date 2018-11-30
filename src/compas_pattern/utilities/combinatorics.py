from compas.utilities import pairwise

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
	'binomial_coefficient'
]

def binomial_coefficient(n, k):

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
