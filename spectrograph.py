#!/usr/bin/env python3
import argparse
from pathlib import Path

from spectrograph import print_query_plan
from spectrograph import query_plan_to_graphviz
from spectrograph import read_query_plan


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("query_plan_file", type=Path)
    parser.add_argument("--graph", type=Path)
    args = parser.parse_args()

    with open(args.query_plan_file) as f:
        items, comments = read_query_plan(f)

    print_query_plan(items)

    print()
    for comment in comments:
        print(comment)

    if args.graph:
        import tempfile
        import os

        graph_format = args.graph.suffix[1:]
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_file = Path(temp_dir) / args.graph.name
            output_file = query_plan_to_graphviz(
                items, comments, temp_file, graph_format
            )
            os.rename(output_file, args.graph)
            print("Graph written to", args.graph)


if __name__ == "__main__":
    main()
