from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

from compas_singular.datastructures.mesh_quad.grammar.add_strip import add_strip
from compas_singular.datastructures.mesh_quad.grammar.delete_strip import delete_strip

__all__ = ['Lizard']


class Lizard:

    def __init__(self, quad_mesh):
        self.lizard = None
        self.grow = False
        self.mesh = quad_mesh

    def initiate(self, tail=None, head=None):
        if tail in self.mesh.vertex and head in self.mesh.vertex and tail in self.mesh.vertex[head]:
            self.lizard = [head, tail]
        else:
            tail = list(self.mesh.vertices())[0]
            head = self.mesh.vertex_neighbors(tail)[0]
            self.lizard = [head, tail]

    def turn(self):
        nbrs = self.mesh.vertex_neighbors(self.lizard[0], ordered=True)
        i = nbrs.index(self.lizard[1])
        new_head = nbrs[i + 1 - len(nbrs)]
        self.lizard.insert(0, new_head)
        if not self.grow:
            del self.lizard[-1]

    def pivot(self):
        nbrs = self.mesh.vertex_neighbors(self.lizard[1], ordered=True)
        i = nbrs.index(self.lizard[0])
        new_head = nbrs[i + 1 - len(nbrs)]
        self.lizard[0] = new_head

    def add(self):
        if self.grow:
            n, old_vkeys_to_new_vkeys = add_strip(self.mesh, self.lizard[1:])
            head = old_vkeys_to_new_vkeys[self.lizard[0]] if self.lizard[0] in old_vkeys_to_new_vkeys else self.lizard[0]
            tail = old_vkeys_to_new_vkeys[self.lizard[1]]
            self.lizard = [head, tail]

        self.grow = not self.grow

    def delete(self):
        if self.grow:
            # use update polyedge
            print('Not Implemented')
            pass

        skey = self.mesh.edge_strip((self.lizard[0], self.lizard[1]))
        self.pivot()  # check that pivot ends along strip
        old_vkeys_to_new_vkeys = delete_strip(self.mesh, skey)
        self.lizard = [old_vkeys_to_new_vkeys[i] for i in self.lizard]  # specify one when old_vkeys_to_new_vkeys[i] is a tuple

    def from_vector_to_string(self, vector):
        string = []
        for i in range(len(vector) // 2):
            x, y = vector[2 * i: 2 * i + 2]
            if (x, y) == (0, 0):
                string.append('t')
            elif (x, y) == (0, 1):
                string.append('p')
            elif (x, y) == (1, 0):
                string.append('a')
            elif (x, y) == (1, 1):
                string.append('d')
        return string

    def from_string_to_vector(self, string):
        vector = []
        for k in string:
            if k == 't':
                vector += [0, 0]
            elif k == 'p':
                vector += [0, 1]
            elif k == 'a':
                vector += [1, 0]
            elif k == 'd':
                vector += [1, 1]
        return vector

    def from_string_to_rules(self, string):
        for k in string:
            if k == 't':
                self.turn()
            elif k == 'p':
                self.pivot()
            elif k == 'a':
                self.add()
            elif k == 'd':
                self.delete()


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass
