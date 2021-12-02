from bellman_multi_graph import bellman_ford_multi, bellman_ford_multi_speedup
from graph_constructor import construct_graph
from math import exp
import time

#experimental variables
AMT_MARKETS = 2
SPEEDUP = True

def calc_profit(g, path):
    ratio = 1
    frm = 0
    to = 1
    while to < len(path):
        ratio *= exp(-g[path[frm]][path[to]]['weight'])
        frm = to
        to += 1
    return ratio

start = time.time()
multi_graph = construct_graph(AMT_MARKETS, load_state=True)
if SPEEDUP:
    g, paths = bellman_ford_multi_speedup(multi_graph, "WETH", unique_paths=True)
else:
    g, paths = bellman_ford_multi(multi_graph, "WETH", unique_paths=True)
end = time.time()
paths = list(paths)
open_file = None
if (AMT_MARKETS == 2) and not SPEEDUP:
    open_file = open("bfamt2.txt", "w")
if (AMT_MARKETS == 3) and not SPEEDUP:
    open_file = open("bfamt3.txt", "w")
if (AMT_MARKETS == 4) and not SPEEDUP:
    open_file = open("bfamt4.txt", "w")
if (AMT_MARKETS == 5) and not SPEEDUP:
    open_file = open("bfamt5.txt", "w")
if (AMT_MARKETS == 2) and SPEEDUP:
    open_file = open("bfspdamt2.txt", "w")
if (AMT_MARKETS == 3) and SPEEDUP:
    open_file = open("bfspdamt3.txt", "w")
if (AMT_MARKETS == 4) and SPEEDUP:
    open_file = open("bfspdamt4.txt", "w")
if (AMT_MARKETS == 5) and SPEEDUP:
    open_file = open("bfspdamt5.txt", "w")

for path in paths:
    if path:
        profit = calc_profit(g, path)
        if profit < 2:
            open_file.write(str((path, profit))+"\n")
            print(path, profit)
time_str = "Time Elapsed: " + str(end-start) + "s"
print(time_str)
open_file.write(time_str)
open_file.close()

