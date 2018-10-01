from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas.utilities import color_to_colordict

import compas_rhino


__all__ = ['StripArtist']

class StripHelpers(object):

    def strip_name(self, key):
        """Get the name of a strip.

        Parameters
        ----------
        key : hashable
            The identifier of the strip.

        Returns
        -------
        str
            The name of the strip in the following format ``<name>.strip.<key>``,
            with *name* the name of the datastructure.

        """
        return '{}.strip.{}'.format(self.name, key)

    def strip_label_name(self, key):
        """Get the name of a strip label.

        Parameters
        ----------
        key : hashable
            The identifier of the strip.

        Returns
        -------
        str
            The name of the label in the following format ``<name>.strip.label.<key>``,
            with *name* the name of the datastructure.

        """
        return '{0}.strip.label.{1}'.format(self.name, key)


class StripSelector(object):

    @staticmethod
    def select_strip(self, message="Select a strip."):
        guid = rs.GetObject(message, preselect=True, filter=rs.filter.point | rs.filter.textdot)
        if guid:
            prefix = self.attributes['name']
            name = rs.ObjectName(guid).split('.')
            if 'strip' in name:
                if not prefix or prefix in name:
                    key = name[-1]
                    return ast.literal_eval(key)
        return None

class StripArtist(object):

    def clear_striplabels(self, keys=None):
        """Clear all edge labels previously drawn by the ``EdgeArtist``.

        Parameters
        ----------
        keys : list, optional
            The keys of a specific set of edges of which the labels should be cleared.
            Default is to clear all edge labels.

        """
        if not keys:
            name = '{}.edge.label.*'.format(self.datastructure.name)
            guids = compas_rhino.get_objects(name=name)
        else:
            guids = []
            for key in keys:
                name = self.datastructure.edge_label_name(key)
                guid = compas_rhino.get_object(name=name)
                guids.append(guid)
        compas_rhino.delete_objects(guids)

    def draw_striplabels(self):
        """Draw the strip labels.

        Parameters
        ----------

        """
        
        strips_to_edges = self.strips_to_edges_dict()

        strip_labels = []
        for strip, edges in strips_to_edges.items():
            strip_labels += [{
                'pos'   : self.datastructure.edge_midpoint(u, v),
                'name'  : strip,
                'color' : [0, 0, 0],
                'text'  : strip,
                'layer' : self.layer
            } for u, v in edges]

        return compas_rhino.xdraw_points(edge_midpoints, layer=self.layer, clear=False, redraw=False)

# ==============================================================================
# Main
# ==============================================================================

if __name__ == "__main__":
    pass
