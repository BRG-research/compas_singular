try:
    import networkx as nx
except:
    pass

import itertools as it

import operator
from math import pi
from compas_pattern.datastructures.mesh_quad.grammar_pattern import delete_strip
from compas_pattern.datastructures.mesh_quad.grammar_pattern import delete_strips
from compas_pattern.datastructures.mesh_quad.grammar_pattern import add_strips
from compas_pattern.datastructures.mesh.operations import mesh_move_by
from compas.geometry import circle_evaluate
from compas.geometry import subtract_vectors
from compas.geometry import centroid_points
from compas.geometry import weighted_centroid_points
from compas.geometry import bounding_box
from compas_plotters.meshplotter import MeshPlotter

__all__ = [
]


def strip_graph(mesh, close_strip_data=False):
    # graph of quad mesh strips: one graph vertex <-> one mesh strip and one graph <-> edge one mesh face
    # graph vertices have an attribute whether the corresponding strip is closed or not

    if mesh.data['attributes']['strips'] is None or mesh.data['attributes']['strips'] == {}:
        mesh.collect_strips()

    graph = nx.MultiGraph([tuple(mesh.face_strips(fkey)) for fkey in mesh.faces()])
    if close_strip_data:
        nx.set_node_attributes(graph, {skey : {'closed': mesh.is_strip_closed(skey)} for skey in mesh.strips()})
    return graph


def are_strip_graphs_isomorphic(strip_graph_i, strip_graph_j):
    # check if two strip graphs are isomorphic, including closeness data
    return nx.is_isomorphic(strip_graph_i, strip_graph_j, node_match=nx.isomorphism.categorical_node_match('closed', None))


def mesh_graph(mesh, boundary_edge_data=False):
    # graph of meshes with edges only
    # edges have an attribute whether they are on the boundary or not (vertex attributes would not be sufficient)
    graph = nx.MultiGraph(mesh.edges())
    if boundary_edge_data:
         nx.set_edge_attributes(graph, {edge: {'boundary': mesh.is_edge_on_boundary(*edge)} for edge in mesh.edges()})
    return graph


def are_mesh_graphs_isomorphic(mesh_graph_i, mesh_graph_j):
    # check if two mesh graphs are isomorphic, including boundary data
    return nx.is_isomorphic(mesh_graph_i, mesh_graph_j, edge_match=nx.isomorphism.categorical_edge_match('boundary', None))


def find_common_submesh_2(mesh_i, mesh_j):
    # get the distance between two meshes by testing combinations for deleting an increasing number of strips
    # until strip graphs are isomorphic, and mesh graphs as well in a second step, due to the limited data in strip graphs
    # isomoprhism comparison differentiate close strips and boundary edges

    # exist potentially multiple common submeshes with the same number of strips but only one is yielded

    # check cost for checking isomorphism of graph compared to mesh
    # other possibility to compare: very fast heuristic ismorphism check on strip graph and classic one on mesh graph

    strip_graph_i = strip_graph(mesh_i, close_strip_data=True)
    ni = strip_graph_i.number_of_nodes()

    strip_graph_j = strip_graph(mesh_j, close_strip_data=True)
    nj = strip_graph_j.number_of_nodes()

    for k in range(0, max(ni, nj) + 1):
        
        for nodes_i in it.combinations(strip_graph_i.nodes(), max(k, k + ni - nj)):
            strip_graph_i_copy = strip_graph_i.copy()
            strip_graph_i_copy.remove_nodes_from(nodes_i)
            
            for nodes_j in it.combinations(strip_graph_j.nodes(), max(k, k + nj - ni)):
                strip_graph_j_copy = strip_graph_j.copy()
                strip_graph_j_copy.remove_nodes_from(nodes_j)
                
                if are_strip_graphs_isomorphic(strip_graph_i_copy, strip_graph_j_copy):
                    mesh_i_copy, mesh_j_copy = mesh_i.copy(), mesh_j.copy()
                    delete_strips(mesh_i_copy, nodes_i)
                    delete_strips(mesh_j_copy, nodes_j)
                    
                    # discard if collateral strip deletions
                    if mesh_i.number_of_strips() - mesh_i_copy.number_of_strips() != len(nodes_i):
                        continue
                    if mesh_j.number_of_strips() - mesh_j_copy.number_of_strips() != len(nodes_j):
                        continue
                    
                    if are_mesh_graphs_isomorphic(mesh_graph(mesh_i_copy, boundary_edge_data=False), mesh_graph(mesh_j_copy, boundary_edge_data=False)):
                        distance = max(k, k + ni - nj) + max(k, k + nj - ni)
                        return distance, nodes_i, nodes_j


def find_common_submesh_n(meshes):
    # find common submesh to n meshes starting with the first mesh and deleting strips after comparisons wit the other ones

    meshes_copy = [mesh.copy() for mesh in meshes]
    mesh_0 = meshes_copy.pop()

    while meshes_copy:
        mesh_i = meshes_copy.pop()
        distance, nodes_0, nodes_i = find_common_submesh_2(mesh_0, mesh_i)
        delete_strips(mesh_0, nodes_0)

    return mesh_0


def find_polyedges_to_add(mesh, submesh, strips_to_delete):
    skey_to_polyedge = {skey: mesh.strip_side_polyedges(skey)[0] for skey in strips_to_delete}
    trimmed_mesh = mesh.copy()
    for skey in strips_to_delete:
        old_vkeys_to_new_vkeys = delete_strip(trimmed_mesh, skey)
        skey_to_polyedge = {skey: [old_vkeys_to_new_vkeys[vkey] if vkey in old_vkeys_to_new_vkeys else vkey for vkey in polyedge] for skey, polyedge in skey_to_polyedge.items()}
    
    # find equivalent in submesh
    trimmed_mesh_graph = mesh_graph(trimmed_mesh, boundary_edge_data=False)
    submesh_graph = mesh_graph(submesh, boundary_edge_data=False)
    matcher = nx.isomorphism.GraphMatcher(trimmed_mesh_graph, submesh_graph)
    matches = matcher.match()
    match_0 = list(matches)[0] # only one of the matches is selected
    # avoid ismorphisms between polyedges due to flips, and offsets for closed polyedges
    return {skey: remove_isomorphism_in_polyedge([match_0[vkey] for vkey in polyedge]) for skey, polyedge in skey_to_polyedge.items()}

def interpolation(meshes):

    # 1. get common mesh to all other meshes
    submesh = find_common_submesh_n(meshes)

    # 2. compare common mesh with all others to find strips to add
    strips_to_delete = {}
    distance_to_submesh = {}
    for mesh in meshes:
        distance, nodes_i, nodes_j = find_common_submesh_2(mesh, submesh)
        strips_to_delete[mesh] = nodes_i
        distance_to_submesh[mesh] = distance
    submesh_distance = [distance_to_submesh[mesh] for mesh in meshes]

    # 3. find corresponding polyedge per strip to add by deleting all
    polyedges_to_add = {mesh: find_polyedges_to_add(mesh, submesh, strips_to_delete[mesh]) for mesh in meshes}
    
    # 4. apply all combinations of strip addition
    interpolated_meshes = {}
    
    polyedge_delta_distance = {}
    for mesh, strip_to_polyedges in polyedges_to_add.items():
        i = meshes.index(mesh)
        for polyedge in strip_to_polyedges.values():
            polyedge = tuple(polyedge)
            if polyedge not in polyedge_delta_distance:
                polyedge_delta_distance[tuple(polyedge)] = [0] * len(meshes)
            d =  polyedge_delta_distance[polyedge]
            d[i] = 1
    # add negative delta distances
    for polyedge, distances in polyedge_delta_distance.items():
        polyedge_delta_distance[polyedge] = [1 if d == 1 else -1 for d in distances]


    all_polyedges = polyedge_delta_distance.keys()
    for k in range(len(all_polyedges) + 1):
        for combination_polyedges in it.combinations(all_polyedges, k):
            submesh_copy = submesh.copy()
            add_strips(submesh_copy, list(combination_polyedges))
            movement = [0] * len(meshes)
            for polyedge in combination_polyedges:
                for i, k in enumerate(polyedge_delta_distance[polyedge]):
                    movement[i] += k
            distance = [a - b for a, b in zip(submesh_distance, movement)]
            interpolated_meshes[submesh_copy] = distance
             
    return meshes, interpolated_meshes


def interpolation_layout_primary(meshes, interpolated_meshes, size):

    # sort input meshes and interpolating meshes
    ext_meshes = meshes
    int_meshes = []
    for mesh, distances in interpolated_meshes.items():
        if mesh not in ext_meshes:
            int_meshes.append(mesh)
    
    mesh_to_xyz = {mesh: [0.0, 0.0, 0.0] for mesh in ext_meshes + int_meshes}
    
    # map input meshes along a circle
    n = len(ext_meshes)
    for i, mesh in enumerate(ext_meshes):
        mesh_to_xyz[mesh] = circle_evaluate(2.0 * pi * i / n, size / 2.0)
    ext_points = [mesh_to_xyz[mesh] for mesh in ext_meshes]
    
    # map interpolating meshes in the circle
    for mesh in int_meshes:
        weights = [ext_meshes[i].number_of_strips() - d for i, d in enumerate(interpolated_meshes[mesh])]
        mesh_to_xyz[mesh] = weighted_centroid_points(ext_points, weights)

    # move meshes
    for mesh in interpolated_meshes.keys():
        centre = mesh.centroid() if mesh.area() != 0 else mesh.vertex_centroid()
        mesh_move_by(mesh, subtract_vectors(mesh_to_xyz[mesh], centre))


def interpolation_layout_secondary(interpolated_meshes, size):
    
    cluster_meshes = {tuple(distance): [] for distance in interpolated_meshes.values()}
    for mesh, distance in interpolated_meshes.items():
        cluster_meshes[tuple(distance)].append(mesh)

    for meshes in cluster_meshes.values():
        n = len(meshes)
        if n > 1:
            for i, mesh in enumerate(meshes):
                xyz = circle_evaluate(2.0 * pi * i / n + pi / 2.0, size / 2.0)
                centre = mesh.centroid() if mesh.area() != 0 else mesh.vertex_centroid()
                mesh_move_by(mesh, subtract_vectors(xyz, centre))


def interpolation_layout_2(interpolated_meshes, dx, dy):
    position_to_meshes = {}
    for mesh, (a, b) in interpolated_meshes.items():
        d = a - b
        if d in position_to_meshes:
            position_to_meshes[d].append(mesh)
        else:
            position_to_meshes[d] = [mesh]

    for d, meshes in position_to_meshes.items():
        for j, mesh in enumerate(meshes):
            centre = mesh.centroid() if mesh.area() != 0 else mesh.vertex_centroid()
            mesh_move_by(mesh, subtract_vectors([d * dx, - j * dy, 0.0], centre))


def remove_isomorphism_in_polyedge(polyedge):
    print(polyedge)
    # if closed: min value first, and its minimum neighbour value second
    if polyedge[0] == polyedge[-1]:
        polyedge = polyedge[:-1]
        #checks if multiple occurences of min value, and of min neighbour
        # min_k = min(polyedge)
        # starts = {i: 0 for i, k in enumerate(polyedge) if k == min_k}
        # for d in range(i, len(polyedge)):
        #     for i, k in starts.items():
        #          pass
        #idx_0 = starts[0]
        idx_0 = polyedge.index(min(polyedge))
        polyedge = polyedge[idx_0:] + polyedge[:idx_0]
        if polyedge[1] > polyedge[-1]:
            polyedge = list(reversed(polyedge))
            polyedge = polyedge[-1:] + polyedge[:-1]
        polyedge += polyedge[:1]

    # if open: minimum value extremmity at the start
    else:
        if polyedge[0] > polyedge[-1]:
            polyedge = list(reversed(polyedge))

    return polyedge


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    from compas_pattern.datastructures.mesh_quad_coarse.mesh_quad_coarse import CoarseQuadMesh
    from compas.datastructures import meshes_join
    from compas_plotters.meshplotter import MeshPlotter

    mesh_1 = CoarseQuadMesh.from_json('/Users/Robin/Desktop/json/f.json')
    mesh_2 = CoarseQuadMesh.from_json('/Users/Robin/Desktop/json/g.json')
    mesh_3 = CoarseQuadMesh.from_json('/Users/Robin/Desktop/json/h.json')
    mesh_4 = CoarseQuadMesh.from_json('/Users/Robin/Desktop/json/i.json')

    meshes = [mesh_1, mesh_4]

    meshes, interpolated_meshes = interpolation(meshes)
    print(interpolated_meshes)
    
    #interpolation_layout_primary(meshes, interpolated_meshes, 200.0)
    #interpolation_layout_secondary(interpolated_meshes, 20.0)
    interpolation_layout_2(interpolated_meshes, 10, 20)

    super_mesh = meshes_join(list(interpolated_meshes.keys()))

    plotter = MeshPlotter(super_mesh, figsize = (20, 20))
    plotter.draw_vertices(radius = 0.01)
    plotter.draw_edges()
    plotter.draw_faces()
    plotter.show()
