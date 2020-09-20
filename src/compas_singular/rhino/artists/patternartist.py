from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas_rhino.artists import MeshArtist


__all__ = ['PatternArtist']


class PatternArtist(MeshArtist):

    def __init__(self, pattern, layer=None):
        super(PatternArtist, self).__init__(pattern, layer=layer)

    @property
    def pattern(self):
        return self.mesh

    @pattern.setter
    def pattern(self, pattern):
        self.mesh = pattern
