"""
Directed Graph Data Structures and Tools

This module contains the necessary pieces to define and construct the basic 
graph data structures needed for the PyConform operations to work.

COPYRIGHT: 2015, University Corporation for Atmospheric Research
LICENSE: See the LICENSE.rst file for details
"""


#===============================================================================
# Graph
#===============================================================================
class Graph(object):
    """
    A rudimentary directed graph data structure
    """
    
    def __init__(self):
        """
        Initializer
        """
        self._vertices = set()
        self._edges = set()

    def vertices(self):
        """
        Return the list of vertices in the graph
        """
        return list(self._vertices)

    def edges(self):
        """
        Return the list of edges (vertex 2-tuples) in the graph
        """
        return list(self._edges)
    
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
        if vertex in self._vertices:
            self._vertices.remove(vertex)
        for edge in tuple(self._edges):
            if vertex in edge:
                self._edges.remove(edge)

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
        self._edges.add((start, stop))

    def disconnect(self, start, stop):
        """
        Remove an edge from the graph

        Parameters:
            start: The starting point of the edge to be removed from the graph
            stop: The ending point of the edge to be removed from the graph
        """
        edge = (start, stop)
        if edge in self._edges:
            self._edges.remove(edge)

    def neighbors_from(self, vertex):
        """
        Return the list of neighbors on edges pointing from the given vertex
        
        Parameters:
            vertex: The vertex object to query
        """
        return [v2 for (v1, v2) in self._edges if v1 == vertex]

    def neighbors_to(self, vertex):
        """
        Return the list of neighbors on edges pointing to the given vertex
        
        Parameters:
            vertex: The vertex object to query
        """
        return [v1 for (v1,v2) in self._edges if v2 == vertex]
