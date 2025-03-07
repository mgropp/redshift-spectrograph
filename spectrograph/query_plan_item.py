import re
from dataclasses import dataclass
from typing import Optional
from uuid import uuid4

__all__ = ("QueryPlanItem",)

re_op = re.compile(
    r"(?P<dist_style>DS_[A-Z_]+)?\s*\(cost=(?P<cost_prep>[0-9]+(?:\.[0-9]+)?)\.\.(?P<cost_comp>[0-9]+(?:\.[0-9]+)?) rows=(?P<rows>[0-9]+) width=(?P<width>[0-9]+)\)\s*$"
)


@dataclass
class QueryPlanItem:
    id: str
    operation: str
    dist_style: Optional[str]
    parameters: list[str]
    cost_prepare: float
    cost_complete: float
    rows: int
    width: int
    children: list["QueryPlanItem"]

    def get_cost_prepare_without_children(self) -> float:
        return max(0.0, self.cost_prepare - sum(x.cost_prepare for x in self.children))

    def get_cost_complete_without_children(self) -> float:
        return max(
            0.0, self.cost_complete - sum(x.cost_complete for x in self.children)
        )

    def get_max_cost_complete_without_children(self) -> float:
        if len(self.children) > 0:
            return max(
                self.get_cost_complete_without_children(),
                max(x.get_max_cost_complete_without_children() for x in self.children),
            )
        else:
            return self.get_cost_complete_without_children()

    def get_max_rows(self):
        if len(self.children) > 0:
            return max(self.rows, max(x.get_max_rows() for x in self.children))
        else:
            return self.rows

    @staticmethod
    def from_line(line: str) -> "QueryPlanItem":
        m = re_op.search(line)
        if m is None:
            dist_style = None
            cost_prepare = float("NaN")
            cost_complete = float("NaN")
            rows = -1
            width = -1
        else:
            dist_style = m.group("dist_style")
            cost_prepare = float(m.group("cost_prep"))
            cost_complete = float(m.group("cost_comp"))
            rows = int(m.group("rows"))
            width = int(m.group("width"))

            line = line[: m.start()].strip()

        line_strip = line.strip()
        if line_strip.startswith("->  "):
            line_strip = line_strip[4:]
        if line_strip.startswith("XN "):
            line_strip = line_strip[3:]

        return QueryPlanItem(
            str(uuid4()),
            line_strip,
            dist_style,
            [],
            cost_prepare,
            cost_complete,
            rows,
            width,
            [],
        )
