import json
from typing import TextIO, Tuple
from .query_plan_item import QueryPlanItem

__all__ = ("read_query_plan",)


def get_depth(line: str) -> int:
    line_strip = line.lstrip()
    depth = (len(line) - len(line_strip)) // 6
    if line_strip.startswith("->  "):
        depth += 1

    return depth


def read_query_plan(f: TextIO) -> Tuple[list[QueryPlanItem], list[str]]:
    def error(x):
        raise Exception("Unexpected query plan item: " + str(x))

    lines = [x["QUERY PLAN"] for x in json.load(f) if x["QUERY PLAN"] is not None]

    top_level_items = []
    stack = []
    comments = []

    for line in lines:
        if line.startswith("--"):
            comments.append(line)
            continue

        depth = get_depth(line)
        new_op = len(stack) == 0 or line.lstrip().startswith("->  ")
        if new_op:
            stack = stack[:depth]
            op = QueryPlanItem.from_line(line)

            if len(stack) == 0:
                top_level_items.append(op)
            else:
                stack[-1].children.append(op)

            stack.append(op)

        else:
            if len(stack) == 0:
                raise Exception("Unexpected depth 0")

            stack[-1].parameters.append(line.strip())

    return top_level_items, comments
