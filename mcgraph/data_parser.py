import json
from typing import Dict, Iterable, List, Optional, Union
from zipfile import ZipFile

from mcgraph.graph_builder import Edge, GraphBuilder, Node


class EdgeColors:
    crafting = "#0000ff"
    smelting = "#cc0000"
    smithing = "#777777"
    item_tag = "#009900"
    block_drop = "#ff00ff"
    entity_drop = "#00ffff"
    chest_loot = "#ffaa00"
    piglin_bartering = "#ff96cc"
    fishing = "#008cff"


class DataParser:
    def __init__(self, jar: ZipFile, graph_builder: GraphBuilder):
        self.jar = jar
        self.graph_builder = graph_builder

    def read_jar(self):
        for filename in self.jar.namelist():
            self.read_file(filename)

    def read_file(self, filename: str):
        if filename.startswith("data/minecraft/recipes/"):
            self.parse_recipe(self.get_file_data(filename))
        elif filename.startswith("data/minecraft/tags/items/"):
            name = filename[len("data/minecraft/tags/items/") : -len(".json")]
            self.parse_item_tag(name, self.get_file_data(filename))
        elif filename.startswith("data/minecraft/loot_tables/"):
            name = filename[len("data/minecraft/loot_tables/") : -len(".json")]
            self.parse_loot_table(name, self.get_file_data(filename))

    def get_file_data(self, filename: str):
        with self.jar.open(filename) as file:
            return json.loads(file.read())

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
            self.graph_builder.add_edge(
                Edge(ingredient, result, color=EdgeColors.crafting)
            )

    def parse_crafting_shapeless_recipe(self, data: Dict):
        result = parse_item_or_tag(data["result"])
        self.graph_builder.add_node(result)

        for ingredient in parse_ingredients(data["ingredients"]):
            self.graph_builder.add_node(ingredient)
            self.graph_builder.add_edge(
                Edge(ingredient, result, color=EdgeColors.crafting)
            )

    def parse_smelting_recipe(self, data: Dict):
        result = get_item_or_block_node(data["result"])
        self.graph_builder.add_node(result)

        for ingredient in parse_ingredient(data["ingredient"]):
            self.graph_builder.add_node(ingredient)
            self.graph_builder.add_edge(
                Edge(ingredient, result, color=EdgeColors.smelting)
            )

    def parse_smithing_recipe(self, data: Dict):
        result = parse_item_or_tag(data["result"])
        self.graph_builder.add_node(result)

        base = parse_item_or_tag(data["base"])
        self.graph_builder.add_node(base)

        addition = parse_item_or_tag(data["addition"])
        self.graph_builder.add_node(addition)

        self.graph_builder.add_edge(Edge(base, result, color=EdgeColors.smithing))
        self.graph_builder.add_edge(Edge(addition, result, color=EdgeColors.smithing))

    def parse_item_tag(self, name: str, data: Dict):
        tag_node = get_item_tag_node(name)
        self.graph_builder.add_node(tag_node)

        for value in data["values"]:
            if value.startswith("#"):
                value_node = get_item_tag_node(value[1:])
            else:
                value_node = get_item_or_block_node(value)

            self.graph_builder.add_node(value_node)

            self.graph_builder.add_edge(
                Edge(value_node, tag_node, color=EdgeColors.item_tag)
            )

    def parse_loot_table(self, name: str, data: Dict):
        if name.startswith("blocks/"):
            self.parse_block_loot_table(name[len("blocks/") :], data)
        elif name.startswith("entities/"):
            self.parse_entity_loot_table(name[len("entities/") :], data)
        elif name.startswith("chests/"):
            self.parse_chest_loot_table(name[len("chests/") :], data)
        elif name == "gameplay/piglin_bartering":
            self.parse_piglin_bartering_loot_table(data)
        elif name == "gameplay/fishing":
            self.parse_fishing_loot_table(data)

    def parse_block_loot_table(self, name: str, data: Dict):
        block_node = get_item_or_block_node(name)

        drop_nodes: List[Node] = []
        self.parse_loot_table_data(data, drop_nodes, not_node=block_node)

        if len(drop_nodes) > 0:
            self.graph_builder.add_node(block_node)

            for drop_node in drop_nodes:
                self.graph_builder.add_node(drop_node)
                self.graph_builder.add_edge(
                    Edge(block_node, drop_node, color=EdgeColors.block_drop)
                )

    def parse_entity_loot_table(self, name: str, data: Dict):
        entity_node = get_entity_node(name)

        drop_nodes: List[Node] = []
        self.parse_loot_table_data(data, drop_nodes)

        if len(drop_nodes) > 0:
            self.graph_builder.add_node(entity_node)

            for drop_node in drop_nodes:
                self.graph_builder.add_node(drop_node)
                self.graph_builder.add_edge(
                    Edge(entity_node, drop_node, color=EdgeColors.entity_drop)
                )

    def parse_chest_loot_table(self, name: str, data: Dict):
        chest_node = get_chest_node(name)

        item_nodes: List[Node] = []
        self.parse_loot_table_data(data, item_nodes)

        if len(item_nodes) > 0:
            self.graph_builder.add_node(chest_node)

            for item_node in item_nodes:
                self.graph_builder.add_node(item_node)
                self.graph_builder.add_edge(
                    Edge(chest_node, item_node, color=EdgeColors.chest_loot)
                )

    def parse_piglin_bartering_loot_table(self, data: Dict):
        gold_ingot_node = get_item_or_block_node("gold_ingot")
        self.graph_builder.add_node(gold_ingot_node)

        bartering_node = Node("piglin_bartering", "piglin_bartering", shape="trapezium")
        self.graph_builder.add_node(bartering_node)
        self.graph_builder.add_edge(
            Edge(gold_ingot_node, bartering_node, color=EdgeColors.piglin_bartering)
        )

        item_nodes: List[Node] = []
        self.parse_loot_table_data(data, item_nodes)

        for item_node in item_nodes:
            self.graph_builder.add_node(item_node)
            self.graph_builder.add_edge(
                Edge(bartering_node, item_node, color=EdgeColors.piglin_bartering)
            )

    def parse_fishing_loot_table(self, data: Dict):
        fishing_rod_node = get_item_or_block_node("fishing_rod")
        self.graph_builder.add_node(fishing_rod_node)

        fishing_node = Node("fishing", "fishing", shape="invhouse")
        self.graph_builder.add_node(fishing_node)
        self.graph_builder.add_edge(
            Edge(fishing_rod_node, fishing_node, color=EdgeColors.fishing)
        )

        item_nodes: List[Node] = []
        self.parse_loot_table_data(data, item_nodes)

        for item_node in item_nodes:
            self.graph_builder.add_node(item_node)
            self.graph_builder.add_edge(
                Edge(fishing_node, item_node, color=EdgeColors.fishing)
            )

    def parse_loot_table_data(
        self, data: Dict, nodes: List[Node], not_node: Optional[Node] = None
    ):
        if "pools" not in data:
            return

        for pool in data["pools"]:
            self.parse_loot_table_entries(pool["entries"], nodes, not_node)

    def parse_loot_table_entries(
        self, entries: List[Dict], nodes: List[Node], not_node: Optional[Node] = None
    ):
        for entry in entries:
            if entry["type"] == "minecraft:item":
                node = get_item_or_block_node(entry["name"])
                if node != not_node and node not in nodes:
                    nodes.append(node)
            elif entry["type"] == "minecraft:tag":
                node = get_item_tag_node(entry["name"])
                if node != not_node and node not in nodes:
                    nodes.append(node)
            elif entry["type"] == "minecraft:alternatives":
                self.parse_loot_table_entries(entry["children"], nodes, not_node)
            elif entry["type"] == "minecraft:loot_table":
                loot_table_data = self.get_file_data(
                    f"data/minecraft/loot_tables/{without_namespace(entry['name'])}.json"
                )
                self.parse_loot_table_data(loot_table_data, nodes, not_node)


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


def get_entity_node(name: str):
    name = without_namespace(name)

    return Node(f"entity/{name}", name, shape="hexagon")


def get_chest_node(name: str):
    name = without_namespace(name)

    return Node(f"chest/{name}", name, shape="box3d")


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
