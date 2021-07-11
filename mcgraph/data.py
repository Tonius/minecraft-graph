from abc import ABC
from dataclasses import dataclass


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


class NameContainer(ABC):
    def __init__(self, name: str):
        if name.startswith("minecraft:"):
            name = name[len("minecraft:") :]

        self.name = name

    def __repr__(self):
        return f"{self.__class__.__name__}({repr(self.name)})"

    def __eq__(self, other):
        return isinstance(other, NameContainer) and other.name == self.name

    def get_node(self) -> Node:
        ...


class Item(NameContainer):
    def get_node(self):
        return Node(f"item/{self.name}", self.name, shape="ellipse")


class ItemTag(NameContainer):
    def get_node(self):
        return Node(f"item_tag/{self.name}", self.name, shape="box")
