from compas.datastructures.mesh import Mesh

from compas.topology import delaunay_from_points

from compas_pattern.datastructures.mesh import face_circle

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
    'mesh_from_polylines',
]

def mesh_from_polylines(polylines):
    """Construct the mesh based on polylines. Uses mesh from lines and then reduces the valency of the faces
    by deleting the 2-valency vertices.

    Parameters
    ----------
    polylines : list
        List of polylines as list of vertices.

    Returns
    -------
    mesh: Mesh

    Raises
    ------
    -

    """

    # convert polylines in lines to use Mesh.from_lines
    lines = []
    for polyline in polylines:
        lines.append([polyline[i], polyline[i + 1]] for i in range(len(polyline) - 1))
    mesh = Mesh.from_lines(lines)

    # convert polygonal faces into minimal valency faces
    for fkey in mesh.faces():
        reduced_face_vertices = [vkey for vkey in mesh.face_vertices(fkey) if len(mesh.vertex_neighbours(vkey)) != 2]
        attr = mesh.facedata[fkey]
        mesh.delete_face(fkey)
        mesh.add_face(reduced_face_vertices, fkey, attr_dict = attr)

    return mesh


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
