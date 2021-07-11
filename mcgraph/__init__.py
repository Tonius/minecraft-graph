import json
from typing import List
from zipfile import ZipFile

from graphviz import Digraph

from mcgraph.recipe import Recipe

# TODO:
# - remaining recipe types
# - entity drops
# - biomes
# - dimensions / portals
# - structures / loot chests
# - entity spawning
# - hardcoded recipes (interactions)


def mcgraph(jar_path: str):
    graph = Digraph()
    graph.attr(rankdir="LR", overlap="false", splines="false")

    nodes = []
    edges = []

    for recipe in load_recipes(jar_path):
        for node in recipe.get_nodes():
            if node not in nodes:
                graph.node(node.name, label=node.label, shape=node.shape)
                nodes.append(node)

        for edge in recipe.get_edges():
            if edge not in edges:
                graph.edge(edge.from_node.name, edge.to_node.name, color=edge.color)
                edges.append(edge)

    graph.render("output", format="svg")


def load_recipes(jar_path: str) -> List[Recipe]:
    recipes = []

    with ZipFile(jar_path) as jar:
        for filename in jar.namelist():

            def get_data():
                with jar.open(filename) as file:
                    return json.loads(file.read())

            recipes += Recipe.parse_file(filename, get_data)

    return recipes
