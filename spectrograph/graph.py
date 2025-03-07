import math
from typing import Optional
from uuid import uuid4

import graphviz
from pathlib import Path

from .format_number import format_number
from .query_plan_item import QueryPlanItem


__all__ = ("query_plan_to_graphviz",)


def query_plan_to_graphviz(
    query_plan: list[QueryPlanItem],
    comments: list[str],
    output_file: Path,
    graph_format: str,
) -> str:
    dot = graphviz.Digraph(comment="Query Plan")
    dot.graph_attr["rankdir"] = "BT"
    dot.attr("node", shape="box")
    dot.attr("node", style="rounded,filled")
    dot.attr("node", margin="0.2,0.2")
    dot.attr("node", fontname="sans-serif")

    def escape(s: str) -> str:
        return graphviz.escape(s).replace("<", "&lt;").replace(">", "&gt;")

    max_cost = max(x.get_max_cost_complete_without_children() for x in query_plan)
    max_rows = max(x.get_max_rows() for x in query_plan)

    def add_nodes(graph: graphviz.Digraph, item: QueryPlanItem):
        rel_cost = item.get_cost_complete_without_children() / max_cost
        color = f"#{int(math.floor(255.0 * 0.7 * rel_cost)):02x}0000"
        fillcolor = f"#ff{int(math.floor(255.0 * (1.0 - 0.3 * rel_cost))):02x}{int(math.floor(255.0 * (1.0 - 0.3 * rel_cost))):02x}"
        penwidth = str(1.0 + 3 * rel_cost)

        def format_dist_style(dist_style: Optional[str]) -> str:
            if dist_style is None:
                return ""
            else:
                if (
                    item.dist_style == "DS_DIST_NONE"
                    or item.dist_style == "DS_DIST_ALL_NONE"
                ):
                    dscolor = "darkgreen"
                else:
                    dscolor = "red"

                return f'<font color="{dscolor}">{escape(dist_style)}</font><br/>'

        def format_cost(item: QueryPlanItem) -> str:
            return f'<font color="{color}">{format_number(item.get_cost_prepare_without_children())} … {format_number(item.get_cost_complete_without_children())}</font><br/>'

        label = "<"
        label += f"<b>{escape(item.operation)}</b><br/>"
        label += format_dist_style(item.dist_style)
        label += format_cost(item)
        label += (
            f"<b>rows:</b> {format_number(item.rows)} <b>width:</b> {item.width}<br/>"
        )
        for param in item.parameters:
            if ": " in param:
                key, value = param.split(": ", 1)
                label += f"<b>{escape(key)}:</b> {escape(value)}<br/>"
            else:
                label += f"{escape(param)}<br/>"
        label += ">"

        graph.node(item.id, label, color=color, fillcolor=fillcolor, penwidth=penwidth)

        b = 0.001
        for child in item.children:
            rel_rows = float(child.rows) / max_rows
            add_nodes(graph, child)
            graph.edge(
                child.id,
                item.id,
                penwidth=str(
                    1.0
                    + 9.0
                    * (math.log(b + rel_rows) - math.log(b))
                    / (math.log(b + 1.0) - math.log(b))
                ),
            )

    with dot.subgraph(name="cluster_comments") as sub:
        sub.node(
            str(uuid4()),
            "Total cost: " + format_number(sum(x.cost_complete for x in query_plan)),
            shape="plaintext",
        )

        for comment in comments:
            sub.node(str(uuid4()), comment, shape="plaintext")

    with dot.subgraph(name="cluster_plan") as sub:
        sub.attr(style="invis")
        for root_item in query_plan:
            add_nodes(sub, root_item)

    dot.render(output_file, format=graph_format)

    return f"{output_file}.{graph_format}"
