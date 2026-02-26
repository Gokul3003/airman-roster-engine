import re,os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RULES_FILE_PATH = os.path.join(BASE_DIR, "data_bucket", "weather_minima.md")

def parse_weather_rules():
    rules = {}
    current_key = None

    with open(RULES_FILE_PATH, "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()

        # Detect rule header
        if line.startswith("###"):
            header = line.replace("###", "").strip()

            # Examples:
            # BASIC - CIRCUITS
            # ADVANCED - NAV
            # SOLO
            # CHECKRIDE - CHK_PREP

            if "-" in header:
                stage, sortie = [x.strip() for x in header.split("-")]
            else:
                stage = header.strip()
                sortie = None

            current_key = f"{stage}_{sortie}" if sortie else stage

            rules[current_key] = {
                "stage": stage.upper(),
                "sortie": sortie.upper() if sortie else None,
                "min_ceiling": None,
                "min_visibility": None
            }

            continue

        if current_key:
            if "Ceiling" in line:
                value = int(re.findall(r"\d+", line)[0])
                rules[current_key]["min_ceiling"] = value

            if "Visibility" in line:
                value = int(re.findall(r"\d+", line)[0])
                rules[current_key]["min_visibility"] = value

    return rules

# Load rules once at startup
PARSED_RULES = parse_weather_rules()

def evaluate_weather(stage, sortie_type, weather_data):

    # Weather unavailable
    if weather_data["confidence"] == "LOW":
        return {
            "dispatch_decision": "NEEDS_REVIEW",
            "rule_chunk": "WEATHER_UNAVAILABLE"
        }

    stage = stage.upper()
    sortie_type = sortie_type.upper()

    key = f"{stage}_{sortie_type}"

    # SOLO special case (if exists)
    if sortie_type == "SOLO" and "SOLO" in PARSED_RULES:
        rule = PARSED_RULES["SOLO"]
        rule_key = "SOLO"
    elif key in PARSED_RULES:
        rule = PARSED_RULES[key]
        rule_key = key
    else:
        return {
            "dispatch_decision": "NEEDS_REVIEW",
            "rule_chunk": "UNKNOWN_RULE"
        }

    # Ceiling check
    if weather_data["ceiling"] < rule["min_ceiling"]:
        return {
            "dispatch_decision": "NO_GO",
            "rule_chunk": rule_key
        }

    # Visibility check
    if weather_data["visibility"] < rule["min_visibility"]:
        return {
            "dispatch_decision": "NO_GO",
            "rule_chunk": rule_key
        }

    return {
        "dispatch_decision": "GO",
        "rule_chunk": rule_key
    }