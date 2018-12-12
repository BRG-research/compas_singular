__all__ = [
	'list_split',
	'are_items_in_list'
]


def list_split(l, indices):
	"""Split list at given indices.
	Closed lists have the same first and last elements.
	If the list is closed, splitting wraps around if the first or last index is not in the indices to split.


	Parameters
	----------
	l : list
		A list.
	indices : list
		A list of indices to split.

	Returns
	-------
	split_lists : list
		Nest lists from splitting the list at the given indices.

	"""

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


def are_items_in_list(items, l):
	"""Check if items are in a list.

	Parameters
	----------
	items : list
		A list of items (order does not matter).
	l : list
		A list.

	Returns
	-------
	bool
		True if all items are in the list. False otherwise.

	"""

	for i in items:
		if i not in l:
			return False
	return True


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas

    print list_split(range(20)+[0],[0,8,9,12,13])
    