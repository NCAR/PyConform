"""
Directed Graph Data Structures and Tools

This module contains the DiGraph directional graph generic data structure.

COPYRIGHT: 2016, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""

from collections import defaultdict
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
        self._vertices = set()
        self._neighbors_to = defaultdict(list)
        self._neighbors_from = defaultdict(list)

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
            if (self._neighbors_to == other._neighbors_to and 
                self._neighbors_from == other._neighbors_from and
                self._vertices == other._vertices):
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
        return vertex in self._vertices
    
    def __len__(self):
        """
        Returns the number of vertices in the graph
        
        Returns:
            int: The number of vertices in the graph
        """
        return len(self._vertices)

    def __str__(self):
        """
        String representation of the graph
        """
        outstr = 'DiGraph:{0}'.format(linesep)
        for v in self.vertices:
            outstr += '   {0!s}'.format(v)
            neighbors = self.neighbors_from(v)
            if len(neighbors) > 0:
                for n in neighbors:
                    outstr += ' --> {0!s}'.format(n)
            outstr += linesep
        return outstr

    def leaves(self):
        """
        Returns the set of vertices in the graph with only incoming edges
        
        Returns:
            set: The set of vertices in the graph with only incoming edges
        """
        return set(self._neighbors_to.keys()) - set(self._neighbors_from.keys())

    def roots(self):
        """
        Returns the set of vertices in the graph with only outgoing edges
        
        Returns:
            set: The set of vertices in the graph with only outgoing edges
        """
        return set(self._neighbors_from.keys()) - set(self._neighbors_to.keys())
                
    def clear(self):
        """
        Remove all vertices and edges from the graph
        """
        self._vertices.clear()
        self._neighbors_to = defaultdict(list)
        self._neighbors_from = defaultdict(list)

    @property
    def vertices(self):
        """
        Return the set of vertices in the graph
        
        Returns:
            set: The set of vertices contained in this graph
        """
        return self._vertices

    @property
    def edges(self):
        """
        Return the list of edges (vertex 2-tuples) in the graph
        
        Returns:
            list: The list of edges contained in this graph
        """
        return [(v,u) for u,vs in self._neighbors_to.iteritems() for v in vs]
    
    def add(self, vertex):
        """
        Add a vertex to the graph

        Parameters:
            vertex: The vertex object to be added to the graph
        """
        self._vertices.add(vertex)

    def remove(self, vertex):
        """
        Remove a vertex from the graph
        
        Parameters:
            vertex: The vertex object to remove from the graph
        """
        self._vertices.discard(vertex)
        self._neighbors_to.pop(vertex, None)
        self._neighbors_from.pop(vertex, None)
                
    def update(self, other):
        """
        Update this graph with the union of itself and another
        
        Parameters:
            other (DiGraph): the other graph to union with
        """
        if not isinstance(other, DiGraph):
            raise TypeError("Cannot form union between DiGraph and non-DiGraph")
        self._vertices.update(other._vertices)
        for v, n in other._neighbors_to.iteritems():
            self._neighbors_to[v].extend(n)
        for v, n in other._neighbors_from.iteritems():
            self._neighbors_from[v].extend(n)

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
        if start not in self._neighbors_from:
            self._neighbors_from[start] = [stop]
        else:
            self._neighbors_from[start].append(stop)
        if stop not in self._neighbors_to:
            self._neighbors_to[stop] = [start]
        else:
            self._neighbors_to[stop].append(start)

    def disconnect(self, start, stop):
        """
        Remove an edge from the graph

        Parameters:
            start: The starting point of the edge to be removed from the graph
            stop: The ending point of the edge to be removed from the graph
        """
        if start in self._neighbors_from:
            if stop in self._neighbors_from[start]:
                self._neighbors_from[start].remove(stop)
                if self._neighbors_from[start] == []:
                    self._neighbors_from.pop(start)
        if stop in self._neighbors_to:
            if start in self._neighbors_to[stop]:
                self._neighbors_to[stop].remove(start)
                if self._neighbors_to[stop] == []:
                    self._neighbors_to.pop(stop)

    def neighbors_from(self, vertex):
        """
        Return the list of neighbors on edges pointing from the given vertex
        
        Parameters:
            vertex: The vertex object to query
        
        Returns:
            list: The list of vertices with incoming edges from vertex
        """
        return list(self._neighbors_from[vertex])

    def neighbors_to(self, vertex):
        """
        Return the list of neighbors on edges pointing to the given vertex
        
        Parameters:
            vertex: The vertex object to query
        
        Returns:
            list: The list of vertices with outgoing edges to vertex
        """
        return list(self._neighbors_to[vertex])

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
            neighbors = self.neighbors_to
        else:
            neighbors = self.neighbors_from
        while queue:
            vertex = queue.pop(0)
            if vertex not in visited:
                yield vertex
                visited.add(vertex)
                queue.extend(v for v in neighbors(vertex) if v not in visited)

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
            neighbors = self.neighbors_to
        else:
            neighbors = self.neighbors_from
        while stack:
            vertex = stack.pop()
            if vertex not in visited:
                yield vertex
                visited.add(vertex)
                stack.extend(v for v in neighbors(vertex) if v not in visited)

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
        stack = list(G.vertices - set(sum(G._neighbors_from.itervalues(), [])))
        while stack:
            vertex = stack.pop()
            sorted_list.append(vertex)
            for neighbor in G.neighbors_from(vertex):
                G.disconnect(vertex, neighbor)
                if len(G.neighbors_to(neighbor)) == 0:
                    stack.append(neighbor)
        if len(sum(G._neighbors_from.itervalues(), [])) > 0:
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
                neighbors = [v for v in self.neighbors_from(vertex) 
                             if v not in comp.vertices]
                for neighbor in neighbors:
                    comp.connect(vertex, neighbor)
                stack.extend(neighbors)
                # Backward
                neighbors = [v for v in self.neighbors_to(vertex) 
                             if v not in comp.vertices]
                for neighbor in neighbors:
                    comp.connect(neighbor, vertex)
                stack.extend(neighbors)
                # Mark vertex as visited
                if vertex in unvisited:
                    unvisited.remove(vertex)
            if len(comp.vertices) > 0:
                components.add(comp)
        return components
