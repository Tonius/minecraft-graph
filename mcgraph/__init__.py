import json
from zipfile import ZipFile

from mcgraph.data_parser import DataParser
from mcgraph.graph_builder import GraphBuilder

# TODO:
# - entity drops
# - biomes
# - dimensions / portals
# - structures / loot chests
# - entity spawning
# - hardcoded recipes (interactions)


def mcgraph(jar_path: str):
    graph_builder = GraphBuilder()
    data_parser = DataParser(graph_builder)

    with ZipFile(jar_path) as jar:
        for filename in jar.namelist():

            def get_data():
                with jar.open(filename) as file:
                    return json.loads(file.read())

            data_parser.parse_file(filename, get_data)

    graph = graph_builder.build()
    graph.render("output", format="svg")
