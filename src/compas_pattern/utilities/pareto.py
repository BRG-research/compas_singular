__all__ = []


def extract_pareto_indices(data):
	"""Get the Pareto front from data. The performances are to be minimised.
	If the metrics must be maximised, take the opposite X <- -X.

	Inputs
	------
	data : list
		A list of iterables storing the performance data.

	Returns
	-------
	list
		List of indices of Pareto front in data.

	References
	----------
	.. [1] Wikipedia. *Multi-objective optimization*.
		   Available at: https://en.wikipedia.org/wiki/Multi-objective_optimization.
	"""

	return [i for i, Xi in enumerate(data) if len([Xj for Xj in data if is_dominating(Xj, Xi)]) == 0]

def is_dominating(X1, X2):
	"""Check if a design (X1) is dominating another one (X2).
	To dominate another design, a design must have all its metrics below or equal and one strictly below the metrics of the other design.
	If the metrics must be maximised, take the opposite X <- -X.
	
	Inputs
	------
	X1 : iterable
		A design to test if is dominating.
	X12 : iterable
		A design to test if is dominated.

	Returns
	-------
	bool
		True if is dominating, False otherwise

	References
	----------
	.. [1] Wikipedia. *Multi-objective optimization*.
		   Available at: https://en.wikipedia.org/wiki/Multi-objective_optimization.
	"""

	return all([X1k <= X2k for X1k, X2k in zip(X1, X2)]) and any([X1k < X2k for X1k, X2k in zip(X1, X2)])


# ==============================================================================
# Main
# ==============================================================================

if __name__ == '__main__':

	data = [[1.3350193755401125, 4.163180549186835, 0.0], [3.2381265372057433, 4.372844897505931, 0.0], [2.2543169027853764, 3.566443557817104, 0.0], [4.254192225213666, 3.324523155910456, 0.0], [1.5608117506529842, 3.114858807591361, 0.0], [2.9155660013302125, 2.7922982717158304, 0.0], [3.980015769719463, 2.437481682252747, 0.0], [2.641389545836012, 1.889128771264345, 0.0], [3.721967341019039, 1.5826962621825906, 0.0], [4.496112627120313, 4.308332790330825, 0.0], [1.7220920185907498, 4.711533460175238, 0.0], [4.592880787882973, 1.7439765301203565, 0.0]]

	for i in extract_pareto_indices(data):
		print(data[i])


