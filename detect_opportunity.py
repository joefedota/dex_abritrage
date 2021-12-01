from bellman_multi_graph import NegativeWeightFinderMulti
from graph_constructor import construct_graph

multi_graph = construct_graph(4, load_state=True)
NWFM = NegativeWeightFinderMulti(multi_graph)
for path in NWFM.bellman_ford(source="WETH", unique_paths=True):
    if path:
        print(path)