import rhinoscriptsyntax as rs

import compas_rhino as rhino

from compas.datastructures.mesh import Mesh

from compas_pattern.algorithms.delaunay_to_qpd import delaunay_to_patch_decomposition

# collect spatial shape: surface/mesh + features

# parameterisation from spatial to planar

# generate specific Delaunay mesh from planar shape and features

# patch polylines from Delaunay mesh

# conversion patch polylines to control mesh

# conforming operations into a quad control mesh

# possibility to apply grammar rules

# mesh densification

# mapping and smoothing on spatial shape

# conversion to pattern