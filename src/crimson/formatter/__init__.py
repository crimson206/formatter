from pydantic import BaseModel
from typing import Dict, Any, List, Literal, Optional
from crimson.formatter.templator_patch import format_indent_patch, format_insert_patch, format_insert_loop


"""
class DataFrame(BaseModel):
    name: str
    data_frame: pd.DataFrame
    _used_keys: List[str] = []
"""

parser_map = {"insert": format_insert_patch, "indent": format_indent_patch, "insert_loop": format_insert_loop}

brackets_map = {
    "insert": {"open": r"\[", "close": r"\]"},
    "indent": {"open": r"\{", "close": r"\}"},
    "insert_loop": {"open": r"\\[", "close": r"\\]"},
}


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
        self._add_kwargs_with_brackets_init(kwargs_holder)

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

    def get_kwargs_holder_list(self) -> List[KwargsHolder]:
        return list(self.kwargs_holders.values())

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

    def generate_key_with_brackets(self, key: str, parser_type: str):
        brackets = brackets_map[parser_type]
        return brackets['open'] + key + brackets['close']

    def get_kwargs(self) -> List[Dict[str, Any]]:
        return [kwargs_holder.kwargs for kwargs_holder in self.get_kwargs_holder_list()]

    def _add_kwargs_with_brackets_init(self, kwargs_holder: KwargsHolder):
        kwargs_with_brackets = {}
        for key, value in kwargs_holder.kwargs.items():
            key = self.generate_key_with_brackets(key, kwargs_holder.parser_type)
            kwargs_with_brackets[key] = value

    def parse_kwargs_one_round(self):
        for template_holder in self.get_template_holder_list():
            self.parse_single_template_using_kwargs(template_holder)

    def parse_template_one_round(self):
        for template_holder in self.get_template_holder_list():
            self.parse_single_template_using_templates_as_kwargs(template_holder)

    def parse_kwargs_greedy(self, buffer=4) -> None:
        for _ in range(buffer):
            self.parse_kwargs_one_round()

    def parse_template_greedy(self, buffer=4) -> None:
        for _ in range(buffer):
            self.parse_template_one_round()

    def parse(self, template: str, kwargs: Dict[str, Any], parser_type: str):
        parser_fn = parser_map[parser_type]
        if parser_type == "insert_loop":
            if _is_insert_loop_type(template):
                return parser_fn(template, kwargs)
            else:
                return template
        else:
            return parser_fn(template, kwargs)

    def parse_single_template_using_kwargs(self, template_holder: TemplateHolder):
        for kwargs_holder in self.get_kwargs_holder_list():
            formatted = self.parse(template_holder.formatted, kwargs_holder.kwargs, kwargs_holder.parser_type)
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
            formatted = self.parse(
                formatted, kwargs={key: _formatted}, parser_type=parser_type
            )
            template_holder.formatted = formatted

    def _count_key_in_templates(self, key_with_bracket: str) -> int:
        count = 0
        for template in self.get_templates():
            count += template.count(key_with_bracket)
        return

    def get_kwargs_holder(self, kwargs_name: str) -> KwargsHolder:
        return self.kwargs_holders[kwargs_name]

    def count_keys_with_bracket_in(
        self, kwargs_name, target: Literal["templates", "formatteds"]
    ):
        kwargs_holder = self.get_kwargs_holder(kwargs_name)
        counts = {}
        for key_with_bracket in kwargs_holder.kwargs_with_brackets.keys():
            count = 0
            if target == "templates":
                texts = self.get_templates()
            elif target == "formatteds":
                texts = self.get_formatteds()

            for template in texts:
                count += template.count(key_with_bracket)

            counts[key_with_bracket]
        return counts

    def count_keys_with_brackets_usages(self, kwargs_name: str) -> Dict[str, int]:
        counts_in_templates = self.count_keys_with_bracket_in(
            kwargs_name, target="templates"
        )
        counts_in_formatteds = self.count_keys_with_bracket_in(
            kwargs_name, target="formatteds"
        )

        usage_counts = {}

        for key_with_brackets in counts_in_templates.keys():
            usage_counts[key_with_brackets] = (
                counts_in_templates[key_with_brackets]
                - counts_in_formatteds[key_with_brackets]
            )

        return usage_counts


def _is_insert_loop_type(template: str):
    brackets = brackets_map['insert_loop']
    if template.find(brackets['open']) == -1:
        return False
    if template.find(brackets['close']) == -1:
        return False
    return True
