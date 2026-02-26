import os
import re


RULE_FILE_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "data_bucket",
    "weather_minima.md"  # adjust filename if needed
)


def load_markdown_rules():
    with open(RULE_FILE_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    # Split by section headers
    sections = re.split(r"### ", content)[1:]

    rules = {}

    for section in sections:
        lines = section.strip().split("\n")
        header = lines[0].strip()  # e.g., BASIC - CIRCUITS
        body = "\n".join(lines[1:])

        ceiling_match = re.search(r"Ceiling >= (\d+)", body)
        visibility_match = re.search(r"Visibility >= (\d+)", body)

        if ceiling_match and visibility_match:
            rules[header] = {
                "min_ceiling": int(ceiling_match.group(1)),
                "min_visibility": int(visibility_match.group(1)),
                "citation": f"rules:weather_minima#{header.replace(' ', '_')}"
            }

    return rules


def retrieve_rule(stage, sortie_type):
    rules = load_markdown_rules()

    for header, data in rules.items():
        if stage in header and sortie_type in header:
            return header, data

    return None, None