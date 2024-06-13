import re

def extract_text_between_brackets(template, open, close):
    pattern = fr'{re.escape(open)}(.*?){re.escape(close)}'
    matches = re.findall(pattern, template)
    filtered_matches = [match for match in matches if not match.endswith('\\')]
    return filtered_matches
