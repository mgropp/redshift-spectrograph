from colorama import Fore, Style, Back

from .query_plan_item import QueryPlanItem
from .format_number import format_number

__all__ = ("print_query_plan",)


def __print_items(
    items: list[QueryPlanItem], depth: int, max_cost: float, cost_width: int = 30
):
    for item in items:
        print(
            f"{'  ' * depth}[{depth}] {Back.BLUE}{Fore.BLACK}{item.operation}{Style.RESET_ALL}",
            end="",
        )
        if item.dist_style is not None:
            if (
                item.dist_style == "DS_DIST_NONE"
                or item.dist_style == "DS_DIST_ALL_NONE"
            ):
                color = Fore.GREEN
            else:
                color = Fore.RED

            print(f" {color}{item.dist_style}{Style.RESET_ALL}", end="")

        print()

        rel_cost = item.get_cost_complete_without_children() / max_cost
        cost_bar = int(cost_width * rel_cost)
        print(
            f"{'  ' * (depth + 1)}Cost: [{Fore.RED}{Style.BRIGHT}{'=' * cost_bar}{' ' * (cost_width - cost_bar)}{Style.RESET_ALL}] {format_number(item.get_cost_prepare_without_children())} .. {format_number(item.get_cost_complete_without_children())} ({format_number(item.cost_complete)})"
        )

        for param in item.parameters:
            print(f"{'  ' * (depth + 1)}{param}")
        __print_items(item.children, depth + 1, max_cost, cost_width)


def print_query_plan(items: list[QueryPlanItem]):
    __print_items(
        items, 0, max(x.get_max_cost_complete_without_children() for x in items)
    )

    total_cost = sum(x.cost_complete for x in items)
    print()
    print("Total cost:", format_number(total_cost))
