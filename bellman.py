import networkx as nx

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


    def bellman_ford(self, source='BTC', unique_paths=True):
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
        
def last_index_in_list(lst, element):
    next(i for i in reversed(range(len(lst))) if lst[i] == element)