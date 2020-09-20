from __future__ import print_function
from __future__ import absolute_import
from __future__ import division


__all__ = [
    'list_split',
    'sublist_from_to_items_in_closed_list',
    'are_items_in_list',
    'common_items',
    'remove_isomorphism_in_integer_list'
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
        if (index in indices and index != 0) or index == n - 1:
            split_lists.append(current_list)
            current_list = [item]

    if closed:
        if 0 not in indices:
            start = split_lists.pop(0)[1:]
            split_lists[-1] += start

    return split_lists


def sublist_from_to_items_in_closed_list(l, from_item, to_item):
    """Return sublist between oe item to another.

    Parameters
    ----------
    l : list
            A list.
    from_item
            An item to be found in the list. The beginning of the sublist.
    to_item
            An item to be found in the list. The end of the sublist.

    Returns
    -------
    sublist : list
            A sublist from the input list, between from_item and to_item.
    """

    if from_item == to_item:
        return [from_item]
    if l[0] != l[-1]:
        l.append(l[0])
    from_idx = l.index(from_item)
    to_idx = l.index(to_item)
    sublists = list_split(l, [from_idx, to_idx])

    for sublist in sublists:
        if sublist[0] == from_item:
            return sublist


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


def common_items(l1, l2):
    """Return common items in two lists.

    Parameters
    ----------
    l1 : list
            A list.
    l2 : list
            A list.

    Returns
    -------
    list
            The common items.
    """

    return [item for item in l1 if item in l2]


def remove_isomorphism_in_integer_list(l):
    # remove isomorphisms in list (open or closed)
    # interpreted as a polyedge

    if len(l) < 2:
        return l

    # if closed: min value first, and its minimum neighbour value second
    if l[0] == l[-1]:
        l = l[:-1]
        candidates = []

        start = min(l)
        for i, key in enumerate(l):
            # collect all candidates, there may be multiple minimum values and multiple minimum neighbours
            if key == start:
                candidate = l[i:] + l[:i] + [l[i]]
                candidates.append(candidate)
                candidates.append(list(reversed(candidate)))
        for k in range(1, len(l) + 1):
            n = len(candidates)
            if n == 1:
                break
            # get minimum-sum sub-list
            min_x = None
            for candidate in candidates:
                x = sum(candidate[:k])
                if min_x is None or x < min_x:
                    min_x = x
            # compare to minimum-sum sub-list
            for i, candidate in enumerate(reversed(candidates)):
                if sum(candidate[:k]) > min_x:
                    del candidates[n - i - 1]
        # potentially multiple canidates left due to symmetry in list, but no isomorphism left
        l = candidates[0]

    # if open: minimum value extremmity at the start
    else:
        if l[0] > l[-1]:
            l = list(reversed(l))

    return l


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass

    # import compas

    # print(list_split(list(range(20)) + [0], [0, 8, 9, 12, 13]))

    # print(sublist_from_to_items_in_closed_list(range(20), 13, 13))
