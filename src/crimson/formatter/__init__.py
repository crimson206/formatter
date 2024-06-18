from pydantic import BaseModel
from typing import Dict, Any, List, Literal, Optional, Callable, Union
from crimson.templator import remove_lines, format_insert_loop
from crimson.formatter.templator_patch import (
    format_indent_patch,
    format_insert_patch,
)


class TemplateHolder(BaseModel):
    name: str
    template: str
    formatted: str
    parser_type_as_kwarg: Optional[Literal["insert", "indent", "insert_loop"]]


class KwargsHolder(BaseModel):
    name: str
    kwargs: Dict[str, Any]
    kwargs_with_brackets: Dict[str, Any] = {}
    parser_type: Literal["insert", "indent", "insert_loop"]
    used_keys: List[str] = []


class Formatter:
    def __init__(self):
        self.kwargs_holders: Dict[str, KwargsHolder] = {}
        self.template_holders: Dict[str, TemplateHolder] = {}
        self.open_close_pairs = []

    def register_kwargs(
        self,
        name,
        kwargs: Dict[str, Any],
        parser_type: Literal["insert", "indent", "insert_loop"],
    ):
        kwargs_holder = KwargsHolder(name=name, kwargs=kwargs, parser_type=parser_type)
        self.kwargs_holders[name] = kwargs_holder
        _add_kwargs_with_brackets_init(kwargs_holder)

    def register_template(
        self,
        name: str,
        template: str,
        parser_type_as_kwarg: Optional[Literal["insert", "indent", "insert_loop"]],
    ):
        self.template_holders[name] = TemplateHolder(
            name=name,
            template=template,
            formatted=template,
            parser_type_as_kwarg=parser_type_as_kwarg,
        )

    def get_template_holder_list(self) -> List[TemplateHolder]:
        return list(self.template_holders.values())

    def get_templates(self) -> List[str]:
        return [
            template_holder.template
            for template_holder in self.get_template_holder_list()
        ]

    def get_formatteds(self) -> List[str]:
        return [
            template_holder.formatted
            for template_holder in self.get_template_holder_list()
        ]

    def parse_greedy(
        self,
        template_name: Optional[str] = None,
        kwargs_buffer: int = 4,
        template_buffer: int = 4,
    ) -> Union[str, None]:
        self.parse_kwargs_greedy(buffer=kwargs_buffer)
        self.parse_template_greedy(buffer=template_buffer)
        if template_name is not None:
            template_holder = self.template_holders[template_name]
            formatted = template_holder.formatted
            return remove_lines(template=formatted)

    def parse_kwargs_greedy(self, buffer: int = 4) -> None:
        for _ in range(buffer):
            self.parse_kwargs_one_round()

    def parse_template_greedy(self, buffer: int = 4) -> None:
        for _ in range(buffer):
            self.parse_template_one_round()

    def parse_kwargs_one_round(self):
        for template_holder in self.get_template_holder_list():
            self.parse_single_template_using_kwargs(template_holder)

    def parse_template_one_round(self):
        for template_holder in self.get_template_holder_list():
            self.parse_single_template_using_templates_as_kwargs(template_holder)

    def parse_single_template_using_kwargs(self, template_holder: TemplateHolder):
        for kwargs_holder in self._get_kwargs_holder_list():
            formatted = _parse(
                template_holder.formatted,
                kwargs_holder.kwargs,
                kwargs_holder.parser_type,
            )
            template_holder.formatted = formatted

    def get_templates_as_kwargs(self) -> Dict[str, Any]:
        kwargs = {}
        for template in self.get_template_holder_list():
            kwargs[template.name] = template.formatted
        return kwargs

    def parse_single_template_using_templates_as_kwargs(
        self, template_holder: TemplateHolder
    ):
        formatted = template_holder.formatted

        for _template_holder in self.get_template_holder_list():
            key = _template_holder.name
            parser_type = _template_holder.parser_type_as_kwarg
            _formatted = _template_holder.formatted
            formatted = _parse(
                formatted, kwargs={key: _formatted}, parser_type=parser_type
            )
            template_holder.formatted = formatted

    def get_kwargs_holder(self, kwargs_name: str) -> KwargsHolder:
        return self.kwargs_holders[kwargs_name]

    def _get_kwargs_holder_list(self) -> List[KwargsHolder]:
        return list(self.kwargs_holders.values())


def _is_insert_loop_type(template: str):
    brackets = _get_brackets("insert_loop")
    if template.find(brackets["open"]) == -1:
        return False
    if template.find(brackets["close"]) == -1:
        return False
    return True


def _get_parser(parser_type: Literal["insert", "indent", "insert_loop"]) -> Callable[
    [
        str,  # text or template
        Union[Dict[str, Dict[str, str]], Dict[str, str]],  # kwargs
        str,  # open
        str,  # close
        bool,  # safe
    ],
    str,
]:

    parser_map = {
        "insert": format_insert_patch,
        "indent": format_indent_patch,
        "insert_loop": format_insert_loop,
    }

    return parser_map[parser_type]


def _get_brackets(
    parser_type: Literal["insert", "indent", "insert_loop"]
) -> Dict[str, str]:
    brackets_map = {
        "insert": {"open": r"\[", "close": r"\]"},
        "indent": {"open": r"\{", "close": r"\}"},
        "insert_loop": {"open": r"\\[", "close": r"\\]"},
    }
    return brackets_map[parser_type]


def _generate_key_with_brackets(key: str, parser_type: str):
    brackets = _get_brackets(parser_type)
    return brackets["open"] + key + brackets["close"]


def _add_kwargs_with_brackets_init(kwargs_holder: KwargsHolder):
    kwargs_with_brackets = {}
    for key, value in kwargs_holder.kwargs.items():
        key = _generate_key_with_brackets(key, kwargs_holder.parser_type)
        kwargs_with_brackets[key] = value


def _parse(template: str, kwargs: Dict[str, Any], parser_type: str):
    parser_fn = _get_parser(parser_type)

    # format_insert_loop uses loop. It can duplicate other templates.
    # Only if the parser_type is insert_loop, we use parser_fn
    if parser_type == "insert_loop":
        if _is_insert_loop_type(template):
            return parser_fn(template, kwargs)
        else:
            return template
    else:
        return parser_fn(template, kwargs)
