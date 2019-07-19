import itertools as it

from compas_pattern.datastructures.mesh_quad.grammar_pattern import delete_strip
from compas_pattern.datastructures.mesh_quad.grammar_pattern import delete_strips
from compas_pattern.datastructures.mesh_quad.grammar_pattern import add_strips

from compas_pattern.algorithms.interpolation.isomorphism import *

__all__ = [
]


class Mapper:

    def __init__(self, meshes):
        self.meshes = meshes
        self.submesh = None
        self.maps = None

    def get_meshes(self):
        return self.meshes

    def get_submesh(self):
        return self.submesh

    def get_maps(self):
        return self.maps

    def compute_submesh(self):
        self.submesh = find_submesh_between_n_meshes(self.get_meshes())
        return self.submesh

    def compute_maps(self):
        meshes = self.get_meshes()
        submesh = self.get_submesh()
        maps = {mesh: {submesh: self.map_mesh_to_submesh(mesh)} for mesh in meshes}
        self.maps = maps
        maps[submesh] = {mesh: self.reverse_map_mesh_to_submesh(mesh) for mesh in meshes}
        #self.maps = maps
        return self.maps

    def map_mesh_to_submesh(self, mesh):
        submesh = self.get_submesh()
        mesh_to_map_mesh = {vkey: vkey for vkey in mesh.vertices()}
        strips_to_delete = submesh_and_distance_and_deletion_rules_between_2_meshes(mesh, submesh)[0][2][mesh]
        map_mesh = mesh.copy()
        for skey in strips_to_delete:
            old_vkeys_to_new_vkeys = delete_strip(map_mesh, skey)
            mesh_to_map_mesh = {mesh_key: old_vkeys_to_new_vkeys[map_mesh_key] if map_mesh_key in old_vkeys_to_new_vkeys else map_mesh_key for mesh_key, map_mesh_key in mesh_to_map_mesh.items()}
        matches = matches_between_ismorphic_meshes(map_mesh, submesh, boundary_edge_data=True)
        match_0 = list(matches)[0]
        mesh_to_submesh = {mesh_key: match_0[map_mesh_key] for mesh_key, map_mesh_key in mesh_to_map_mesh.items()}
        return mesh_to_submesh

    def reverse_map_mesh_to_submesh(self, mesh):
        submesh = self.get_submesh()
        mesh_to_submesh = self.get_maps()[mesh][submesh]
        submesh_to_mesh = {vkey: [] for vkey in mesh_to_submesh.values()}
        for mesh_key, submesh_key in mesh_to_submesh.items():
            submesh_to_mesh[submesh_key].append(mesh_key)
        return submesh_to_mesh

    def map_from_mesh_to_mesh(self, mesh_0, mesh_1):
        submesh = self.get_submesh()
        maps = self.get_maps()
        return {key: maps[submesh][mesh_1][item] for key, item in maps[mesh_0][submesh].items()}

    def map_polyedge_from_mesh_to_mesh(self, polyedge, mesh_0, mesh_1):
        vkey_map = self.map_from_mesh_to_mesh(mesh_0, mesh_1)
        return [vkey_map[vkey] for vkey in polyedge]

# --------------------------------------------------------------------------
# distances, deletion rules and submeshes
# --------------------------------------------------------------------------


def distance_and_deletion_rules_between_2_meshes(mesh_i, mesh_j):
    # get the distance between two meshes by testing combinations for deleting an increasing number of strips
    # until strip graphs are isomorphic, and mesh graphs as well in a second step, due to the limited data in strip graphs
    # isomoprhism comparison differentiate close strips and boundary edges

    # exist potentially multiple common submeshes with the same number of strips but only one is yielded

    # check cost for checking isomorphism of graph compared to mesh
    # other possibility to compare: very fast heuristic ismorphism check on strip graph and classic one on mesh graph

    results = []

    ni, nj = mesh_i.number_of_strips(), mesh_j.number_of_strips()
    
    for k in range(0, max(ni, nj) + 1):
        
        for nodes_i in it.combinations(list(mesh_i.strips()), max(k, k + ni - nj)):
            mesh_i_copy = mesh_i.copy()
            delete_strips(mesh_i_copy, nodes_i)
            # discard if collateral strip deletions, which are at a higher distance
            if ni - mesh_i_copy.number_of_strips() != len(nodes_i):
                continue

            for nodes_j in it.combinations(list(mesh_j.strips()), max(k, k + nj - ni)):
                mesh_j_copy = mesh_j.copy()
                delete_strips(mesh_j_copy, nodes_j)
                # discard if collateral strip deletions, which are at a higher distance
                if nj - mesh_j_copy.number_of_strips() != len(nodes_j):
                    continue

                # test strip isomorphism
                if are_strips_isomorphic(mesh_i_copy, mesh_j_copy, close_strip_data=True):  
                    # test mesh isomorphism
                    if are_meshes_isomorphic(mesh_i_copy, mesh_j_copy, boundary_edge_data=True):
                        distance = max(k, k + ni - nj) + max(k, k + nj - ni)
                        results.append((distance, {mesh_i: nodes_i, mesh_j: nodes_j}))
        
        # potentially several combinations with different combinations of strips at the same distance
        if len(results) != 0:
            return results


def submesh_and_distance_and_deletion_rules_between_2_meshes(mesh_i, mesh_j):
    distance, deletion_rules = distance_and_deletion_rules_between_2_meshes(mesh_i, mesh_j)
    submesh = mesh_i.copy()
    delete_strips(submesh, deletion_rules[mesh_i])
    return submesh, distance, deletion_rules


def submesh_and_distance_and_deletion_rules_between_n_meshes(meshes):

    submesh = find_submesh_between_n_meshes(meshes)

    distances_to_submesh = {}
    deletion_rules_to_submesh = {}
    for mesh in meshes:
        distance, deletion_rules = distance_and_deletion_rules_between_2_meshes(mesh, submesh)
        deletion_rules_to_submesh[mesh] = deletion_rules[mesh]
        distances_to_submesh[mesh] = distance

    return submesh, distances_to_submesh, deletion_rules_to_submesh


def find_submesh_between_n_meshes(meshes):
    # find common submesh to n meshes starting with the first mesh and deleting strips after comparisons wit the other ones

    submesh = meshes[0].copy()
    for mesh in meshes[1:]:
        distance, deletion_rules = distance_and_deletion_rules_between_2_meshes(submesh, mesh)
        delete_strips(submesh, deletion_rules[submesh])
    return submesh


def polyedge_from_mesh_to_submesh(polyedge, mesh, submesh, match_mesh_to_submesh):
    # or from supermesh to mesh
    trans_mesh = mesh.copy()
    old_vkeys_to_new_vkeys = delete_strip(trans_mesh, skey)
    submesh_polyedge = [match_mesh_to_submesh[old_vkeys_to_new_vkeys[vkey]] if vkey in old_vkeys_to_new_vkeys else vkey for vkey in polyedge]


def add_strip_to_other_mesh_via_submesh(mesh, skey, submesh, supermesh, match_mesh_to_submesh):

    mesh_polyedge = mesh.strip_side_polyedges(skey)[0]

    mesh_submesh = mesh.copy()
    old_vkeys_to_new_vkeys = delete_strip(mesh_submesh, skey)
    submesh_polyedge = [match_mesh_to_submesh[old_vkeys_to_new_vkeys[vkey]] if vkey in old_vkeys_to_new_vkeys else vkey for vkey in polyedge]

    super_mesh_polyedge


def reverse_deletion_to_deletion_rules(mesh, submesh, strips_to_delete):
    skey_to_polyedge = {skey: mesh.strip_side_polyedges(skey)[0] for skey in strips_to_delete}
    
    trimmed_mesh = mesh.copy()
    for skey in strips_to_delete:
        old_vkeys_to_new_vkeys = delete_strip(trimmed_mesh, skey)
        skey_to_polyedge = {skey: [old_vkeys_to_new_vkeys[vkey] if vkey in old_vkeys_to_new_vkeys else vkey for vkey in polyedge] for skey, polyedge in skey_to_polyedge.items()}
    
    # find equivalent in submesh
    matches = matches_between_ismorphic_meshes(trimmed_mesh, submesh, boundary_edge_data=False)
    match_0 = list(matches)[0] # only one of the matches is selected
    
    # remap polyedge using match found in submesh
    skey_to_polyedge = {skey: [match_0[vkey] for vkey in polyedge] for skey, polyedge in skey_to_polyedge.items()}

    # avoid ismorphisms between polyedges due to flips, and offsets for closed polyedges
    skey_to_polyedge = {skey: remove_isomorphism_in_polyedge(polyedge) for skey, polyedge in skey_to_polyedge.items()}
    
    return skey_to_polyedge


def interpolation(meshes):

    for mesh in meshes:
        mesh.collect_strips()

    # get common mesh to all other meshes
    # compare common mesh with all others to find strips to add
    submesh, distances_to_submesh, deletion_rules_to_submesh = submesh_and_distance_and_deletion_rules_between_n_meshes(meshes)
    
    return 0
    # 3. find corresponding polyedge per strip to add by deleting all
    polyedges_to_add = {mesh: find_polyedges_to_add(mesh, submesh, deletion_rules_to_submesh[mesh]) for mesh in meshes}
    
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
            distance = [a - b for a, b in zip([distances_to_submesh[mesh] for mesh in meshes], movement)]
            interpolated_meshes[submesh_copy] = distance
             
    return meshes, interpolated_meshes


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    from compas_pattern.datastructures.mesh_quad_coarse.mesh_quad_coarse import CoarseQuadMesh
    from compas_pattern.algorithms.interpolation.layout import *
    from compas.datastructures import meshes_join
    from compas_plotters.meshplotter import MeshPlotter

    mesh_1 = CoarseQuadMesh.from_json('/Users/Robin/Desktop/json/f.json')
    mesh_2 = CoarseQuadMesh.from_json('/Users/Robin/Desktop/json/g.json')
    mesh_3 = CoarseQuadMesh.from_json('/Users/Robin/Desktop/json/h.json')
    mesh_4 = CoarseQuadMesh.from_json('/Users/Robin/Desktop/json/i.json')
    mesh_5 = CoarseQuadMesh.from_json('/Users/Robin/Desktop/json/j.json')

    # mesh_1.collect_strips()
    # mesh_5.collect_strips()
    # print(distance_and_deletion_rules_between_2_meshes(mesh_1, mesh_5))

    meshes = [mesh_2, mesh_3]
    for mesh in meshes:
        mesh.collect_strips()

    for result in distance_and_deletion_rules_between_2_meshes(*meshes):
        print(result)
    # mapper = Mapper(meshes)
    # mapper.compute_submesh()
    # mapper.compute_maps()
    # #print(mapper.get_maps())
    # print(mapper.map_from_mesh_to_mesh(meshes[0], meshes[1]))
    # print(mapper.map_from_mesh_to_mesh(meshes[1], meshes[0]))
    # #print(mapper.map_from_mesh_to_mesh(meshes[1], meshes[1]))

    # print(mapper.map_polyedge_from_mesh_to_mesh([0, 1, 2], meshes[0], meshes[1]))

    #print(interpolation(meshes))
    # meshes, interpolated_meshes = interpolation(meshes)
    # print(interpolated_meshes)
    
    # #interpolation_layout_primary(meshes, interpolated_meshes, 200.0)
    # #interpolation_layout_secondary(interpolated_meshes, 20.0)
    # interpolation_layout_two_meshes(interpolated_meshes, 10, 20)

    # super_mesh = meshes_join(list(interpolated_meshes.keys()))

    # plotter = MeshPlotter(super_mesh, figsize = (20, 20))
    # plotter.draw_vertices(radius = 0.01)
    # plotter.draw_edges()
    # plotter.draw_faces()
    # plotter.show()
