from abc import ABC
from typing import Callable, Dict, List, Union

from mcgraph.data import Edge, Item, ItemTag, Node


class Recipe(ABC):
    def get_nodes(self) -> List[Node]:
        ...

    def get_edges(self) -> List[Edge]:
        ...

    @classmethod
    def parse_file(cls, filename: str, get_data: Callable[[], Dict]) -> List["Recipe"]:
        if filename.startswith("data/minecraft/recipes/"):
            data = get_data()

            if data["type"] == "minecraft:crafting_shaped":
                return [CraftingShaped(data)]
            elif data["type"] == "minecraft:crafting_shapeless":
                return [CraftingShapeless(data)]
            elif data["type"] == "minecraft:smelting":
                return [Smelting(data)]
            elif data["type"] == "minecraft:smithing":
                return [Smithing(data)]
        elif filename.startswith("data/minecraft/tags/items/"):
            name = filename[len("data/minecraft/tags/items/") : -len(".json")]

            return [ItemTagValues(name, get_data())]

        return []


class CraftingShaped(Recipe):
    result: Item
    ingredients: List[Union[Item, ItemTag]]

    def __init__(self, data: Dict):
        self.result = parse_item_or_tag(data["result"])

        self.ingredients = []
        for item in data["key"].values():
            for ingredient in parse_ingredient(item):
                if ingredient not in self.ingredients:
                    self.ingredients.append(ingredient)

    def get_nodes(self):
        return [self.result.get_node(), *[i.get_node() for i in self.ingredients]]

    def get_edges(self):
        return [
            Edge(ingredient.get_node(), self.result.get_node(), color="blue")
            for ingredient in self.ingredients
        ]


class CraftingShapeless(Recipe):
    result: Item
    ingredients: List[Union[Item, ItemTag]]

    def __init__(self, data: Dict):
        self.result = parse_item_or_tag(data["result"])

        self.ingredients = []
        for item in data["ingredients"]:
            for ingredient in parse_ingredient(item):
                if ingredient not in self.ingredients:
                    self.ingredients.append(ingredient)

    def get_nodes(self):
        return [self.result.get_node(), *[i.get_node() for i in self.ingredients]]

    def get_edges(self):
        return [
            Edge(ingredient.get_node(), self.result.get_node(), color="blue")
            for ingredient in self.ingredients
        ]


class Smelting(Recipe):
    result: Item
    ingredients: List[Union[Item, ItemTag]]

    def __init__(self, data: Dict):
        self.result = Item(data["result"])
        self.ingredients = parse_ingredient(data["ingredient"])

    def get_nodes(self):
        return [self.result.get_node(), *[i.get_node() for i in self.ingredients]]

    def get_edges(self):
        return [
            Edge(ingredient.get_node(), self.result.get_node(), color="red")
            for ingredient in self.ingredients
        ]


class Smithing(Recipe):
    result: Item
    base: Union[Item, ItemTag]
    addition: Union[Item, ItemTag]

    def __init__(self, data: Dict):
        self.result = parse_item_or_tag(data["result"])
        self.base = parse_item_or_tag(data["base"])
        self.addition = parse_item_or_tag(data["addition"])

    def get_nodes(self):
        return [self.result.get_node(), self.base.get_node(), self.addition.get_node()]

    def get_edges(self):
        return [
            Edge(self.base.get_node(), self.result.get_node(), color="darkgray"),
            Edge(self.addition.get_node(), self.result.get_node(), color="darkgray"),
        ]


class ItemTagValues(Recipe):
    name: str
    items: List[Item]

    def __init__(self, name: str, data: Dict):
        self.name = name

        self.items = []
        for value in data["values"]:
            if value.startswith("#"):
                self.items.append(ItemTag(value[1:]))
            else:
                self.items.append(Item(value))

    def get_nodes(self):
        return [ItemTag(self.name).get_node(), *[i.get_node() for i in self.items]]

    def get_edges(self):
        return [
            Edge(item.get_node(), ItemTag(self.name).get_node(), color="green")
            for item in self.items
        ]


def parse_ingredient(data: Union[Dict, List[Dict]]):
    # TODO: if data is a list, make a recipe for each item
    if type(data) is not list:
        data = [data]

    return [parse_item_or_tag(i) for i in data]


def parse_item_or_tag(item: Dict):
    if "item" in item:
        return Item(item["item"])
    elif "tag" in item:
        return ItemTag(item["tag"])

    raise Exception(f"Item {repr(item)} has no 'item' or 'tag'")
