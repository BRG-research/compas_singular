import compas

try:
	import rhinoscriptsyntax as rs

except ImportError:
	compas.raise_if_ironpython()

from compas_rhino.geometry import RhinoGeometry

from compas_pattern.datastructures.mesh import Mesh
from compas_pattern.datastructures.quad_mesh import QuadMesh
from compas_pattern.datastructures.coarse_quad_mesh import CoarseQuadMesh
from compas_pattern.datastructures.pseudo_quad_mesh import PseudoQuadMesh
from compas_pattern.datastructures.coarse_pseudo_quad_mesh import CoarsePseudoQuadMesh

from compas_pattern.cad.rhino.utilities import clear_layer
from compas_pattern.cad.rhino.utilities import draw_mesh

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [

]

class Pattern:
	"""Definition of a pattern.

	Attributes
	----------
	singularity_mesh : coarse_pseudo_quad_mesh
		A coarse pseudo-quad mesh with data regarding singularities.
	quad_mesh : mesh
		A mesh with data regarding density.
	pattern : mesh
		A mesh with data regarding the pattern's topology.
	geometry : mesh
		A mesh with data regarding the pattern's geoemtry.

	"""

	def __init__(self, settings = None):
		if settings is not None:
			self.settings = settings
		else:
			self.settings = {}
		self.singularity_mesh = CoarsePseudoQuadMesh()
		self.density_mesh = PseudoQuadMesh()
		self.topology_mesh = Mesh()
		self.geometry_mesh = Mesh()

	# --------------------------------------------------------------------------
	# add layers
	# --------------------------------------------------------------------------

	def add_layers(self):
		"""Add the layers to draw the meshes.

		"""

		for layer in ['singularity', 'density', 'topology', 'geometry']:
			rs.AddLayer(layer)

	# --------------------------------------------------------------------------
	# collect data
	# --------------------------------------------------------------------------

	def collect_data_singularity(self):
		"""Collect the existing singularity mesh in the singularity layer.

		"""

		objects = rs.ObjectsByLayer('singularity')

		if objects is not None:

			if len(objects) == 1:
				if rs.ObjectType(objects[0]) == 32:

					vertices, faces = RhinoGeometry.from_guid(objects[0]).get_vertices_and_faces()
					self.singularity_mesh = CoarseQuadMesh.from_vertices_and_faces(vertices, faces)
				
				else:
					print 'the object in the singularity layer is not a mesh'

			elif len(objects) > 1:
				print 'too many objects in the singularity layer'

	def collect_data_density(self):
		"""Collect the existing density mesh in the density layer.

		"""

		objects = rs.ObjectsByLayer('density')

		if objects is not None:

			if len(objects) == 1:
				if rs.ObjectType(objects[0]) == 32:

					vertices, faces = RhinoGeometry.from_guid(objects[0]).get_vertices_and_faces()
					self.density_mesh = Mesh.from_vertices_and_faces(vertices, faces)
				
				else:
					print 'the object in the density layer is not a mesh'

			elif len(objects) > 1:
				print 'too many objects in the density layer'

	def collect_data_topology(self):
		"""Collect the existing pattern topology in the topology layer.

		"""

		objects = rs.ObjectsByLayer('topology')

		if objects is not None:

			if len(objects) == 1:
				if rs.ObjectType(objects[0]) == 32:

					vertices, faces = RhinoGeometry.from_guid(objects[0]).get_vertices_and_faces()
					self.pattern_topology = Mesh.from_vertices_and_faces(vertices, faces)
				
				else:
					print 'the object in the topology layer is not a mesh'

			elif len(objects) > 1:
				print 'too many objects in the topology layer'

	def collect_data_geometry(self):
		"""Collect the existing pattern geoemtry in the geometry layer.

		"""

		objects = rs.ObjectsByLayer('geometry')

		if objects is not None:

			if len(objects) == 1:
				if rs.ObjectType(objects[0]) == 32:

					vertices, faces = RhinoGeometry.from_guid(objects[0]).get_vertices_and_faces()
					self.pattern_geoemtry = Mesh.from_vertices_and_faces(vertices, faces)
				
				else:
					print 'the object in the geometry layer is not a mesh'

			elif len(objects) > 1:
				print 'too many objects in the geometry layer'

	def collect_all_data(self):
		"""Collect the existing data in the layers.

		"""

		self.collect_data_singularity()
		self.collect_data_density()
		self.collect_data_topology()
		self.collect_data_geometry()

	# --------------------------------------------------------------------------
	# draw data
	# --------------------------------------------------------------------------

	def draw_singularity(self):
		"""Draw the pattern's singularity in the singularity layer.

	    Returns
	    -------
	    guid
        	The singularity mesh guid in Rhino.

		"""

		clear_layer('singularity')
		return draw_mesh(self.singularity_mesh, 'singularity')

	def draw_density(self):
		"""Draw the pattern's density in the density layer.
		
		Returns
	    -------
	    guid
        	The density mesh guid in Rhino.

		"""

		clear_layer('density')
		return draw_mesh(self.density_mesh, 'density')
	
	def draw_topology(self):
		"""Draw the pattern's topology mesh in the topology layer.

		Returns
	    -------
	    guid
        	The topology mesh guid in Rhino.

		"""

		clear_layer('topology')
		return draw_mesh(self.topology_mesh, 'topology')

	def draw_geometry(self):
		"""Draw the pattern's geometry mesh in the geometry layer.

		Returns
	    -------
	    guid
        	The geometry mesh guid in Rhino.

		"""

		clear_layer('geometry')
		return draw_mesh(self.geometry_mesh, 'geometry')

	def draw_all_data(self):
		"""Draw all the data.

		Returns
	    -------
	    list
        	The list of the mesh guids in Rhino.

		"""

		return self.draw_singularity(), self.draw_density(), self.draw_topology(), self.draw_geometry()

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	import compas
