from edge import Edge
from node import Node

class Network:

    def __init__(self):
        self.nodes = {}
        self.edges = []

    def add_node(self, id, weight = 0.0):
        if id in self.nodes.keys():
            pass
        else:
            node = Node(id, weight)
            self.nodes[id] = node

    def add_edge(self, source_id, target_id, directed=False):
        source_node = self.nodes[source_id]
        target_node = self.nodes[target_id]
        edge = Edge(source_node, target_node, directed)
        self.edges.append(edge)

    def get_node_list(self):
        return list(self.nodes.values())
    
    def get_node(self, id):
        return self.nodes[id]

    def get_edge_list(self):
        return self.edges
    
    def get_edge(self, source, target):
        for edge in self.edges:
            if edge.get_source() == source and edge.get_target() == target:
                return edge
    
    def remove_edge(self, source, target):
        edge = self.get_edge(source, target)
        self.edges.remove(edge)
        
    def remove_node(self, node):
        del self.nodes[node]
        for edge in self.edges:
            if edge.get_source() == node or edge.get_target() == node:
                self.edges.remove(edge)

    def __str__(self):
        num_nodes = len(self.nodes)
        num_edges = len(self.edges)
        return f"Network with {num_nodes} nodes and {num_edges} edges"

