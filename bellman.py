import networkx as nx
import random

class NegativeWeightFinder:
    __slots__ = ['graph', 'predecessor_to', 'distance_to', 'seen_nodes']

    def __init__(self, graph: nx.Graph):
        self.graph = graph
        self.predecessor_to = {}
        self.distance_to = {}

        self.seen_nodes = set()

    def reset_all_but_graph(self):
        """
        Call this to look for opportunities after updating the graph
        """
        self.predecessor_to = {}
        self.distance_to = {}

        self.seen_nodes = set()

    def initialize(self, source):
        for node in self.graph:
            # Initialize all distance_to values to infinity and all predecessor_to values to None
            self.distance_to[node] = float('Inf')
            self.predecessor_to[node] = None

        # The distance from any node to (itself) == 0
        self.distance_to[source] = 0


    def bellman_ford(self, source='WETH', unique_paths=True):
        """
        Finds arbitrage opportunities in self.graph and yields them
        Parameters
        ----------
        source
            A node (currency) in self.graph. Opportunities will be yielded only if they are "reachable" from source.
            Reachable means that a series of trades can be executed to buy one of the currencies in the opportunity.
            For the most part, it does not matter what the value of source is, because typically any currency can be
            reached from any other via only a few trades.
        unique_paths : bool
            unique_paths: If True, each opportunity is not yielded more than once
        :return: a generator of profitable (negatively-weighted) arbitrage paths in self.graph
        """
        self.initialize(source)

        # After len(graph) - 1 passes, algorithm is complete.
        for i in range(len(self.graph) - 1):
            # for each node in the graph, test if the distance to each of its siblings is shorter by going from
            # source->base_currency + base_currency->quote_currency
            for edge in self.graph.edges(data=True):
                self.relax(edge)

        for edge in self.graph.edges(data=True):
            if self.distance_to[edge[0]] + edge[2]['weight'] < self.distance_to[edge[1]]:
                if unique_paths and edge[1] in self.seen_nodes:
                    continue
                path = self._retrace_negative_cycle(edge[1], unique_paths)
                if path is None or path == (None, None):
                    continue
                yield path

    def relax(self, edge):
        if self.distance_to[edge[0]] + edge[2]['weight'] < self.distance_to[edge[1]]:
            self.distance_to[edge[1]] = self.distance_to[edge[0]] + edge[2]['weight']
            self.predecessor_to[edge[1]] = edge[0]

        return True
    
    def _retrace_negative_cycle(self, start, unique_paths):
        """
        Retraces an arbitrage opportunity (negative cycle) which a currency can reach and returns it.
        Parameters
        ----------
        start
            A node (currency) from which it is known an arbitrage opportunity is reachable
        unique_paths : bool
            unique_paths: If True, no duplicate opportunities are returned
        Returns
        -------
        list
            An arbitrage opportunity reachable from start. Value is None if seen_nodes is True and a
            duplicate opportunity would be returned.
        """
        arbitrage_loop = [start]
        prior_node = start
        while True:
            prior_node = self.predecessor_to[prior_node]
            # if negative cycle is complete
            if prior_node in arbitrage_loop:
                arbitrage_loop = arbitrage_loop[:last_index_in_list(arbitrage_loop, prior_node) + 1]
                arbitrage_loop.insert(0, prior_node)
                return arbitrage_loop

            # because if prior_node is in arbitrage_loop prior_node must be in self.seen_nodes. thus, this conditional
            # must proceed checking if prior_node is in arbitrage_loop
            if unique_paths and prior_node in self.seen_nodes:
                return None

            arbitrage_loop.insert(0, prior_node)
            self.seen_nodes.add(prior_node)





# Speedup

    def bellman_ford_randomized_speedup(self, source='WETH', unique_paths=True):
        # Initialize our graph weights
        self.initialize(source)

        # Create a dictionary for node to value pairings, as well as value to node
        # pairings for easy numerical ordering
        node_values, value_nodes = self.randomized_nodes()
        
        # Keep track of nodes where D[node] was changed in the previoius iteration.
        # Once no nodes have been changed in the previous iteration, the algorithm is
        # completed.
        changed_list = set(source)
        while changed_list:

            # We need to keep track of node v in any (u, v) edges where D[v] is updated
            # in the current iteration
            changed_list_neighbors = set()

            # For each node in ASCENDING numerical order, relax any 
            # edge (u, v) where v holds a greater node value than u
            # only if u is in the changed list, or D[v] has been changed
            # since the start of the iteration
            for i in range(self.graph.number_of_nodes()):
                u = value_nodes[i]
                u_value = node_values[u]
                for v in self.graph[u]:
                    if u in changed_list or v in changed_list_neighbors:
                        if node_values[v] > u_value:
                            weight = self.graph.edges[u, v]['weight']
                            if self.relax(u, v, weight):
                                changed_list_neighbors.add(v)

            # For each node in DECREASING numerical order, relax any
            # edge (u, v) where v holds a lesser node value than u
            # only if u is in the changed list, or D[v] has been changed
            # since the start of the iteration
            for i in range(self.graph.num_of_nodes()-1, -1, -1):
                u = value_nodes[i]
                u_value = node_values[u]
                for v in self.graph[u]:
                    if u in changed_list or v in changed_list_neighbors:
                        if node_values[v] < u_value:
                            weight = self.graph.edges[u, v]['weight']
                            if self.relax(u, v, weight):
                                changed_list_neighbors.add(v)
        
        # Carry on like regular Bellman-Ford, completing one more pass to detect negative cycles
        for edge in self.graph.edges(data=True):
            if self.distance_to[edge[0]] + edge[2]['weight'] < self.distance_to[edge[1]]:
                if unique_paths and edge[1] in self.seen_nodes:
                    continue
                path = self._retrace_negative_cycle(edge[1], unique_paths)
                if path is None or path == (None, None):
                    continue
                yield path
    
        return None

    def randomized_nodes(self):
        num_of_nodes = self.graph.number_of_nodes()

        nodes = list(self.graph.nodes)
        numbers = [i for i in range(num_of_nodes)]
        random.shuffle(numbers)

        # Return a dictionary of node : node value key/value pairs
        return dict(zip(nodes, numbers)), dict(zip(numbers, nodes))

    def relax(self, node, neighbor, weight):
        if self.distance_to[node] + weight < self.distance_to[neighbor]:
            self.distance_to[neighbor] = self.distance_to[node] + weight
            self.predecessor_to[neighbor] = node
            return True
        return False
        
def last_index_in_list(lst, element):
    return len(lst) - next(i for i, v in enumerate(reversed(lst), 1) if v == element)