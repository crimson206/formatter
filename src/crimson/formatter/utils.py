import re
from typing import List


def extract_text_between_brackets(template: str, open: str, close: str) -> List[str]:
    pattern = rf"{re.escape(open)}(.*?){re.escape(close)}"
    matches = re.findall(pattern, template)
    filtered_matches = [match for match in matches if not match.endswith("\\")]
    return filtered_matches
