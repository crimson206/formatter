from pydantic import BaseModel
from typing import Dict, Any, List, Literal, Optional
from crimson.formatter.templator_patch import (
    format_indent_patch,
    format_insert_patch
)
from crimson.templator import (
    format_insert_loop,
)


class Kwargs(BaseModel):
    name: str
    kwargs: Dict[str, Any]

class Template(BaseModel):
    name: str
    body: str
    parser_type: Literal["insert", "indent", "insert_loop"]
    parser_inputs: Dict[str, Any]
    _formatted: Optional[str]
    _all_keys: List[str] = []
    _used_keys: List[str] = []
    _used_keys: List[str] = []

class OpenClosePair(BaseModel):
    open: str
    close: str

class Formatter():
    def __init__(self):
        self.kwargs: List[Kwargs] = []
        self.templates: List[Template] = []
        self.open_close_pairs = []
    
    def register_kwargs(self, name, kwargs:Dict[str, Any]):
        self.kwargs.append(Kwargs(
            name=name,
            kwargs=kwargs
        ))

    def register_template(self, name, template, parser_type, parser_inputs):
        self.templates.append(Template(
            name=name,
            body=template,
            parser_type=parser_type,
            parser_inputs=parser_inputs
        ))
    
    def parser_one_round():
        pass

def _get_open_and_close(parser_inputs):
    return OpenClosePair(**parser_inputs)
