try:
    import rhinoscriptsyntax as rs

except ImportError:
    import platform
    if platform.python_implementation() == 'IronPython':
        raise

from compas.datastructures.mesh import Mesh

from compas_pattern.topology.templates import template

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

    a_pt = rs.GetPoint('1st vertex')
    a_type = rs.GetString('is corner?', defaultString = 'False', strings = ['True', 'False'])
    b_pt = rs.GetPoint('2nd vertex')
    b_type = rs.GetString('is corner?', defaultString = 'False', strings = ['True', 'False'])
    c_pt = rs.GetPoint('3rd vertex')
    c_type = rs.GetString('is corner?', defaultString = 'False', strings = ['True', 'False'])
    d_pt = rs.GetPoint('4th vertex')
    d_type = rs.GetString('is corner?', defaultString = 'False', strings = ['True', 'False'])
    points = [a_pt, b_pt, c_pt, d_pt]
    types = [a_type, b_type, c_type, d_type]
    vertices, faces = template(points, types)

    return vertices, faces

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
