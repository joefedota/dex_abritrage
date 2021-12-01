import networkx as nx
from uniswap import uni_sushi_swap, kyber, dydx
import pickle
from math import log

def construct_graph(num_networks, load_state=False):
    uni_tups = []
    sushi_tups = []
    kyber_tups = []
    dydx_tups = []
    #sushi_tups = uni_sushi_swap("https://api.thegraph.com/subgraphs/name/sushiswap/exchange")
    #uni_tups = uni_sushi_swap("https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2")
    #kyber_tups = []
    if load_state:
        open_file = open("sushi.pkl", "rb")
        sushi_tups = pickle.load(open_file)
        open_file.close()
        #print(sushi_tups)
        open_file = open("uni.pkl", "rb")
        uni_tups = pickle.load(open_file)
        open_file.close()
        if num_networks > 2:
            open_file = open("dydx.pkl", "rb")
            dydx_tups = pickle.load(open_file)
            open_file.close()
        if num_networks > 3:
            open_file = open("kyber.pkl", "rb")
            kyber_tups = pickle.load(open_file)
            open_file.close()
    else:
        sushi_tups = uni_sushi_swap("https://api.thegraph.com/subgraphs/name/sushiswap/exchange")
        uni_tups = uni_sushi_swap("https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2")
        if num_networks > 2:
            dydx_tups = dydx()
        if num_networks > 3:
            kyber_tups = kyber()
    
    
    graph = nx.MultiDiGraph()
    
    for tup in sushi_tups:
        if not graph.__contains__(tup[0]):
            graph.add_node(tup[0])
        if not graph.__contains__(tup[1]):
            graph.add_node(tup[1])
        graph.add_edge(tup[0], tup[1], weight=(log(float(tup[3]))*(-1)))
        graph.add_edge(tup[1], tup[0], weight=(log(float(tup[2]))*(-1)))
    for tup in uni_tups:
        if not graph.__contains__(tup[0]):
            graph.add_node(tup[0])
        if not graph.__contains__(tup[1]):
            graph.add_node(tup[1])
        graph.add_edge(tup[0], tup[1], weight=log(float(tup[3]))*(-1))
        graph.add_edge(tup[1], tup[0], weight=(log(float(tup[2]))*(-1)))
    if num_networks > 2:
        for tup in dydx_tups:
            if not graph.__contains__(tup[0]):
                graph.add_node(tup[0])
            if not graph.__contains__(tup[1]):
                graph.add_node(tup[1])
            graph.add_edge(tup[0], tup[1], weight=(log(float(tup[2]))*(-1)))
            graph.add_edge(tup[1], tup[0], weight=(log(float(tup[2]))*(-1)))
    if num_networks > 3:
        for tup in kyber_tups:
            if not graph.__contains__(tup[0]):
                graph.add_node(tup[0])
            if not graph.__contains__(tup[1]):
                graph.add_node(tup[1])
            graph.add_edge(tup[0], tup[1], weight=(log(float(tup[2]))*(-1)))
            graph.add_edge(tup[1], tup[0], weight=(log(float(tup[2]))*(-1)))
    #pass the original value for the prices into the graph then have jakes 
    # algo convert to negative logs in flight, that way can traverse the 
    #discovered path to find profit
    return graph
'''
g = construct_graph(4, load_state=True)
wts = nx.get_edge_attributes(g,'weight')
open_file = open("wts.txt", "w")
open_file.write(wts.__str__())
open_file.close()'''