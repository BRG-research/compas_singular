from compas.datastructures.mesh import Mesh

from compas_pattern.datastructures.pseudo_quad_mesh import PseudoQuadMesh

from compas.topology import mesh_flip_cycles
from compas_pattern.topology.joining_welding import join_meshes

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
    'mesh_thickening',
]

def mesh_thickening(mesh, thickness = 1):
    """Transforms a mesh with the topology of a perforated disc into a closed mesh.

    Parameters
    ----------
    mesh : Mesh
        Mesh with the topology of a perforated disc.
    thickness : real
        Mesh thickness


    Returns
    -------
    vertices : list, None
        The vertices of the thickened mesh.
        None if thicnkess not striclty positive.
    faces : list, None
        The faces of the thickened mesh.
        None if thicnkess not striclty positive.

    """

    offset_mesh = mesh.copy()

    new_positions = {}
    for vkey in offset_mesh.vertices():
        xyz0 = offset_mesh.vertex_coordinates(vkey)
        if len(offset_mesh.vertex_neighbours(vkey)) == 0:
            xyz1 = [0, 0, 1]
        else:
            xyz1 = offset_mesh.vertex_normal(vkey)
        xyz2 = [thickness * a for a in xyz1]
        xyz = [sum(a) for a in zip(xyz0, xyz2)]
        new_positions[vkey] = xyz

    for vkey, xyz in new_positions.items():
            x, y, z = xyz
            attr = offset_mesh.vertex[vkey]
            attr['x'] = x
            attr['y'] = y
            attr['z'] = z

    mesh_flip_cycles(mesh)

    vertices, faces = join_meshes([mesh, offset_mesh])
    new_mesh = PseudoQuadMesh.from_vertices_and_faces(vertices, faces)

    n = new_mesh.number_of_vertices() / 2

    naked_edges = list(new_mesh.edges_on_boundary())
    for u, v in naked_edges:
        if u >= n:
            continue
        w = v + n
        x = u + n
        new_mesh.add_face([x, w, v, u])

    return new_mesh

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
