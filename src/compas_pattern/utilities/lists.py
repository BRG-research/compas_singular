from compas.utilities import pairwise

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
]

def split_list(l, index):

	if index == 0 or index == len(l) - 1:
		return [l]

	return l[: index + 1], l[index :]


def splits_list(l, indices):

	indices = [0] + list(sorted(indices))
	ls = [l]

	for index_1, index_2 in pairwise(indices):	
		new_ls =  split_list(ls[-1], index_2 - index_1)
		del ls[-1]
		ls += new_ls

	return ls

def splits_closed_list(l, indices):
	
	indices = list(sorted(indices))

	if len(indices) == 0:
		return [l]

	if indices[0] != 0:
		l = l[indices[0] :] + l[1 : indices[0] + 1]
		indices = [idx - indices[0] for idx in indices]
	
	else:
		l = l[:] + [l[0]]
	
	return splits_list(l, indices)

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas

    print splits_closed_list(range(20) + [0],[])
    #print splits_closed_list([1, 21, 7, 8, 13, 27, 35, 10, 6, 9, 25, 34, 28, 12, 2, 23, 18, 3, 29, 24], [1, 6, 11, 16])