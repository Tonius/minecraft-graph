from dataclasses import dataclass
from typing import List

from graphviz import Digraph


@dataclass
class Node:
    name: str
    label: str
    shape: str = "ellipse"


@dataclass
class Edge:
    from_node: Node
    to_node: Node
    color: str = "black"


class GraphBuilder:
    def __init__(self):
        self.nodes: List[Node] = []
        self.edges: List[Edge] = []

    def add_node(self, node: Node):
        if node not in self.nodes:
            self.nodes.append(node)

    def add_edge(self, edge: Edge):
        if edge not in self.edges:
            self.edges.append(edge)

    def build(self):
        graph = Digraph()
        graph.attr(rankdir="LR", overlap="false", splines="false")

        for node in self.nodes:
            graph.node(node.name, label=node.label, shape=node.shape)

        for edge in self.edges:
            graph.edge(edge.from_node.name, edge.to_node.name, color=edge.color)

        return graph
