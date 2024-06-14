from pydantic import BaseModel
from typing import Dict, Any, List, Literal, Optional
from crimson.formatter.templator_patch import format_indent_patch, format_insert_patch
from crimson.templator import (
    format_insert_loop,
)
import pandas as pd


class Kwargs(BaseModel):
    name: str
    kwargs: Dict[str, Any]
    with_brackets: bool
    _used_keys: List[str] = []


"""
class DataFrame(BaseModel):
    name: str
    data_frame: pd.DataFrame
    _used_keys: List[str] = []
"""


class Template(BaseModel):
    name: str
    body: str
    formatted: str

class Parser(BaseModel):
    parser_type: Literal["insert", "indent", "insert_loop"]
    open: str
    close: str


class Formatter:
    def __init__(self):
        self.kwargs_list: List[Kwargs] = []
        self.template_list: List[Template] = []
        self.parser_list: List[Parser] = []
        self.open_close_pairs = []

    def register_kwargs(self, name, kwargs: Dict[str, Any], with_brackets: bool):
        self.kwargs_list.append(
            Kwargs(name=name, kwargs=kwargs, with_brackets=with_brackets)
        )

    def register_template(self, name, template):

        self.template_list.append(
            Template(
                name=name,
                body=template,
                formatted=template,
            )
        )

    def register_parser(self, parser_props: Parser):
        self.parser_list.append(parser_props)

    def parser_one_round(self):
        for template in self.template_list:
            self.parser_single_template(template)

    def parser_single_template(self, template: Template):
        for parser in self.parser_list:
            parser_fn = parser_map[parser.parser_type]
            for kwargs in self.kwargs_list:
                formatted = parser_fn(
                    template.formatted,
                    kwargs.kwargs,
                    open=parser.open,
                    close=parser.close,
                )

                template.formatted = formatted
            
            template_kwargs = self.get_templates_as_kwargs()
            formatted = parser_fn(
                template.formatted,
                template_kwargs,
                open=parser.open,
                close=parser.close,
            )
            template.formatted = formatted

    def get_templates_as_kwargs(self):
        kwargs = {}
        for template in self.template_list:
            kwargs[template.name] = template.formatted
        return kwargs

parser_map = {"insert": format_insert_patch, "indent": format_indent_patch}
