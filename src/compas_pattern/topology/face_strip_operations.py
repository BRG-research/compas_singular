from compas.datastructures.mesh import Mesh

from compas_pattern.topology.polyline_extraction import dual_edge_groups
from compas_pattern.topology.polyline_extraction import quad_mesh_polylines_all

from compas_pattern.topology.joining_welding import weld_mesh

from compas_pattern.topology.grammar_rules import quad_quad_1
from compas_pattern.topology.grammar_rules import penta_quad_1
from compas_pattern.topology.grammar_rules import hexa_quad_1
from compas_pattern.topology.grammar_rules import quad_tri_1

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2018, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
    'face_strip_collapse',
    'face_strip_subdivide',
    'face_strips_merge',
    'face_strip_insert',
]


def face_strip_collapse(cls, mesh, u, v):
    """Collapse a face strip in a quad mesh.

    Parameters
    ----------
    mesh : Mesh
        A quad mesh.
    u: int
        Key of edge start vertex.
    v: int
        Key of edge end vertex.

    Returns
    -------
    mesh : mesh, None
        The modified quad mesh.
        None if mesh is not a quad mesh or if (u,v) is not an edge.

    Raises
    ------
    -

    """

    # checks
    if not mesh.is_quadmesh():
        return None
    if v not in mesh.halfedge[u] and u not in mesh.halfedge[v]:
        return None

    # get edges in the face strip
    edge_groups, max_group = dual_edge_groups(mesh)
    group_number = edge_groups[(u, v)]
    edges_to_collapse = [edge for edge, group in edge_groups.items() if group == group_number]

    # delete faces in the face strip
    for u, v in edges_to_collapse:
        if v in mesh.halfedge[u]:
            fkey = mesh.halfedge[u][v]
            if fkey is not None:
                mesh.delete_face(fkey)

    to_cull = []
    # merge vertices of collapsed edges
    boundary_vertices = mesh.vertices_on_boundary()
    for u, v in edges_to_collapse:
        # if only one edge vertex on boundary, set as new location
        if u in boundary_vertices and v not in boundary_vertices:
            x, y, z = mesh.vertex_coordinates(v)
        elif v in boundary_vertices and u not in boundary_vertices:
            x, y, z = mesh.vertex_coordinates(u)
        # or to edge midpoint otherwise
        else:
            x, y, z = mesh.edge_midpoint(u, v)
        w = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})
        # update adjacent face vertices
        for vkey in [u, v]:
            for fkey in mesh.vertex_faces(vkey):
                face_vertices = mesh.face_vertices(fkey)[:]
                idx = face_vertices.index(vkey)
                face_vertices[idx] = w
                mesh.delete_face(fkey)
                mesh.add_face(face_vertices, fkey)
        
    # clean mesh
    mesh = weld_mesh(cls, mesh)
    mesh.cull_vertices()

    return mesh

def face_strip_subdivide(cls, mesh, u, v):
    """Subdivide a face strip in a quad mesh.

    Parameters
    ----------
    mesh : Mesh
        A quad mesh.
    u: int
        Key of edge start vertex.
    v: int
        Key of edge end vertex.

    Returns
    -------
    mesh : mesh, None
        The modified quad mesh.
        None if mesh is not a quad mesh or if (u,v) is not an edge.

    Raises
    ------
    -

    """

    # checks
    if not mesh.is_quadmesh():
        return None
    if v not in mesh.halfedge[u] and u not in mesh.halfedge[v]:
        return None

    # add new vertex at mid edge
    x, y, z = mesh.edge_midpoint(u, v)
    w = mesh.add_vertex(attr_dict = {'x': x, 'y': y, 'z': z})


    # transform adjacent quad faces in penta faces with new vertex
    # [u][v]
    if v in mesh.halfedge[u] and mesh.halfedge[u][v] is not None:
        fkey = mesh.halfedge[u][v]
        face_vertices = mesh.face_vertices(fkey)[:]
        i = face_vertices.index(v)
        face_vertices.insert(i, w)
        mesh.delete_face(fkey)
        mesh.add_face(face_vertices, fkey)
    # [v][u]
    if u in mesh.halfedge[v] and mesh.halfedge[v][u] is not None:
        fkey = mesh.halfedge[v][u]
        face_vertices = mesh.face_vertices(fkey)[:]
        i = face_vertices.index(u)
        face_vertices.insert(i, w)
        mesh.delete_face(fkey)
        mesh.add_face(face_vertices, fkey)

    if w in mesh.halfedge[u] and mesh.halfedge[u][w] is not None:
        fkey = mesh.halfedge[u][w]
    elif u in mesh.halfedge[w] and mesh.halfedge[w][u] is not None:
        fkey = mesh.halfedge[w][u]
    else: fkey = None

    vkey = w

    is_naked = mesh.is_edge_on_boundary(u, w)
    is_loop = False

    # propagate
    count = mesh.number_of_faces()
    while count > 0:
        count -= 1
        if len(mesh.face_vertices(fkey)) == 5:
            wkey = penta_quad_1(mesh, fkey, vkey)
            fkey = mesh.halfedge[vkey][wkey]
            ukey = mesh.face_vertex_descendant(fkey, wkey)
            if mesh.is_edge_on_boundary(wkey, ukey):
                break
            else:
                fkey = mesh.halfedge[ukey][wkey]
                vkey = wkey
                if vkey == w:
                    is_loop = True
                    break
                else:
                    continue
        elif len(mesh.face_vertices(fkey)) == 6:
            hexa_quad_1(mesh, fkey, vkey)
            break
        elif len(mesh.face_vertices(fkey)) == 4:
            if vkey == w:
                is_loop = True
                break
            else:
                wkey = quad_tri_1(mesh, fkey, vkey)
                break
        break

    if not is_loop and not is_naked:
        fkey = mesh.halfedge[w][u]
        vkey = w
        count = mesh.number_of_faces()
        while count > 0:
            count -= 1
            if len(mesh.face_vertices(fkey)) == 5:
                wkey = penta_quad_1(mesh, fkey, vkey)
                fkey = mesh.halfedge[vkey][wkey]
                ukey = mesh.face_vertex_descendant(fkey, wkey)
                if mesh.is_edge_on_boundary(wkey, ukey):
                    break
                else:
                    fkey = mesh.halfedge[ukey][wkey]
                    vkey = wkey
                    if vkey == w:
                        is_loop = True
                        break
                    else:
                        continue
            elif len(mesh.face_vertices(fkey)) == 6:
                hexa_quad_1(mesh, fkey, vkey)
                break
            elif len(mesh.face_vertices(fkey)) == 4:
                if vkey == w:
                    is_loop = True
                    break
                else:
                    wkey = quad_tri_1(mesh, fkey, vkey)
                    break
            break

    return mesh

def face_strips_merge(cls, mesh, u, v):
    """Merge two parallel face strips in a quad mesh. The polyedge inbetween is composed of regular vertices only.

    Parameters
    ----------
    mesh : Mesh
        A quad mesh.
    u: int
        Start vertex key of an edge of the polyedge.
    v: int
        End vertex key of an edge of the polyedge.

    Returns
    -------
    mesh : mesh, None
        The modified quad mesh.
        None if mesh is not a quad mesh or if (u, v) is on boundary or if (u,v) is not on a polyedge with only regular vertices.

    Raises
    ------
    -

    """

    # check
    if not mesh.is_quadmesh():
        return None
    if mesh.is_edge_on_boundary(u, v):
        return None

    # get polyedge
    polylines = quad_mesh_polylines_all(mesh)
    for polyline in polylines:
        for i in range(len(polyline) - 1):
            if (u == polyline[i] and v == polyline[i + 1]) or (v == polyline[i] and u == polyline[i + 1]):
                polyedge = polyline

    # check
    for vkey in polyedge:
        if (mesh.is_vertex_on_boundary(vkey) and len(mesh.vertex_neighbours(vkey)) != 3) or (not mesh.is_vertex_on_boundary(vkey) and len(mesh.vertex_neighbours(vkey)) != 4): 
            return None


    # store faces of new face strip
    faces = []

    for i in range(len(polyedge) - 1):
        
        # per edge
        u, v = polyedge[i], polyedge[i + 1]
        
        # get adajcent faces
        fkey_1 = mesh.halfedge[u][v]
        fkey_2 = mesh.halfedge[v][u]

        # collect vertices of new face
        a = mesh.face_vertex_descendant(fkey_1, v)
        b = mesh.face_vertex_descendant(fkey_1, a)
        c = mesh.face_vertex_descendant(fkey_2, u)
        d = mesh.face_vertex_descendant(fkey_2, c)

        # delete old faces
        mesh.delete_face(fkey_1)
        mesh.delete_face(fkey_2)

        # add new face
        fkey = mesh.add_face([a, b, c, d])
        faces.append(fkey)

    return faces

def face_strip_insert(cls, mesh, polyedge):
    return 0

# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas

