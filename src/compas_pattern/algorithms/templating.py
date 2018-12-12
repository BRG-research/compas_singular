try:
    import rhinoscriptsyntax as rs

except ImportError:
    import platform
    if platform.python_implementation() == 'IronPython':
        raise

from compas.datastructures.mesh import Mesh

from compas_pattern.topology.templates import template_disc
from compas_pattern.topology.templates import template_disc_advanced
from compas_pattern.topology.templates import template_sphere
from compas_pattern.topology.templates import template_torus

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
    'templating',
]

def templating():
    """Apply one of the simple quad mesh templates based on four points.

    Parameters
    ----------

    Returns
    -------
    vertices : list
        The vertices of the template.
    faces : list
        The faces of the template.

    Raises
    ------
    -

    """

    template_topology = rs.GetString('template topology?', defaultString = 'disc', strings = ['disc', 'disc_advanced', 'sphere', 'torus'])

    if template_topology == 'disc':
            X = rs.GetReal(message = 'X', number = 1, minimum = .0001, maximum = 1000)
            Y = rs.GetReal(message = 'Y', number = 1, minimum = .0001, maximum = 1000)
            vertices, faces = template_disc(X = X, Y = Y)

    elif template_topology == 'disc_advanced':
            X = rs.GetReal(message = 'X', number = 1, minimum = .0001, maximum = 1000)
            Y = rs.GetReal(message = 'Y', number = 1, minimum = .0001, maximum = 1000)
            a = rs.GetString('is 1st vertex corner?', defaultString = 'False', strings = ['True', 'False'])
            b = rs.GetString('is 2nd vertex corner?', defaultString = 'False', strings = ['True', 'False'])
            c = rs.GetString('is 3rd vertex corner?', defaultString = 'False', strings = ['True', 'False'])
            d = rs.GetString('is 4th vertexcorner?', defaultString = 'False', strings = ['True', 'False'])
            singularities_at_corner = [a, b, c, d]
            vertices, faces = template_disc(X = X, Y = Y)

    elif template_topology == 'sphere':
            X = rs.GetReal(message = 'X', number = 1, minimum = .0001, maximum = 1000)
            Y = rs.GetReal(message = 'Y', number = 1, minimum = .0001, maximum = 1000)
            Z = rs.GetReal(message = 'Z', number = 1, minimum = .0001, maximum = 1000)
            vertices, faces = template_sphere(X = X, Y = Y, Z = Z)

    elif template_topology == 'torus':
            X = rs.GetReal(message = 'X', number = 1, minimum = .0001, maximum = 1000)
            Y = rs.GetReal(message = 'Y', number = 1, minimum = .0001, maximum = 1000)
            Z = rs.GetReal(message = 'Z', number = 1, minimum = .0001, maximum = 1000)
            R = rs.GetReal(message = 'R', number = .25, minimum = .0001, maximum = 1000)
            vertices, faces = template_torus(X = X, Y = Y, Z= Z, R = R)

    return vertices, faces

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
