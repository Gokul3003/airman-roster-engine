import os
import re


# -------------------------------------------------
# 1️⃣ Load Markdown File (Knowledge Source)
# -------------------------------------------------

RULE_FILE_PATH = os.path.join(
    os.path.dirname(__file__),
    "..",
    "data_bucket",
    "weather_minima.md"
)


def parse_markdown_rules():

    with open(RULE_FILE_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    sections = re.split(r"### ", content)[1:]

    rules = {}

    for section in sections:
        lines = section.strip().split("\n")
        header = lines[0].strip()  # e.g. BASIC - CIRCUITS

        ceiling_match = re.search(r"Ceiling >= (\d+)", section)
        visibility_match = re.search(r"Visibility >= (\d+)", section)

        if ceiling_match and visibility_match:
            key = header.replace(" - ", "_").replace(" ", "_").upper()

            rules[key] = {
                "min_ceiling": int(ceiling_match.group(1)),
                "min_visibility": int(visibility_match.group(1))
            }

    return rules


# -------------------------------------------------
# 2️⃣ Parse Once (Global Cache)
# -------------------------------------------------

PARSED_RULES = parse_markdown_rules()


# -------------------------------------------------
# 3️⃣ Evaluate Weather (RAG-Grounded)
# -------------------------------------------------

def evaluate_weather(stage, sortie_type, weather_data):

    if weather_data.get("confidence") == "LOW":
        return {
            "dispatch_decision": "NEEDS_REVIEW",
            "rule_chunk": "WEATHER_UNAVAILABLE",
            "citation": "rules:weather_minima#WEATHER_UNAVAILABLE"
        }

    stage = stage.upper()
    sortie_type = sortie_type.upper()

    key = f"{stage}_{sortie_type}"

    rule = None
    rule_key = None

    if sortie_type == "SOLO" and "SOLO" in PARSED_RULES:
        rule = PARSED_RULES["SOLO"]
        rule_key = "SOLO"

    elif key in PARSED_RULES:
        rule = PARSED_RULES[key]
        rule_key = key

    if not rule:
        return {
            "dispatch_decision": "NEEDS_REVIEW",
            "rule_chunk": "UNKNOWN_RULE",
            "citation": "rules:weather_minima#UNKNOWN_RULE"
        }

    min_ceiling = rule["min_ceiling"]
    min_visibility = rule["min_visibility"]

    ceiling = weather_data.get("ceiling")
    visibility = weather_data.get("visibility")

    if ceiling < min_ceiling:
        return {
            "dispatch_decision": "NO_GO",
            "rule_chunk": rule_key,
            "citation": f"rules:weather_minima#{rule_key}"
        }

    if visibility < min_visibility:
        return {
            "dispatch_decision": "NO_GO",
            "rule_chunk": rule_key,
            "citation": f"rules:weather_minima#{rule_key}"
        }

    return {
        "dispatch_decision": "GO",
        "rule_chunk": rule_key,
        "citation": f"rules:weather_minima#{rule_key}"
    }