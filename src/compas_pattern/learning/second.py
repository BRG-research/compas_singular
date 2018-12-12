# Author: Narine Kokhlikyan <narine@slice.com>
# License: BSD

print(__doc__)

import numpy as np
import matplotlib.pyplot as plt

from matplotlib.ticker import NullFormatter
from sklearn import manifold, datasets
from time import time

n_samples = 300
n_components = 2
(fig, subplots) = plt.subplots(1, 2, figsize=(4, 2))
perplexities = [5]

# X, y = datasets.make_circles(n_samples=n_samples, factor=.5, noise=.05)
# print X
# print y
# red = y == 0
# green = y == 1

X = np.random.rand(2, 5)
y = np.random.rand(10)
for i in y:
	i = int(i + 1)
print X, y
red = y < 0.5
green = y >= 0.5
print red
print green

ax = subplots[0]
ax.scatter(X[red, 0], X[red, 1], c="r")
ax.scatter(X[green, 0], X[green, 1], c="g")
ax.xaxis.set_major_formatter(NullFormatter())
ax.yaxis.set_major_formatter(NullFormatter())
plt.axis('tight')

for i, perplexity in enumerate(perplexities):
    ax = subplots[i + 1]

    t0 = time()
    tsne = manifold.TSNE(n_components=n_components, init='random',
                         random_state=0, perplexity=perplexity)
    Y = tsne.fit_transform(X)
    t1 = time()
    print("circles, perplexity=%d in %.2g sec" % (perplexity, t1 - t0))
    ax.set_title("Perplexity=%d" % perplexity)
    ax.scatter(Y[red, 0], Y[red, 1], c="r")
    ax.scatter(Y[green, 0], Y[green, 1], c="g")
    ax.xaxis.set_major_formatter(NullFormatter())
    ax.yaxis.set_major_formatter(NullFormatter())
    ax.axis('tight')

# # Another example using s-curve
# X, color = datasets.samples_generator.make_s_curve(n_samples, random_state=0)

# ax = subplots[1][0]
# ax.scatter(X[:, 0], X[:, 2], c=color, cmap=plt.cm.viridis)
# ax.xaxis.set_major_formatter(NullFormatter())
# ax.yaxis.set_major_formatter(NullFormatter())

# for i, perplexity in enumerate(perplexities):
#     ax = subplots[1][i + 1]

#     t0 = time()
#     tsne = manifold.TSNE(n_components=n_components, init='random',
#                          random_state=0, perplexity=perplexity)
#     Y = tsne.fit_transform(X)
#     t1 = time()
#     print("S-curve, perplexity=%d in %.2g sec" % (perplexity, t1 - t0))

#     ax.set_title("Perplexity=%d" % perplexity)
#     ax.scatter(Y[:, 0], Y[:, 1], c=color, cmap=plt.cm.viridis)
#     ax.xaxis.set_major_formatter(NullFormatter())
#     ax.yaxis.set_major_formatter(NullFormatter())
#     ax.axis('tight')


# # Another example using a 2D uniform grid
# x = np.linspace(0, 1, int(np.sqrt(n_samples)))
# xx, yy = np.meshgrid(x, x)
# X = np.hstack([
#     xx.ravel().reshape(-1, 1),
#     yy.ravel().reshape(-1, 1),
# ])
# color = xx.ravel()
# ax = subplots[2][0]
# ax.scatter(X[:, 0], X[:, 1], c=color, cmap=plt.cm.viridis)
# ax.xaxis.set_major_formatter(NullFormatter())
# ax.yaxis.set_major_formatter(NullFormatter())

# for i, perplexity in enumerate(perplexities):
#     ax = subplots[2][i + 1]

#     t0 = time()
#     tsne = manifold.TSNE(n_components=n_components, init='random',
#                          random_state=0, perplexity=perplexity)
#     Y = tsne.fit_transform(X)
#     t1 = time()
#     print("uniform grid, perplexity=%d in %.2g sec" % (perplexity, t1 - t0))

#     ax.set_title("Perplexity=%d" % perplexity)
#     ax.scatter(Y[:, 0], Y[:, 1], c=color, cmap=plt.cm.viridis)
#     ax.xaxis.set_major_formatter(NullFormatter())
#     ax.yaxis.set_major_formatter(NullFormatter())
#     ax.axis('tight')


plt.show()