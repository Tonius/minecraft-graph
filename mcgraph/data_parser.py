from typing import Callable, Dict, Iterable, List, Union

from mcgraph.graph_builder import Edge, GraphBuilder, Node


class DataParser:
    def __init__(self, graph_builder: GraphBuilder):
        self.graph_builder = graph_builder

    def parse_file(self, filename: str, get_data: Callable[[], Dict]):
        if filename.startswith("data/minecraft/recipes/"):
            self.parse_recipe(get_data())
        elif filename.startswith("data/minecraft/tags/items/"):
            name = filename[len("data/minecraft/tags/items/") : -len(".json")]
            self.parse_item_tag(name, get_data())

    def parse_recipe(self, data: Dict):
        if data["type"] == "minecraft:crafting_shaped":
            self.parse_crafting_shaped_recipe(data)
        elif data["type"] == "minecraft:crafting_shapeless":
            self.parse_crafting_shapeless_recipe(data)
        elif data["type"] == "minecraft:smelting":
            self.parse_smelting_recipe(data)
        elif data["type"] == "minecraft:smithing":
            self.parse_smithing_recipe(data)

    def parse_crafting_shaped_recipe(self, data: Dict):
        result = parse_item_or_tag(data["result"])
        self.graph_builder.add_node(result)

        for ingredient in parse_ingredients(data["key"].values()):
            self.graph_builder.add_node(ingredient)
            self.graph_builder.add_edge(Edge(ingredient, result, color="#0000ff"))

    def parse_crafting_shapeless_recipe(self, data: Dict):
        result = parse_item_or_tag(data["result"])
        self.graph_builder.add_node(result)

        for ingredient in parse_ingredients(data["ingredients"]):
            self.graph_builder.add_node(ingredient)
            self.graph_builder.add_edge(Edge(ingredient, result, color="#0000ff"))

    def parse_smelting_recipe(self, data: Dict):
        result = get_item_or_block_node(data["result"])
        self.graph_builder.add_node(result)

        for ingredient in parse_ingredient(data["ingredient"]):
            self.graph_builder.add_node(ingredient)
            self.graph_builder.add_edge(Edge(ingredient, result, color="#cc0000"))

    def parse_smithing_recipe(self, data: Dict):
        result = parse_item_or_tag(data["result"])
        self.graph_builder.add_node(result)

        base = parse_item_or_tag(data["base"])
        self.graph_builder.add_node(base)

        addition = parse_item_or_tag(data["addition"])
        self.graph_builder.add_node(addition)

        self.graph_builder.add_edge(Edge(base, result, color="#777777"))
        self.graph_builder.add_edge(Edge(addition, result, color="#777777"))

    def parse_item_tag(self, name: str, data: Dict):
        tag_node = get_item_tag_node(name)
        self.graph_builder.add_node(tag_node)

        for value in data["values"]:
            if value.startswith("#"):
                value_node = get_item_tag_node(value[1:])
            else:
                value_node = get_item_or_block_node(value)

            self.graph_builder.add_node(value_node)

            self.graph_builder.add_edge(Edge(value_node, tag_node, color="#009900"))


def without_namespace(name: str):
    if name.startswith("minecraft:"):
        return name[len("minecraft:") :]

    return name


def get_item_or_block_node(name: str):
    name = without_namespace(name)

    return Node(f"item_or_block/{name}", name, shape="ellipse")


def get_item_tag_node(name: str):
    name = without_namespace(name)

    return Node(f"item_tag/{name}", name, shape="box")


def parse_item_or_tag(data: Dict):
    if "item" in data:
        return get_item_or_block_node(data["item"])
    elif "tag" in data:
        return get_item_tag_node(data["tag"])

    raise Exception(f"{repr(data)} has no 'item' or 'tag'")


def parse_ingredient(data: Union[Dict, List[Dict]]):
    if type(data) is not list:
        data = [data]

    return [parse_item_or_tag(i) for i in data]


def parse_ingredients(data: Iterable[Union[Dict, List[Dict]]]):
    ingredients: List[Node] = []

    for item in data:
        ingredients += parse_ingredient(item)

    return ingredients