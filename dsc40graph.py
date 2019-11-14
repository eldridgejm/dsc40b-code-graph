"""Efficient undirected and directed graph data structures."""


class _EdgeView:
    """Base class for views into a graph's edges."""

    def __init__(self, adj, number_of_edges):
        self._adj = adj
        self._number_of_edges = number_of_edges

    def __contains__(self, edge):
        """Perform an edge query.
        
        Average case time complexity: Theta(1)
        """
        u, v = edge
        try:
            return v in self._adj[u]
        except KeyError:
            return False

    def __len__(self):
        """The number of edges.

        Average case time complexity: Theta(1)
        """
        return self._number_of_edges


class _UndirectedEdgeView(_EdgeView):
    """A view into an undirected graph's edges."""

    def __iter__(self):
        """Iterate through the edges.

        Each edge in the graph is yielded exactly once as a pair whose order is
        arbitrary. That is, suppose that a graph has an edge between node 1 and
        node 2. Then the pair (1,2) may be yielded, or (2,1), but not both.

        Yields
        ------
        edge
            The edge as a pair of labels.

        """
        seen = set()

        for u, neighbors in self._adj.items():
            for v in neighbors:
                edge = frozenset((u, v))
                if edge not in seen:
                    seen.add(edge)
                    yield (u, v)
                else:
                    continue


class _DirectedEdgeView(_EdgeView):

    def __iter__(self):
        """Iterate through the edges.

        Yields
        ------
        edge
            The edge as an ordered pair of labels.

        """
        for u, neighbors in self._adj.items():
            for v in neighbors:
                yield (u, v)


class _Graph:
    """Base class for graph data structures."""

    def __init__(self, _edge_view_factory):
        self.adj = dict()
        self._number_of_edges = 0
        self._edge_view_factory = _edge_view_factory

    def add_node(self, label):
        """
        Add a node with the given label.

        Average case time complexity: Theta(1).

        Parameters
        ----------
        label
            The label of the node.

        """
        if label not in self.nodes:
            self.adj[label] = set()

    @property
    def nodes(self):
        """A view into the graph's nodes."""
        return self.adj.keys()

    @property
    def edges(self):
        """A view into the graph's edges."""
        return self._edge_view_factory(self.adj, self._number_of_edges)


class UndirectedGraph(_Graph):

    def __init__(self, _edge_view_factory=_UndirectedEdgeView):
        super().__init__(_edge_view_factory)

    def add_edge(self, u_label, v_label):
        """Add an edge to the graph.

        Average case time complexity: Theta(1).

        Parameters
        ----------
        u_label
            Label of one of the nodes in the edge.
        v_label
            Label of the other node in the edge.

        Notes
        -----
        If either of the nodes is not in the graph, the node is created.

        Raises
        ------
        ValueError
            If an attempt to add a self-loop is made. Undirected graphs do
            not have self-loops.

        """
        if u_label == v_label:
            raise ValueError('Undirected graphs have no self loops.')

        for x in {u_label, v_label}:
            if x not in self.adj:
                self.adj[x] = set()

        if (u_label, v_label) not in self.edges:
            self.adj[u_label].add(v_label)
            self.adj[v_label].add(u_label)
            self._number_of_edges += 1

    def remove_node(self, label):
        """Remove a node grom the graph.
        
        Parameters
        ----------
        label
            The label of the node to be removed.

        """
        if label not in self.nodes:
            return

        for neighbor in self.adj[label]:
            self.adj[neighbor].discard(label)
            self._number_of_edges -= 1

        del self.adj[label]

    def neighbors(self, u_label):
        return self.adj[u_label]


class DirectedGraph(_Graph):

    def __init__(self, _edge_view_factory=_DirectedEdgeView):
        super().__init__(_edge_view_factory)
        self.back_adj = dict()

    def add_edge(self, u_label, v_label):
        """Average case: Theta(1)."""
        for x in {u_label, v_label}:
            if x not in self.adj:
                self.adj[x] = set()
            if x not in self.back_adj:
                self.back_adj[x] = set()

        self.adj[u_label].add(v_label)
        self.back_adj[v_label].add(u_label)
        self._number_of_edges += 1

    def remove_node(self, node):
        if node not in self.nodes:
            return

        # in case there is a self-loop, since we can't modify set while iterating
        if node in self.back_adj[node]:
            self.adj[node].discard(node)
            self.back_adj[node].discard(node)
            self._number_of_edges -= 1

        for parent in self.back_adj[node]:
            self.adj[parent].discard(node)
            self._number_of_edges -= 1

        self._number_of_edges -= len(self.adj[node])
        del self.adj[node]

    def predecessors(self, node):
        return self.back_adj[node]

    def successors(self, node):
        return self.adj[node]

    def neighbors(self, node):
        return self.successors(node)
