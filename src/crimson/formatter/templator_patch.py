from typing import Dict
from crimson.templator import (
    format_indent,
    format_insert,
)


def format_indent_patch(
    text: str,
    kwargs: Dict[str, str],
    open: str = r"\{",
    close: str = r"\}",
    safe: bool = True,
) -> str:
    return format_indent(text, open, close, safe, **kwargs)


def format_insert_patch(
    text: str,
    kwargs: Dict[str, str],
    open: str = r"\[",
    close: str = r"\]",
    safe: bool = True,
) -> str:
    return format_insert(text, open, close, safe, **kwargs)
