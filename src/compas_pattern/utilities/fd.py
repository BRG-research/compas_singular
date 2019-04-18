from compas.numerical import fd_numpy
from compas.utilities import XFunc

from compas_pattern.datastructures.mesh.mesh import Mesh

__all__ = [
    'fd_cpp_xfunc',
    'fd'
]


def fd_numpy_xfunc(vertices, edges, fixed, q, loads, **kwargs):

    return fd_numpy(vertices, edges, fixed, q, loads, **kwargs)


def fd(vertices, edges, fixed, q, loads, **kwargs):

    return XFunc('compas_pattern.utilities.fd.fd_numpy_xfunc')(vertices, edges, fixed, q, loads, **kwargs)


def fd_mesh_from_json(filepath, force_density, load):

    mesh = Mesh.from_json(filepath)

    vertices = [mesh.vertex_coordinates(vkey) for vkey in mesh.vertices()]
    edges = list(mesh.edges())
    fixed = mesh.vertices_on_boundary()
    q = [force_density] * len(edges)
    loads = [load] * len(vertices)

    xyz, q, f, l, r = fd(vertices, edges, fixed, q, loads)

    for vkey, coordinates in zip(mesh.vertices(), xyz):
        mesh.vertex[vkey]['x'] = coordinates[0]
        mesh.vertex[vkey]['y'] = coordinates[1]
        mesh.vertex[vkey]['z'] = coordinates[2]

    return mesh


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
