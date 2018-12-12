from sklearn import manifold
import numpy as np

def manifold_learning_xfunc(method, n_neighbours, number, dimension, min_value, max_value):

    data = random_data(number, dimension, min_value, max_value)
    data_map = manifold_learning(method, n_neighbours, data)

    data.tolist()
    data_map.tolist()

    # print data
    # print data_map

    return data, data_map

def manifold_learning(method, n_neighbours, data):

    return manifold.LocallyLinearEmbedding(n_neighbours, 2, method=method).fit_transform(data).T
    
def random_data(number, dimension, min_value, max_value):

    data = np.random.rand(number, dimension) * (max_value + 1 - min_value) + min_value

    data.astype(int)

    return data

manifold_learning_xfunc('standard', 10, 100, 5, 1, 10)