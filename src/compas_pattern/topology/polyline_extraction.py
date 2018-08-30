from compas.datastructures.mesh import Mesh

from compas.topology.duality import mesh_dual

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2017, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'

__all__ = [
    'mesh_boundaries',
    'quad_mesh_polylines',
    'dual_edge_polylines',
    'singularity_polylines',
    'strip_polylines',
]

def mesh_boundaries(mesh, vertex_splits = []):
    """Extract mesh outer and inner boundaries as lists of vertices with optional splits.

    Parameters
    ----------
    mesh : Mesh
        Mesh.
    vertex_splits : list
        List of boundary vertex keys for optional splits.

    Returns
    -------
    split_boundaries: list
        List of boundaries as lists of vertex keys.

    """

    boundary_vertices = [vkey for vkey in mesh.vertices_on_boundary() if len(mesh.vertex_neighbours(vkey)) != 0]

    vertex_splits = [vkey for vkey in vertex_splits if vkey in boundary_vertices]

    # collect boundary polylines with splits
    split_boundaries = []
    count = len(boundary_vertices) * 2
    while len(boundary_vertices) > 0 and count > 0:
        count -= 1
        if len(vertex_splits) > 0:
            start = vertex_splits.pop()
            boundary_vertices.remove(start)
        else:
            start = boundary_vertices.pop()
        polyline = [start]
        count_2 = len(boundary_vertices) * 2
        while count_2 > 0:
            count_2 -= 1
            for nbr, fkey in iter(mesh.halfedge[polyline[-1]].items()):
                if fkey is None:
                    if nbr in boundary_vertices:
                        boundary_vertices.remove(nbr)
                    polyline.append(nbr)
                    break

            # end of boundary element
            if start == polyline[-1]:
                split_boundaries.append(polyline)
                break
            # end of boundary subelement
            elif polyline[-1] in vertex_splits:
                split_boundaries.append(polyline)
                vertex_splits.remove(polyline[-1])
                polyline = polyline[-1 :]
                
    return split_boundaries

def quad_mesh_polylines(mesh, dual = False):
    """Extracts the polylines as lists of keys of vertices of a quad mesh or faces of the quad mesh dual.

    Parameters
    ----------
    mesh : Mesh
        A quad mesh.
    dual : bool
        False to collect the vertex keys of the quad mesh.
        True to collect the face keys of the quad mesh dual.

    Returns
    -------
    list or None
        If on the primal:
        The list of polylines as lists of vertex keys.
        If on the dual:
        The list of dual polylines as list of face keys.
        None if not a quad mesh.

    """
    
    # switch to dual
    if dual:
        mesh = mesh_dual(mesh)

    # store edges to keep track of which one are visited
    edges = list(mesh.edges())

    nb_edges = mesh.number_of_edges()

    # store polylines
    polylines = []

    # pop edges from the stack to start polylines until the stack is empty
    while nb_edges > 0:
        u0, v0 = edges.pop()
        nb_edges -= 1
        # is polyline on the boundary
        if mesh.is_edge_on_boundary(u0, v0):
            is_boundary_polyline = True
        else:
            is_boundary_polyline = False
        polyline = [u0, v0]
        # search next polyline edges in both directions
        for i in range(2):
            count = nb_edges
            while count > 0:
                # start from last edge
                u, v = polyline[-2], polyline[-1]
                count -= 1
                # for not boundary polyline: stop if the last vertex is on the boundary or if it is a singularity or if the polyline is closed "without kink"
                if not is_boundary_polyline and (mesh.is_vertex_on_boundary(v) or len(mesh.vertex_neighbours(v)) != 4 or polyline[0] == polyline[-1]):
                    break
                # for boundary polyline: stop if the last vertex is on the boundary or if it is a singularity or if the polyline is closed "without kink"
                elif is_boundary_polyline and (len(mesh.vertex_neighbours(v)) != 3 or polyline[0] == polyline[-1]):
                    break             
                # get next vertex of polyline
                # dichotomy if halfedge u v points outside in case of boundary polylines
                if mesh.halfedge[u][v] is not None:
                    x = mesh.face_vertex_descendant(mesh.halfedge[u][v], v)
                    w = mesh.face_vertex_descendant(mesh.halfedge[x][v], v)
                else:
                    x = mesh.face_vertex_ancestor(mesh.halfedge[v][u], v)
                    w = mesh.face_vertex_ancestor(mesh.halfedge[v][x], v)
                # remove next edge of polyline from the stack
                if (v, w) in edges:
                    edges.remove((v, w))
                else:
                    edges.remove((w, v))
                nb_edges -= 1
                polyline.append(w)
                
            # before starting searching in the other direction
            polyline.reverse()
            # do not do second search if the polyline is already closed
            if polyline[0] == polyline[-1]:
                break
        polylines.append(polyline)

    return polylines

def dual_edge_polylines(mesh):
    """Groups edges that are opposite to each other in a quad face.

    Parameters
    ----------
    mesh : Mesh
        A quad mesh.

    Returns
    -------
    list or None
        The list of edge groups as lists of edges.
        None if not a quad mesh.

    Raises
    ------
    -

    """

    # check if is a quad mesh
    if not mesh.is_quadmesh():
        return None
    

    edge_groups = {}
    max_group = 0
    for fkey in mesh.faces():
        a, b, c, d = mesh.face_vertices(fkey)
        for u, v, w, x in [ [a, b, c, d], [b, c, d, a] ]:
 
            # exceptions if pseudo quad mesh with faces like [a, b, c, c]
            if u == v:
                if (w, x) not in edge_groups:
                    max_group += 1
                    edge_groups[(w, x)] = max_group
                    edge_groups[(x, w)] = max_group
            elif w == x:
                if (u, v) not in edge_groups:
                    max_group += 1
                    edge_groups[(u, v)] = max_group
                    edge_groups[(v, u)] = max_group

            else:
                if (u, v) in edge_groups and (w, x) in edge_groups:
                    # flip one
                    new_group = edge_groups[(u, v)]
                    old_group = edge_groups[(w, x)]
                    for e0, e1 in edge_groups:
                        if edge_groups[(e0, e1)] == old_group:
                            edge_groups[(e0, e1)] = new_group
                            edge_groups[(e1, e0)] = new_group

                elif (u, v) not in edge_groups and (w, x) in edge_groups:
                    # add the other
                    group = edge_groups[(w, x)]
                    edge_groups[(u, v)] = group
                    edge_groups[(v, u)] = group

                elif (u, v) in edge_groups and (w, x) not in edge_groups:
                    # add the other
                    group = edge_groups[(u, v)]
                    edge_groups[(w, x)] = group
                    edge_groups[(x, w)] = group

                else:
                    # start new group
                    max_group += 1
                    edge_groups[(u, v)] = max_group
                    edge_groups[(v, u)] = max_group
                    edge_groups[(w, x)] = max_group
                    edge_groups[(x, w)] = max_group

    return edge_groups, max_group

def singularity_polylines(mesh):
    """Collect vertex polylines in a quad mesh that stem from singularities.

    Parameters
    ----------
    mesh : Mesh
        A quad mesh.

    Returns
    -------
    list or None
        The list of polylines as lists of vertices.
        None if not a quad mesh.

    Raises
    ------
    -

    """

    # check if is a quad mesh
    if not mesh.is_quadmesh():
        return None

    singularities = [vkey for vkey in mesh.vertices() if (mesh.is_vertex_on_boundary(vkey) and len(mesh.vertex_neighbours(vkey)) != 3) or (not mesh.is_vertex_on_boundary(vkey) and len(mesh.vertex_neighbours(vkey)) != 4)]
    polylines = []
    
    # start from singularuty
    for sing in singularities:

        # propagate in each direction
        for nbr in mesh.vertex_neighbours(sing):
            # initiate
            u = sing
            v = nbr
            polyline = [u, v]
            is_polyline_on_boundary = mesh.is_vertex_on_boundary(polyline[1])
            count = mesh.number_of_vertices()

            # continue until next singularity
            while polyline[-1] not in singularities and count > 0:
                if not mesh.is_vertex_on_boundary(polyline[1]) and mesh.is_vertex_on_boundary(polyline[-1]):
                    break
                count -= 1
                u = polyline[-2]
                v = polyline[-1]
                nbrs = mesh.vertex_neighbours(v, True)
                idx = nbrs.index(u)
                # if not on boundary
                if not mesh.is_vertex_on_boundary(v):
                    w = nbrs[idx - 2]
                # if on boundary
                else:
                    if mesh.is_vertex_on_boundary(nbrs[idx - 1]):
                        w = nbrs[idx - 1]
                    else:
                        w = nbrs[idx - 2]
                polyline.append(w)

            # avoid duplicate polylines (additional criteria for loops)
            if polyline[-1] not in singularities or polyline[0] < polyline[-1] or (polyline[0] == polyline[-1] and polyline[1] < polyline[-2]):
                polylines.append(polyline)

    return polylines

def strip_polylines(mesh):

    edge_groups, max_group = dual_edge_polylines(mesh)

    strip_polylines = {}
    for fkey in mesh.faces():
        a, b, c, d = mesh.face_vertices(fkey)
        group_0 = edge_groups[(a, b)]
        line_0 = [mesh.edge_midpoint(a, b), mesh.edge_midpoint(c, d)]
        if group_0 in strip_polylines:
            strip_polylines[group_0].append(line_0)
        else:
            strip_polylines[group_0] = [line_0]
            
        group_1 = edge_groups[(b, c)]
        line_1 = [mesh.edge_midpoint(b, c), mesh.edge_midpoint(d, a)]
        if group_1 in strip_polylines:
            strip_polylines[group_1].append(line_1)
        else:
            strip_polylines[group_1] = [line_1]

    polylines = []
    for key, item in strip_polylines.items():
        lines = item
        polyline = lines.pop()
        count = len(lines)
        while len(lines) > 0 and count > 0:
            count -= 1
            to_remove = None
            for u, v in lines:
                if u == polyline[0]:
                    polyline.insert(0, v)
                    to_remove = [u, v]
                elif u == polyline[-1]:
                    polyline.append(v)
                    to_remove = [u, v]
                elif v == polyline[0]:
                    polyline.insert(0, u)
                    to_remove = [u, v]
                elif v == polyline[-1]:
                    polyline.append(u)
                    to_remove = [u, v]
                if to_remove is not None:
                    break
            lines.remove(to_remove)
        polylines.append(polyline)

    return polylines
# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas
