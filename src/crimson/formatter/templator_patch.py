from pydantic import BaseModel
from typing import Dict, Any, List, Literal, Optional
from crimson.templator import (
    format_indent,
    format_insert,
    format_insert_loop,
)


def format_indent_patch(
    text: str,
    kwargs:Dict[str, str],
    open: str = r"\{",
    close: str = r"\}",
    safe: bool = True,
):
    return format_indent(text, open, close, safe, **kwargs)

def format_insert_patch(
    text: str,
    kwargs:Dict[str, str],
    open: str = r"\[",
    close: str = r"\]",
    safe: bool = True,
):
    return format_insert(text, open, close, safe, **kwargs)
