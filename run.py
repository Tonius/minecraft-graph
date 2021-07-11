from argparse import ArgumentParser
from mcgraph import mcgraph


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("jar_path", help="path to Minecraft jar file")

    args = parser.parse_args()

    mcgraph(args.jar_path)
