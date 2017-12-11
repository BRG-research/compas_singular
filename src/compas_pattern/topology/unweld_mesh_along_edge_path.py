from compas.datastructures.mesh import Mesh

__author__     = ['Robin Oval']
__copyright__  = 'Copyright 2014, Block Research Group - ETH Zurich'
__license__    = 'MIT License'
__email__      = 'oval@arch.ethz.ch'


__all__ = [
    'unweld_mesh_along_edge_path',
]


def unweld_mesh_along_edge_path(mesh, edge_path):
    """Unwelds mesh along a path of edges. The vertices along the path are duplicated and the corresponding faces modified.
    The vertices at the extremities of the edge path are duplicated only if they are on the boundary.

    Parameters
    ----------
    mesh : Mesh
    edge_path: list
        List of successive edges. A single edge does not apply any unwelding.

    Returns
    -------
    mesh : Mesh
        The mesh once unwelded.

    Raises
    ------
    -

    """
    
    # conversion of edge path in vertex path
    vertex_path = [edge[0] for edge in edge_path]
    # add last vertex of edge path only if different from first vertex, i.e. if not a loop.
    if edge_path[-1][-1] != vertex_path[0]:
        vertex_path.append(edge_path[-1][-1])

    # store changes to make in the faces along the vertex path in the following format {face to change = [old vertices, new vertex]}
    to_change = {}

    # iterate along path
    for i, vkey in enumerate(vertex_path):
        # vertices before and after current
        last_vkey = vertex_path[i - 1]
        next_vkey = vertex_path[i + 1 - len(vertex_path)]

        # skip the extremities of the vertex path, except if the path is a loop or if vertex is on boundary
        if (vertex_path[0] == vertex_path[-1]) or (i != 0 and i != len(vertex_path) - 1) or mesh.is_vertex_on_boundary(vkey):
            # duplicate vertex and its attributes
            attr = mesh.vertex[vkey]
            new_vkey = mesh.add_vertex(attr_dict = attr)
            # split neighbours in two groups depending on the side of the path
            vertex_nbrs = mesh.vertex_neighbours(vkey, True)
            # exceptions on last_vkey or next_vkey if the vertex is on the boundary
            if mesh.is_vertex_on_boundary(vkey):
                for j in range(len(vertex_nbrs)):
                    if mesh.is_vertex_on_boundary(vertex_nbrs[j - 1]) and mesh.is_vertex_on_boundary(vertex_nbrs[j]):
                        before, after = vertex_nbrs[j - 1], vertex_nbrs[j]
                if i == 0:
                    last_vkey = before
                elif i == len(vertex_path) - 1:
                    next_vkey = after
            idxa = vertex_nbrs.index(last_vkey)
            idxb = vertex_nbrs.index(next_vkey)
            if idxa < idxb:
                half_nbrs = vertex_nbrs[idxa : idxb]
            else:
                half_nbrs = vertex_nbrs[idxa :] + vertex_nbrs[: idxb]
            # get faces corresponding to vertex neighbours
            faces = [mesh.halfedge[nbr][vkey] for nbr in half_nbrs]
            # store change per face with index of duplicate vertex
            for fkey in faces:
                if fkey in to_change:
                    # add to other changes
                    to_change[fkey] += [[vkey, new_vkey]]
                else: 
                    to_change[fkey] = [[vkey, new_vkey]]

    # apply stored changes
    for fkey, changes in to_change.items():
        if fkey is None:
            continue
        face_vertices = mesh.face_vertices(fkey)[:]
        for change in changes:
            old_vertex, new_vertex = change
            # replace in list of face vertices
            idx = face_vertices.index(old_vertex)
            face_vertices[idx] = new_vertex
        # modify face by removing it and adding the new one
        attr = mesh.facedata[fkey]
        mesh.delete_face(fkey)
        mesh.add_face(face_vertices, fkey, attr_dict = attr)

    return mesh


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

    import compas

    vertices = [[4.014702796936035, 6.605471611022949, 0.0], [3.957170248031616, 7.572740077972412, 0.0], [3.899637460708618, 8.540008544921875, 0.0], [3.842104911804199, 9.50727653503418, 0.0], [3.784572124481201, 10.4745454788208, 0.0], [3.7270395755767822, 11.441813468933105, 0.0], [3.669506788253784, 12.40908145904541, 0.0], [3.611974000930786, 13.376350402832031, 0.0], [3.554441452026367, 14.343618392944336, 0.0], [3.496908664703369, 15.310886383056641, 0.0], [3.43937611579895, 16.278154373168945, 0.0], [3.381843328475952, 17.245424270629883, 0.0], [4.953444480895996, 6.716222286224365, 0.0], [4.888720512390137, 7.670785427093506, 0.0], [4.823996067047119, 8.625349044799805, 0.0], [4.759271621704102, 9.579912185668945, 0.0], [4.694547653198242, 10.534475326538086, 0.0], [4.629823207855225, 11.489038467407227, 0.0], [4.565098762512207, 12.443601608276367, 0.0], [4.500374794006348, 13.398164749145508, 0.0], [4.43565034866333, 14.352727890014648, 0.0], [4.370926380157471, 15.307291030883789, 0.0], [4.306201934814453, 16.26185417175293, 0.0], [4.2414774894714355, 17.21641731262207, 0.0], [5.892186164855957, 6.826972484588623, 0.0], [5.820270538330078, 7.7688307762146, 0.0], [5.748354434967041, 8.710688591003418, 0.0], [5.676438808441162, 9.652546882629395, 0.0], [5.604522705078125, 10.594405174255371, 0.0], [5.532607078552246, 11.536262512207031, 0.0], [5.460690975189209, 12.478120803833008, 0.0], [5.38877534866333, 13.419979095458984, 0.0], [5.316859245300293, 14.361837387084961, 0.0], [5.244943618774414, 15.303694725036621, 0.0], [5.173027515411377, 16.245553970336914, 0.0], [5.101111888885498, 17.187412261962891, 0.0], [6.830927848815918, 6.937723159790039, 0.0], [6.7518205642700195, 7.866876125335693, 0.0], [6.672713279724121, 8.796029090881348, 0.0], [6.5936055183410645, 9.725181579589844, 0.0], [6.514498233795166, 10.654335021972656, 0.0], [6.435390949249268, 11.583487510681152, 0.0], [6.356283187866211, 12.512640953063965, 0.0], [6.2771759033203125, 13.441793441772461, 0.0], [6.198068618774414, 14.370946884155273, 0.0], [6.118960857391357, 15.30009937286377, 0.0], [6.039853572845459, 16.229251861572266, 0.0], [5.9607462882995605, 17.158405303955078, 0.0], [7.769669532775879, 7.048473358154297, 0.0], [7.683370590209961, 7.964921474456787, 0.0], [7.597071647644043, 8.881368637084961, 0.0], [7.510772705078125, 9.797817230224609, 0.0], [7.424473762512207, 10.714264869689941, 0.0], [7.338174819946289, 11.630712509155273, 0.0], [7.251875400543213, 12.547160148620605, 0.0], [7.165576457977295, 13.463607788085938, 0.0], [7.079277515411377, 14.38005542755127, 0.0], [6.992978572845459, 15.296504020690918, 0.0], [6.906679630279541, 16.21295166015625, 0.0], [6.820380210876465, 17.129398345947266, 0.0], [8.70841121673584, 7.159224033355713, 0.0], [8.614920616149902, 8.062966346740723, 0.0], [8.521430015563965, 8.966709136962891, 0.0], [8.427939414978027, 9.870451927185059, 0.0], [8.33444881439209, 10.774194717407227, 0.0], [8.240958213806152, 11.677937507629395, 0.0], [8.147467613220215, 12.581680297851563, 0.0], [8.053977012634277, 13.485422134399414, 0.0], [7.96048641204834, 14.389164924621582, 0.0], [7.866995811462402, 15.29290771484375, 0.0], [7.773505210876465, 16.1966495513916, 0.0], [7.680014610290527, 17.100393295288086, 0.0], [9.647152900695801, 7.269974231719971, 0.0], [9.546470642089844, 8.161011695861816, 0.0], [9.445788383483887, 9.05204963684082, 0.0], [9.34510612487793, 9.943086624145508, 0.0], [9.244423866271973, 10.834124565124512, 0.0], [9.143742561340332, 11.7251615524292, 0.0], [9.043060302734375, 12.616199493408203, 0.0], [8.942378044128418, 13.507237434387207, 0.0], [8.841695785522461, 14.398274421691895, 0.0], [8.741013526916504, 15.289312362670898, 0.0], [8.640331268310547, 16.180349349975586, 0.0], [8.53964900970459, 17.071386337280273, 0.0], [10.585894584655762, 7.380724906921387, 0.0], [10.478020668029785, 8.25905704498291, 0.0], [10.370147705078125, 9.137389183044434, 0.0], [10.262273788452148, 10.015722274780273, 0.0], [10.154399871826172, 10.894054412841797, 0.0], [10.046525955200195, 11.77238655090332, 0.0], [9.938652038574219, 12.650718688964844, 0.0], [9.830778121948242, 13.529051780700684, 0.0], [9.722904205322266, 14.407383918762207, 0.0], [9.615030288696289, 15.28571605682373, 0.0], [9.507157325744629, 16.16404914855957, 0.0], [9.399283409118652, 17.042381286621094, 0.0], [11.524636268615723, 7.4914751052856445, 0.0], [11.409571647644043, 8.357102394104004, 0.0], [11.294506072998047, 9.222729682922363, 0.0], [11.179440498352051, 10.088356971740723, 0.0], [11.064374923706055, 10.953984260559082, 0.0], [10.949309349060059, 11.819611549377441, 0.0], [10.834244728088379, 12.6852388381958, 0.0], [10.719179153442383, 13.55086612701416, 0.0], [10.604113578796387, 14.41649341583252, 0.0], [10.489048004150391, 15.282120704650879, 0.0], [10.373982429504395, 16.147747039794922, 0.0], [10.258917808532715, 17.013374328613281, 0.0], [12.463377952575684, 7.6022257804870605, 0.0], [12.341121673583984, 8.455147743225098, 0.0], [12.218864440917969, 9.308070182800293, 0.0], [12.096607208251953, 10.160991668701172, 0.0], [11.974349975585937, 11.013914108276367, 0.0], [11.852093696594238, 11.866836547851563, 0.0], [11.729836463928223, 12.719758033752441, 0.0], [11.607579231262207, 13.572680473327637, 0.0], [11.485322952270508, 14.425602912902832, 0.0], [11.363065719604492, 15.278524398803711, 0.0], [11.240808486938477, 16.131446838378906, 0.0], [11.118551254272461, 16.9843692779541, 0.0], [13.402119636535645, 7.712975978851318, 0.0], [13.272671699523926, 8.553193092346191, 0.0], [13.143222808837891, 9.393409729003906, 0.0], [13.013773918151855, 10.233627319335937, 0.0], [12.884325981140137, 11.073843955993652, 0.0], [12.754877090454102, 11.914060592651367, 0.0], [12.625428199768066, 12.754278182983398, 0.0], [12.495980262756348, 13.594494819641113, 0.0], [12.366531372070313, 14.434711456298828, 0.0], [12.237083435058594, 15.274929046630859, 0.0], [12.107634544372559, 16.115146636962891, 0.0], [11.978185653686523, 16.955362319946289, 0.0], [14.340861320495605, 7.823726654052734, 0.0], [14.204221725463867, 8.651238441467285, 0.0], [14.067581176757812, 9.478750228881836, 0.0], [13.930941581726074, 10.306262016296387, 0.0], [13.79430103302002, 11.133773803710938, 0.0], [13.657661437988281, 11.961285591125488, 0.0], [13.521020889282227, 12.788797378540039, 0.0], [13.384380340576172, 13.61630916595459, 0.0], [13.247740745544434, 14.443820953369141, 0.0], [13.111100196838379, 15.271332740783691, 0.0], [12.974460601806641, 16.098844528198242, 0.0], [12.837820053100586, 16.926357269287109, 0.0], [15.279603004455566, 7.934476852416992, 0.0], [15.135771751403809, 8.749283790588379, 0.0], [14.991939544677734, 9.564090728759766, 0.0], [14.848108291625977, 10.378896713256836, 0.0], [14.704276084899902, 11.193703651428223, 0.0], [14.560444831848145, 12.008510589599609, 0.0], [14.41661262512207, 12.823317527770996, 0.0], [14.272781372070313, 13.638123512268066, 0.0], [14.128949165344238, 14.452930450439453, 0.0], [13.98511791229248, 15.26773738861084, 0.0], [13.841285705566406, 16.082544326782227, 0.0], [13.697454452514648, 16.897350311279297, 0.0], [16.218345642089844, 8.04522705078125, 0.0], [16.06732177734375, 8.847329139709473, 0.0], [15.916298866271973, 9.649430274963379, 0.0], [15.765275001525879, 10.451532363891602, 0.0], [15.614252090454102, 11.253633499145508, 0.0], [15.463228225708008, 12.05573558807373, 0.0], [15.31220531463623, 12.857836723327637, 0.0], [15.161182403564453, 13.659937858581543, 0.0], [15.010158538818359, 14.462039947509766, 0.0], [14.859135627746582, 15.264141082763672, 0.0], [14.708111763000488, 16.066242218017578, 0.0], [14.557088851928711, 16.868345260620117, 0.0], [17.157087326049805, 8.155978202819824, 0.0], [16.998872756958008, 8.945374488830566, 0.0], [16.840656280517578, 9.734770774841309, 0.0], [16.682441711425781, 10.524167060852051, 0.0], [16.524227142333984, 11.313563346862793, 0.0], [16.366012573242187, 12.102959632873535, 0.0], [16.207798004150391, 12.892355918884277, 0.0], [16.049583435058594, 13.681753158569336, 0.0], [15.89136791229248, 14.471149444580078, 0.0], [15.733152389526367, 15.26054573059082, 0.0], [15.57493782043457, 16.049942016601563, 0.0], [15.416723251342773, 16.839338302612305, 0.0], [18.095829010009766, 8.266728401184082, 0.0], [17.930421829223633, 9.04341983795166, 0.0], [17.7650146484375, 9.820111274719238, 0.0], [17.599609375, 10.5968017578125, 0.0], [17.434202194213867, 11.373493194580078, 0.0], [17.268796920776367, 12.150184631347656, 0.0], [17.103389739990234, 12.926876068115234, 0.0], [16.9379825592041, 13.703567504882812, 0.0], [16.7725772857666, 14.480258941650391, 0.0], [16.607170104980469, 15.256949424743652, 0.0], [16.441762924194336, 16.033641815185547, 0.0], [16.276357650756836, 16.810333251953125, 0.0]]
    face_vertices = [[13, 1, 0, 12], [14, 2, 1, 13], [15, 3, 2, 14], [16, 4, 3, 15], [17, 5, 4, 16], [18, 6, 5, 17], [19, 7, 6, 18], [20, 8, 7, 19], [21, 9, 8, 20], [22, 10, 9, 21], [23, 11, 10, 22], [25, 13, 12, 24], [26, 14, 13, 25], [27, 15, 14, 26], [28, 16, 15, 27], [29, 17, 16, 28], [30, 18, 17, 29], [31, 19, 18, 30], [32, 20, 19, 31], [33, 21, 20, 32], [34, 22, 21, 33], [35, 23, 22, 34], [37, 25, 24, 36], [38, 26, 25, 37], [39, 27, 26, 38], [40, 28, 27, 39], [41, 29, 28, 40], [42, 30, 29, 41], [43, 31, 30, 42], [44, 32, 31, 43], [45, 33, 32, 44], [46, 34, 33, 45], [47, 35, 34, 46], [49, 37, 36, 48], [50, 38, 37, 49], [51, 39, 38, 50], [52, 40, 39, 51], [53, 41, 40, 52], [54, 42, 41, 53], [55, 43, 42, 54], [56, 44, 43, 55], [57, 45, 44, 56], [58, 46, 45, 57], [59, 47, 46, 58], [61, 49, 48, 60], [62, 50, 49, 61], [63, 51, 50, 62], [64, 52, 51, 63], [65, 53, 52, 64], [66, 54, 53, 65], [67, 55, 54, 66], [68, 56, 55, 67], [69, 57, 56, 68], [70, 58, 57, 69], [71, 59, 58, 70], [73, 61, 60, 72], [74, 62, 61, 73], [75, 63, 62, 74], [76, 64, 63, 75], [77, 65, 64, 76], [78, 66, 65, 77], [79, 67, 66, 78], [80, 68, 67, 79], [81, 69, 68, 80], [82, 70, 69, 81], [83, 71, 70, 82], [85, 73, 72, 84], [86, 74, 73, 85], [87, 75, 74, 86], [88, 76, 75, 87], [89, 77, 76, 88], [90, 78, 77, 89], [91, 79, 78, 90], [92, 80, 79, 91], [93, 81, 80, 92], [94, 82, 81, 93], [95, 83, 82, 94], [97, 85, 84, 96], [98, 86, 85, 97], [99, 87, 86, 98], [100, 88, 87, 99], [101, 89, 88, 100], [102, 90, 89, 101], [103, 91, 90, 102], [104, 92, 91, 103], [105, 93, 92, 104], [106, 94, 93, 105], [107, 95, 94, 106], [109, 97, 96, 108], [110, 98, 97, 109], [111, 99, 98, 110], [112, 100, 99, 111], [113, 101, 100, 112], [114, 102, 101, 113], [115, 103, 102, 114], [116, 104, 103, 115], [117, 105, 104, 116], [118, 106, 105, 117], [119, 107, 106, 118], [121, 109, 108, 120], [122, 110, 109, 121], [123, 111, 110, 122], [124, 112, 111, 123], [125, 113, 112, 124], [126, 114, 113, 125], [127, 115, 114, 126], [128, 116, 115, 127], [129, 117, 116, 128], [130, 118, 117, 129], [131, 119, 118, 130], [133, 121, 120, 132], [134, 122, 121, 133], [135, 123, 122, 134], [136, 124, 123, 135], [137, 125, 124, 136], [138, 126, 125, 137], [139, 127, 126, 138], [140, 128, 127, 139], [141, 129, 128, 140], [142, 130, 129, 141], [143, 131, 130, 142], [145, 133, 132, 144], [146, 134, 133, 145], [147, 135, 134, 146], [148, 136, 135, 147], [149, 137, 136, 148], [150, 138, 137, 149], [151, 139, 138, 150], [152, 140, 139, 151], [153, 141, 140, 152], [154, 142, 141, 153], [155, 143, 142, 154], [157, 145, 144, 156], [158, 146, 145, 157], [159, 147, 146, 158], [160, 148, 147, 159], [161, 149, 148, 160], [162, 150, 149, 161], [163, 151, 150, 162], [164, 152, 151, 163], [165, 153, 152, 164], [166, 154, 153, 165], [167, 155, 154, 166], [169, 157, 156, 168], [170, 158, 157, 169], [171, 159, 158, 170], [172, 160, 159, 171], [173, 161, 160, 172], [174, 162, 161, 173], [175, 163, 162, 174], [176, 164, 163, 175], [177, 165, 164, 176], [178, 166, 165, 177], [179, 167, 166, 178], [181, 169, 168, 180], [182, 170, 169, 181], [183, 171, 170, 182], [184, 172, 171, 183], [185, 173, 172, 184], [186, 174, 173, 185], [187, 175, 174, 186], [188, 176, 175, 187], [189, 177, 176, 188], [190, 178, 177, 189], [191, 179, 178, 190]]
    mesh = Mesh.from_vertices_and_faces(vertices, face_vertices)

    edge_paths = [[[120, 121], [121, 122], [122, 123], [123, 124]], [[39, 40], [40, 52], [52, 64], [64, 76], [76, 75], [75, 74], [74, 73], [73, 61], [61, 49], [49, 37], [37, 38], [38, 39]], [[105, 117], [117, 129], [129, 141], [141, 153]], [[54, 55], [55, 56], [56, 57], [57, 58], [58, 59]], [[6, 18], [18, 30], [30, 42], [42, 54]], [[54, 66], [66, 78], [78, 90], [90, 102], [102, 114], [114, 126], [126, 138], [138, 150], [150, 162], [162, 174], [174, 186]]]

    print mesh

    # if there are several edge paths for unwelding that come at the same point (e.g. T-junction), they must be split at this point
    for edge_path in edge_paths:
        unweld_mesh_along_edge_path(mesh, edge_path)
    print mesh