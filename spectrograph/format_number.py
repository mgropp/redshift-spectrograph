__all__ = ("format_number",)


def format_number(x: float | int) -> str:
    if x > 1000000000000000:
        return f"{(x / 1000000000000000.0):.1f}P"
    elif x > 1000000000000:
        return f"{(x / 1000000000000.0):.1f}T"
    elif x > 1000000000:
        return f"{(x / 1000000000.0):.1f}G"
    elif x > 1000000:
        return f"{(x / 1000000.0):.1f}M"
    elif x > 1000:
        return f"{(x / 1000.0):.2f}k"
    else:
        return str(x)
