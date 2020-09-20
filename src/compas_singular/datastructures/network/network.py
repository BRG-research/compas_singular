from __future__ import absolute_import
from __future__ import print_function
from __future__ import division

from compas.datastructures import Network
# from compas.utilities import pairwise
# from compas.utilities import geometric_key


__all__ = ['Network']


class Network(Network):

    def __init__(self):
        super(Network, self).__init__()

    @classmethod
    def from_nodes_and_edges(cls, nodes, edges):
        """Construct a network from nodes and edges.

        Parameters
        ----------
        nodes : list , dict
            A list of node coordinates or a dictionary of keys pointing to node coordinates to specify keys.
        edges : list of tuple of int

        Returns
        -------
        Network
            A network object.

        Examples
        --------
        >>>
        """
        network = cls()
        for i, (x, y, z) in nodes.items():
            network.add_node(i, x=x, y=y, z=z)
        for u, v in edges:
            network.add_edge(u, v)
        return network


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass
