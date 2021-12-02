import networkx as nx
from uniswap import uni_sushi_swap, kyber, dydx, univ3
import pickle
from math import log

def construct_graph(num_networks, load_state=False):
    uni_tups = []
    sushi_tups = []
    kyber_tups = []
    dydx_tups = []
    v3_tups = []
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
        if num_networks > 4:
            open_file = open("univ3.pkl", "rb")
            v3_tups = pickle.load(open_file)
            open_file.close()
    else:
        print("loading sushi prices...")
        sushi_tups = uni_sushi_swap("https://api.thegraph.com/subgraphs/name/sushiswap/exchange")
        print("DONE")
        print("loading uni prices...")
        uni_tups = uni_sushi_swap("https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2")
        print("DONE")
        if num_networks > 2:
            print("loading dydx prices...")
            dydx_tups = dydx()
            print("DONE")
        if num_networks > 3:
            print("loading kyber prices...")
            kyber_tups = kyber()
            print("DONE")
        if num_networks > 4:
            print("loading univ3 prices...")
            v3_tups = univ3()
            print("DONE")
    
    graph = nx.MultiDiGraph()
    
    for tup in sushi_tups:
        if not graph.__contains__(tup[0]):
            graph.add_node(tup[0])
        if not graph.__contains__(tup[1]):
            graph.add_node(tup[1])
        graph.add_edge(tup[0], tup[1], weight=(log(float(tup[3]))*(-1)), market=tup[4])
        graph.add_edge(tup[1], tup[0], weight=(log(float(tup[2]))*(-1)), market=tup[4])
    for tup in uni_tups:
        if not graph.__contains__(tup[0]):
            graph.add_node(tup[0])
        if not graph.__contains__(tup[1]):
            graph.add_node(tup[1])
        graph.add_edge(tup[0], tup[1], weight=log(float(tup[3]))*(-1), market=tup[4])
        graph.add_edge(tup[1], tup[0], weight=(log(float(tup[2]))*(-1)), market=tup[4])
    if num_networks > 2:
        
        for tup in dydx_tups:
            if not graph.__contains__(tup[0]):
                graph.add_node(tup[0])
            if not graph.__contains__(tup[1]):
                graph.add_node(tup[1])
            graph.add_edge(tup[0], tup[1], weight=(log(float(tup[3]))*(-1)), market=tup[4])
            graph.add_edge(tup[1], tup[0], weight=(log(float(tup[2]))*(-1)), market=tup[4])

    if num_networks > 3:
        
        for tup in kyber_tups:
            if not graph.__contains__(tup[0]):
                graph.add_node(tup[0])
            if not graph.__contains__(tup[1]):
                graph.add_node(tup[1])
            graph.add_edge(tup[0], tup[1], weight=(log(float(tup[3]))*(-1)), market=tup[4])
            graph.add_edge(tup[1], tup[0], weight=(log(float(tup[2]))*(-1)), market=tup[4])
    
    if num_networks > 4:
        for tup in v3_tups:
            if not graph.__contains__(tup[0]):
                graph.add_node(tup[0])
            if not graph.__contains__(tup[1]):
                graph.add_node(tup[1])
            graph.add_edge(tup[0], tup[1], weight=(log(float(tup[3]))*(-1)), market=tup[4])
            graph.add_edge(tup[1], tup[0], weight=(log(float(tup[2]))*(-1)), market=tup[4])

    #this is to record the last market state if we just requeried it
    if not load_state:
        wts = graph.edges.data()
        open_file = open("wts.txt", "w")
        open_file.write(wts.__str__())
        open_file.close()

    return graph