from __future__ import print_function
from __future__ import absolute_import
from __future__ import division

__all__ = [
    'extract_pareto_indices',
    'is_dominating'

]


def extract_pareto_indices(data, k=1.0):
    """Get the Pareto front from data. The performances are to be minimised.
    If the metrics must be maximised, take the opposite X <- -X and the inverse k <- 1/k.

    Parameters
    ----------
    data : list
        A list of iterables storing the performance data.
    k : float, optional
        Parameter for weak domination. Default is 1.0.

    Returns
    -------
    list
        List of indices of Pareto front in data.

    References
    ----------
    .. [1] Wikipedia. *Multi-objective optimization*.
           Available at: https://en.wikipedia.org/wiki/Multi-objective_optimization.
    """

    return [i for i, Xi in enumerate(data) if len([Xj for Xj in data if is_dominating(Xj, Xi, 1/k)]) == 0]


def is_dominating(X1, X2, k=1.0):
    """Check if a design (X1) is dominating another one (X2).
    To dominate another design, a design must have all its metrics below or equal and one strictly below the metrics of the other design.
    A weak domination is allowed for values of k below 1.0.
    If the metrics must be maximised, take the opposite X <- -X and the inverse k <- 1/k.

    Parameters
    ----------
    X1 : iterable
        A design to test if is dominating.
    X12 : iterable
        A design to test if is dominated.
    k : float, optional
        Parameter for weak domination. Default if 1.0.

    Returns
    -------
    bool
        True if is dominating, False otherwise

    References
    ----------
    .. [1] Wikipedia. *Multi-objective optimization*.
           Available at: https://en.wikipedia.org/wiki/Multi-objective_optimization.
    """

    return all([k * X1k <= X2k for X1k, X2k in zip(X1, X2)]) and any([k * X1k < X2k for X1k, X2k in zip(X1, X2)])


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':
    pass
