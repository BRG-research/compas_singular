from compas.utilities import pairwise

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
	'list_split',
	'is_sublist_in_list'
]


def list_split(l, indices):

	n = len(l)

	if l[0] == l[-1]:
		closed = True
		if n - 1 in indices:
			indices.remove(n - 1)
			if 0 not in indices:
				indices.append(0)
	else:
		closed = False

	indices = list(sorted(set(indices)))

	split_lists = []
	current_list = []
	for index, item in enumerate(l):
		current_list.append(item)
		if (index in indices and index != 0) or index == n -1:
			split_lists.append(current_list)
			current_list = [item]

	if closed:
		if 0 not in indices:
			start = split_lists.pop(0)[1 :]
			split_lists[-1] += start

	return split_lists


def is_sublist_in_list(small_list, big_list):

	for i in small_list:
		is_in = False
		
		for j in big_list:
			if i == j:
				is_in = True
				break
		
		if not is_in:
			return False

	return True

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas

    print list_split(range(20)+[0],[0,8,9,12,13])
    