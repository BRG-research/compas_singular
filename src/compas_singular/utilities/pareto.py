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

    # import itertools as it
    # from compas.utilities import average

    # # data = [[1.3350193755401125, 4.163180549186835, 0.0], [3.2381265372057433, 4.372844897505931, 0.0], [2.2543169027853764, 3.566443557817104, 0.0], [4.254192225213666, 3.324523155910456, 0.0], [1.5608117506529842, 3.114858807591361, 0.0], [2.9155660013302125, 2.7922982717158304, 0.0], [3.980015769719463, 2.437481682252747, 0.0], [2.641389545836012, 1.889128771264345, 0.0], [3.721967341019039, 1.5826962621825906, 0.0], [4.496112627120313, 4.308332790330825, 0.0], [1.7220920185907498, 4.711533460175238, 0.0], [4.592880787882973, 1.7439765301203565, 0.0]]

    # # for i in extract_pareto_indices(data):
    # # 	print(data[i])

    # # 	data = [
    # # 		[	0.8	,	0.71	,	0.24	,	1	,	0.72	,	0.7	],
    # # 		[	0.64	,	0.88	,	0.19	,	0.85	,	0.8	,	0.71	],
    # # 		[	0.92	,	0.6	,	0.54	,	0.82	,	0.98	,	0.76	],
    # # 		[	0.82	,	0.61	,	0.3	,	0.86	,	0.97	,	0.8	],
    # # 		[	0.84	,	0.86	,	0.52	,	0.84	,	0.71	,	0.67	],
    # # 		[	0.84	,	1	,	1	,	0.84	,	0.63	,	1	],
    # # 		[	0.87	,	0.44	,	0.33	,	0.6	,	0.44	,	0.8	],
    # # 		[	0.81	,	0.64	,	0.38	,	0.78	,	0.81	,	0.72	],
    # # 		[	1	,	0.38	,	0.74	,	0.71	,	0.55	,	0.79	],
    # # 		[	0.8	,	0.51	,	0.39	,	0.65	,	0.83	,	0.71	],
    # # 		[	0.87	,	0.76	,	0.42	,	0.69	,	1	,	0.8	],
    # # 		[	0.81	,	0.42	,	0.35	,	0.64	,	0.32	,	0.72	],
    # # 		[	0.87	,	0.35	,	0.41	,	0.62	,	0.31	,	0.81	],
    # # 		[	0.92	,	0.43	,	0.39	,	0.62	,	0.28	,	0.84	],
    # # 		[	0.9	,	0.45	,	0.27	,	0.5	,	0.28	,	0.84	],
    # # ]

    # # 	print(extract_pareto_indices(data))
    # # 	for i in extract_pareto_indices(data):
    # # 		print(i, data[i])

    # # def average_nd(xs):
    # #     n = len(xs)
    # #     coord = zip(*xs)
    # #     return [sum(i) / n for i in coord]

    # # def distance_nd(x, y):
    # # 	return sum([(xi - yi) ** 2 for xi, yi in zip(x, y)]) ** 0.5

    # # def distance_one_to_group(x, ys):
    # # 	return average([distance_nd(x, y) for y in ys])

    # # def distance_group_to_group(xs, ys):
    # # 	return average([distance_one_to_group(x, ys) for x in xs])

    # # def average_distance_nd_xs(xs):
    # # 	if len(xs) == 1:
    # # 		return 0
    # # 	return average([distance_nd(x1, x2) for x1, x2 in it.combinations(xs, 2)])

    # # d1 = [296.64637117727239, 275.79114969003, 289.33043769195956, 301.2683145277262, 334.97227787447446, 289.99594460408707, 295.02079524854804, 279.84018527686044, 293.37435445490735, 300.07009031075125, 330.00952020345483, 359.28053052207946, 302.87776704249444, 281.60517417833159, 286.22095753778507, 280.39994708659435, 338.80635124061769, 313.32079280028609, 299.37584877092183, 283.34596124676352, 339.98497279123211, 280.3094173147623, 296.72046947967328, 354.0630439328479, 305.36887748198728, 326.45834472298571, 294.42134896882345, 281.74251042631494, 288.35727513726681, 294.38621438632049]
    # # d2 = [0.81922531091993622, 0.67158914986617169, 0.970031397623766, 1.2126650750794497, 1.2731576010238055, 1.439903981770412, 1.5513817228876092, 1.3115218873370647, 2.0309719792025507, 1.2920481155080379, 1.3307611705518418, 1.4732495978637543, 1.3442028984951118, 0.66147232178261983, 2.3980962944882998, 0.51730202142990556, 1.1610159762775032, 1.7264784091013543, 2.193717146975362, 0.55375756962510558, 0.42834518467563243, 0.56746935446809477, 0.90368504582948839, 2.033154688482466, 1.954569945584665, 0.44790598909339163, 0.95168248485206364, 0.65721293658749469, 0.7894073415045233, 0.87686394640019583]
    # # d3 = [0.21456729159953475, 0.2493760282525985, 0.3394005469808502, 0.49698462763439327, 0.77768847906514271, 0.5683596050199039, 0.83051358203018222, 0.66580549246762122, 1.1124537099176448, 0.53224547757935192, 0.66411601245324259, 0.91744708306494693, 0.43855022880973499, 0.48652080253932833, 1.3502301847044458, 0.30568896818204361, 0.2342916379234542, 0.49658078471472927, 0.86538950193908115, 0.41709778472605913, 0.25178201965948316, 0.22581711022627615, 0.74194299415425147, 0.58565767647599143, 0.64156872639203077, 0.29774352705719714, 0.70927133440528378, 0.56321686133331417, 0.64268623716860285, 0.5282822387314341]
    # # d4 = [0.0099281124009749193, 0.0061246520629641933, 0.0087496982413705574, 0.021283990195413938, 0.023009685349076079, 0.01758217109295512, 0.022523642819750823, 0.013350623206119291, 0.025269020559453296, 0.023086192789994183, 0.021590276430420604, 0.02291183769677653, 0.020692484608833741, 0.0061133316061373223, 0.033979671979631365, 0.0061715179321002213, 0.015676710231506592, 0.020862855503471108, 0.030492205034625453, 0.0034678420858817514, 0.0049654582598436655, 0.0051855592670257333, 0.012974729985092694, 0.019658952259684958, 0.021170571904323383, 0.0032053891126348879, 0.016971651126506167, 0.010704939188666407, 0.0078490911041736722, 0.018114588053916698]
    # # d5 = [68.983079481364044, 55.29443679558004, 71.743789095569241, 67.60640424957991, 116.43270363251371, 68.401053416807, 55.22858384648363, 59.532080172747321, 83.515177907367175, 67.51004560491748, 115.05937701825518, 97.428239051137083, 87.111083215361433, 38.267779900372346, 51.138946725696641, 29.01615529455956, 88.168025254363712, 75.576191723850769, 66.6051692602795, 48.278571481193836, 65.352181037316058, 43.084651434578291, 58.007761705523968, 130.2088725974024, 88.275846535186716, 70.485444427644524, 45.90216814926066, 47.150580894815405, 54.628556999466213, 44.715129321754588]
    # # ks = [False, False, False, False, False, False, False, True, True, True, True, False, True, True, True, False, False, False, False, True, True, True, True, True, True, True, False, True, True, True]
    # # data = [[i1, i3, i4, i5] for i1, i2, i3, i4, i5, k in zip(d1, d2, d3, d4, d5, ks)]

    # # for d in [d1, d2, d3, d4, d5, data]:
    # # 	del d[25]
    # # 	del d[22]
    # # 	del d[19]
    # # 	del d[13]

    # # groups = [
    # # 	list(range(0,1)),
    # # 	list(range(1,3)),
    # # 	list(range(3,8)),
    # # 	list(range(8,14)),
    # # 	list(range(14,18)),
    # # 	list(range(18,22)),
    # # 	list(range(22,24)),
    # # 	list(range(24,26))
    # # 	]

    # # s = [10, 9, 9, 8, 8, 8, 8, 8, 7, 7, 7, 7, 7, 7, 6, 6, 6, 6, 5, 5, 5, 5, 4, 4, 3, 3]
    # #print(len(d1), len(s))

    # # matrix = []
    # # for group_i in groups:
    # # 	row = []
    # # 	di = average_distance_nd_xs([[d1[i], d3[i], d4[i], d5[i]] for i in group_i])
    # # 	for group_j in groups:
    # # 		dj = average_distance_nd_xs([[d1[j], d3[j], d4[j], d5[j]] for j in group_j])
    # # 		if dj == 0:
    # # 			dij = float('inf')
    # # 		else:
    # # 			dij = di / dj
    # # 		row.append(dij)
    # # 	matrix.append(row)

    # # matrix = []
    # # for group_i in groups:
    # # 	row = []
    # # 	for group_j in groups:
    # # 		xi = [[d1[i], d3[i], d4[i], d5[i]] for i in group_i]
    # # 		xj = [[d1[j], d3[j], d4[j], d5[j]] for j in group_j]
    # # 		dij = distance_group_to_group(xi, xj)
    # # 		row.append(dij)
    # # 	matrix.append(row)

    # # print(matrix)

    # # for row in matrix:
    # #	print(row)

    # # dist_perf = []
    # # dist_topo = []
    # # for i in range(len(d1)):
    # # 	for j in range(len(d1)):
    # # 		if i != j:
    # # 			dist_perf.append(distance_nd([d1[i], d3[i], d4[i], d5[i]], [d1[j], d3[j], d4[j], d5[j]]))
    # # 			dist_topo.append(distance_nd([s[i]], [s[j]]))
    # # print(dist_perf)
    # # print(dist_topo)

    # # group_perf = []
    # # for group in groups:
    # # 	points = [[d1[i], d3[i], d4[i], d5[i]] for i in group]
    # # 	group_perf.append(average_nd(points))

    # # dist_perf = []
    # # dist_topo = []
    # # for i in range(len(groups)):
    # # 	for j in range(len(groups)):
    # # 		if i != j:
    # # 			dist_perf.append(distance_nd(group_perf[i], group_perf[j]))
    # # 			dist_topo.append(abs(i - j))
    # # print(dist_perf)
    # # print(dist_topo)

    # # x0 = [d1[0], d3[0], d4[0], d5[0]]
    # # for group in groups:
    # # 	print(average([distance_nd(x0, [d1[i], d3[i], d4[i], d5[i]]) for i in group]))

    # d1 = [	0.0911869860146109,	0.745864104547218,	0.677676087424328,	0.847978294852792,	0.800912100780209,	0.548942503247104,	0.354493419949552,
    #         0.971030241492185,	0.623932622211096,	1,	0.848675071041386,	0.772250905022578,	0.803339773437299,	0.506585405115783,	]
    # d2 = [	0.749271346387736,	0.40910950948532,	0.5946634173142,	0.385618195765887,	0.673784313971342,	0.415053863944384,	1,
    #         0.505152723745388,	0.385899740454552,	0.401781368580753,	0.402058353841261,	0.448066403511672,	0.433469394268571,	0.477343631561729,	]
    # d3 = [	0.914158388689134,	0.620292217685417,	0.275207203364008,	1,	0.538692181120117,	0.874550551526601,	0.660116399536839,
    #         0.34695898592236,	0.276206654884515,	0.220592357852398,	0.485523188494119,	0.607537022365775,	0.497638491071973,	0.512942592479737,	]
    # data = [[i2, i3] for i1, i2, i3 in zip(d1, d2, d3)]
    # print(extract_pareto_indices(data))
