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

    with ZipFile(jar_path) as jar:
        data_parser = DataParser(jar, graph_builder)
        data_parser.read_jar()

    graph = graph_builder.build()
    graph.render("output", format="svg")
