__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
	'mean',
	'standard_deviation'
]

def avrg(list):
	"""Average of a list.

	Parameters
	----------
	list : list
		List of values.

	Returns
	-------
	float
		The mean value.

	Raises
	------
	-

	"""

	return sum(list) / float(len(list))

def st_dev(list):
	"""Standard deviation of a list.

	Parameters
	----------
	list : list
		List of values.

	Returns
	-------
	float
		The standard deviation value.

	Raises
	------
	-

	"""

	m = avrg(list)

	return (sum([(i - m) ** 2 for i in list]) / float(len(list))) ** .5

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
    