from compas_rhino.artists import MeshArtist
__all__ = [
	'PatternArtist'
]


class PatternArtist(MeshArtist):

	def __init__(self, pattern, layer=None):
		super(MeshArtist, self).__init__(layer=layer)
		self.pattern = pattern
		self.mesh = pattern


	def draw_singularity_mesh(self):

		self.clear()
		self.