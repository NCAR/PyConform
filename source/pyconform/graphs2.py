"""
Directed Graph Data Structures and Tools

This module contains the DiGraph directional graph generic data structure.

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from copy import deepcopy
from os import linesep


#===============================================================================
# DiGraph - A directed Graph data structure
#===============================================================================
class DiGraph(object):
    """
    A rudimentary directed graph data structure
    """
    
    def __init__(self):
        """
        Initializer
        """
        self._forward_map = {}
        self._reverse_map = {}

    def __str__(self):
        """
        String representation of the graph
        """
        outstrs = ['DiGraph:']
        for vertex, neighbors in self._forward_map.iteritems():
            if len(neighbors) == 0:
                outstrs.append('   {0!s}'.format(vertex))
            else:
                for neighbor in neighbors:
                    outstrs.append('   {0!s} --> {1!s}'.format(vertex, neighbor))
        return linesep.join(outstrs)

    def __eq__(self, other):
        """
        Check if an other graph is equal to this graph
        
        Equality for the DiGraph is defined as when all of the vertex
        objects and edges in the other graph are in this graph.
        
        Parameters:
            other (DiGraph): the graph to compare against
            
        Returns:
            bool: True if equal, False if not equal
        """
        if isinstance(other, DiGraph):
            if (self._forward_map == other._forward_map and
                self._reverse_map == other._reverse_map):
                return True
        return False
    
    def __ne__(self, other):
        """
        Check if an other graph is not equal to this graph
        
        Inquality for the DiGraph is defined as when the other graph is
        found to NOT equal this graph.
        
        Parameters:
            other (DiGraph): the graph to compare against        
            
        Returns:
            bool: True if not equal, False if equal
        """
        return not (self == other)

    def __contains__(self, vertex):
        """
        Check if a vertex is in the graph
            
        Returns:
            bool: True if vertex in graph, False otherwise
        """
        return vertex in self._forward_map or vertex in self._reverse_map
    
    def __len__(self):
        """
        Returns the number of vertices in the graph
        
        Returns:
            int: The number of vertices in the graph
        """
        return self.nvertices

    @property
    def nvertices(self):
        """
        Returns the number of edges in the graph
        
        Returns:
            int: The numebr of edges in the graph
        """
        return len(self.vertices)
    
    @property
    def nedges(self):
        """
        Returns the number of edges in the graph
        
        Returns:
            int: The numebr of edges in the graph
        """
        return len(self.edges)

    def sinks(self):
        """
        Returns the set of vertices in the graph with only incoming edges
        
        Returns:
            set: The set of vertices in the graph with only incoming edges
        """
        zero_outgoing = set(v for v,n in self._forward_map.iteritems()
                            if len(n) == 0)
        plus_incoming = set(v for v,n in self._reverse_map.iteritems()
                            if len(n) > 0)
        return plus_incoming.intersection(zero_outgoing)

    def sources(self):
        """
        Returns the set of vertices in the graph with only outgoing edges
        
        Returns:
            set: The set of vertices in the graph with only outgoing edges
        """
        zero_incoming = set(v for v,n in self._reverse_map.iteritems()
                            if len(n) == 0)
        plus_outgoing = set(v for v,n in self._forward_map.iteritems()
                            if len(n) > 0)
        return plus_outgoing.intersection(zero_incoming)
                
    def clear(self):
        """
        Remove all vertices and edges from the graph
        """
        self._reverse_map = {}
        self._forward_map = {}

    @property
    def vertices(self):
        """
        Return the list of vertices in the graph
        
        Returns:
            set: The list of vertices contained in this graph
        """
        return self._forward_map.keys()

    @property
    def edges(self):
        """
        Return the list of edges (vertex 2-tuples) in the graph
        
        Returns:
            list: The list of edges contained in this graph
        """
        return [(u,v) for u,vs in self._forward_map.iteritems() for v in vs]
    
    def add(self, vertex):
        """
        Add a vertex to the graph

        Parameters:
            vertex: The vertex object to be added to the graph
        """
        if vertex not in self._forward_map:
            self._forward_map[vertex] = []
            self._reverse_map[vertex] = []

    def remove(self, vertex):
        """
        Remove a vertex from the graph
        
        Parameters:
            vertex: The vertex object to remove from the graph
        """
        if vertex in self._forward_map:
            self._forward_map.pop(vertex)
            self._reverse_map.pop(vertex)
                
    def update(self, other):
        """
        Update this graph with the union of itself and another
        
        Parameters:
            other (DiGraph): the other graph to union with
        """
        if not isinstance(other, DiGraph):
            raise TypeError("Cannot form union between DiGraph and non-DiGraph")
        for vertex, neighbors in other._forward_map.iteritems():
            self.add(vertex)
            self._forward_map[vertex].extend([n for n in neighbors if n not in
                                              self._forward_map[vertex]])
        for vertex, neighbors in other._reverse_map.iteritems():
            self._reverse_map[vertex].extend([n for n in neighbors if n not in
                                              self._forward_map[vertex]])

    def union(self, other):
        """
        Form the union of this graph with another
        
        Parameters:
            other (DiGraph): the other graph to union with
        
        Returns:
            DiGraph: A graph containing the union of this graph with another
        """
        if not isinstance(other, DiGraph):
            raise TypeError("Cannot for union between DiGraph and non-DiGraph")
        G = deepcopy(self)
        G.update(other)
        return G

    def connect(self, start, stop):
        """
        Add an edge to the graph
        
        If the vertices specified are not in the graph, they will be added.

        Parameters:
            start: The starting point of the edge to be added to the graph
            stop: The ending point of the edge to be added to the graph
        """
        self.add(start)
        self.add(stop)
        if stop not in self._forward_map[start]:
            self._forward_map[start].append(stop)
            self._reverse_map[stop].append(start)

    def disconnect(self, start, stop):
        """
        Remove an edge from the graph

        Parameters:
            start: The starting point of the edge to be removed from the graph
            stop: The ending point of the edge to be removed from the graph
        """
        if start not in self._forward_map:
            return
        if stop in self._forward_map[start]:
            self._forward_map[start].remove(stop)
            self._reverse_map[stop].remove(start)

    def neighbors_from(self, vertex):
        """
        Return the list of neighbors on edges pointing from the given vertex
        
        Parameters:
            vertex: The vertex object to query
        
        Returns:
            list: The list of vertices with incoming edges from vertex
        """
        return list(self._forward_map[vertex])

    def neighbors_to(self, vertex):
        """
        Return the list of neighbors on edges pointing to the given vertex
        
        Parameters:
            vertex: The vertex object to query
        
        Returns:
            list: The list of vertices with outgoing edges to vertex
        """
        return list(self._reverse_map[vertex])

    def iter_bfs(self, start, reverse=False):
        """
        Breadth-First Search generator from the root node
        
        Parameters:
            start: The starting vertex of the search
            reverse (bool): Whether to perform the search "backwards"
                through the graph (True) or "forwards" (False)
                
        Yields:
            The next vertex found in the breadth-first search from start
        """
        if start not in self.vertices:
            raise KeyError('Root vertex not in graph')
        
        visited = set()
        queue = [start]
        if reverse:
            neighbors = self._reverse_map
        else:
            neighbors = self._forward_map
        while queue:
            vertex = queue.pop(0)
            if vertex not in visited:
                yield vertex
                visited.add(vertex)
                queue.extend(v for v in neighbors[vertex] if v not in visited)

    def iter_dfs(self, start, reverse=False):
        """
        Depth-First Search generator from the root node
        
        Parameters:
            start: The starting vertex of the search
            reverse (bool): Whether to perform the search "backwards"
                through the graph (True) or "forwards" (False)
        """
        if start not in self.vertices:
            raise KeyError('Root vertex not in graph')
        
        visited = set()
        stack = [start]
        if reverse:
            neighbors = self._reverse_map
        else:
            neighbors = self._forward_map
        while stack:
            vertex = stack.pop()
            if vertex not in visited:
                yield vertex
                visited.add(vertex)
                stack.extend(v for v in neighbors[vertex] if v not in visited)

    def toposort(self):
        """
        Return a topological ordering of the vertices using Kahn's algorithm
        
        Returns:
            list: If topological ordering is possible, then return the list of
                topologically ordered vertices
            None: If topological ordering is not possible (i.e., if the DiGraph
                is cyclic), then return None
        """
        G = deepcopy(self)
        sorted_list = []
        stack = [v for v,n in G._reverse_map.iteritems() if len(n) == 0]
        while stack:
            vertex = stack.pop()
            sorted_list.append(vertex)
            for neighbor in list(G._forward_map[vertex]):
                G.disconnect(vertex, neighbor)
                if len(G._reverse_map[neighbor]) == 0:
                    stack.append(neighbor)
        if sum(len(n) for n in G._forward_map.itervalues()) > 0:
            return None
        else:
            return sorted_list
        
    def is_cyclic(self):
        """
        Returns whether the graph is cyclic or not
        """
        return self.toposort() is None

    def components(self):
        """
        Return the connected components of the graph
        
        Returns:
            list: A list of connected DiGraphs
        """
        unvisited = set(self.vertices)
        components = set()
        while unvisited:
            start = unvisited.pop()
            comp = type(self)()
            stack = [start]
            while stack:
                vertex = stack.pop()
                # Forward
                neighbors = [v for v in self._forward_map[vertex] 
                             if v not in comp]
                for neighbor in neighbors:
                    comp.connect(vertex, neighbor)
                stack.extend(neighbors)
                # Backward
                neighbors = [v for v in self._reverse_map[vertex] 
                             if v not in comp]
                for neighbor in neighbors:
                    comp.connect(neighbor, vertex)
                stack.extend(neighbors)
                # Mark vertex as visited
                if vertex in unvisited:
                    unvisited.remove(vertex)
            if len(comp.vertices) > 0:
                components.add(comp)
        return components
