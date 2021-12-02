from bellman_multi_graph import bellman_ford_multi
from graph_constructor import construct_graph
from math import exp

def calc_profit(g, path):
    ratio = 1
    frm = 0
    to = 1
    while to < len(path):
        ratio *= exp(-g[path[frm]][path[to]]['weight'])
        frm = to
        to += 1
    return ratio

multi_graph = construct_graph(2, load_state=True)
g, paths = bellman_ford_multi(multi_graph, "WETH", unique_paths=True)
paths = list(paths)
for path in paths:
    if path:
        print(path, calc_profit(g, path))

