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


def list_split(thelist, indices):
    """Split list at given indices.
    Closed lists have the same first and last elements.
    If the list is closed, splitting wraps around if the first or last index is not in the indices to split.


    Parameters
    ----------
    thelist : list
            A list.
    indices : list
            A list of indices to split.

    Returns
    -------
    split_lists : list
            Nest lists from splitting the list at the given indices.

    """

    n = len(thelist)

    if thelist[0] == thelist[-1]:
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
    for index, item in enumerate(thelist):
        current_list.append(item)
        if (index in indices and index != 0) or index == n - 1:
            split_lists.append(current_list)
            current_list = [item]

    if closed:
        if 0 not in indices:
            start = split_lists.pop(0)[1:]
            split_lists[-1] += start

    return split_lists


def sublist_from_to_items_in_closed_list(thelist, from_item, to_item):
    """Return sublist between oe item to another.

    Parameters
    ----------
    thelist : list
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
    if thelist[0] != thelist[-1]:
        thelist.append(thelist[0])
    from_idx = thelist.index(from_item)
    to_idx = thelist.index(to_item)
    sublists = list_split(thelist, [from_idx, to_idx])

    for sublist in sublists:
        if sublist[0] == from_item:
            return sublist


def are_items_in_list(items, thelist):
    """Check if items are in a list.

    Parameters
    ----------
    items : list
            A list of items (order does not matter).
    thelist : list
            A list.

    Returns
    -------
    bool
            True if all items are in the list. False otherwise.
    """

    for i in items:
        if i not in thelist:
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


def remove_isomorphism_in_integer_list(thelist):
    # remove isomorphisms in list (open or closed)
    # interpreted as a polyedge

    if len(thelist) < 2:
        return thelist

    # if closed: min value first, and its minimum neighbour value second
    if thelist[0] == thelist[-1]:
        thelist = thelist[:-1]
        candidates = []

        start = min(thelist)
        for i, key in enumerate(thelist):
            # collect all candidates, there may be multiple minimum values and multiple minimum neighbours
            if key == start:
                candidate = thelist[i:] + thelist[:i] + [thelist[i]]
                candidates.append(candidate)
                candidates.append(list(reversed(candidate)))
        for k in range(1, len(thelist) + 1):
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
        thelist = candidates[0]

    # if open: minimum value extremmity at the start
    else:
        if thelist[0] > thelist[-1]:
            thelist = list(reversed(thelist))

    return thelist


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass

    # import compas

    # print(list_split(list(range(20)) + [0], [0, 8, 9, 12, 13]))

    # print(sublist_from_to_items_in_closed_list(range(20), 13, 13))
