from datetime import datetime, timedelta

# Simple in-memory cache
_weather_cache = {}

CACHE_TTL_MINUTES = 15

# Deterministic weather scenarios (for testing & stability)
WEATHER_SCENARIOS = {
    "S1": {"ceiling": 1000, "visibility": 5, "wind": 10},
    "S2": {"ceiling": 3000, "visibility": 10, "wind": 8},
    "S3": {"ceiling": 2000, "visibility": 8, "wind": 12},
    "S4": {"ceiling": 5000, "visibility": 10, "wind": 5},
}


def map_time_to_slot(start_time):
    if start_time == "07:00":
        return "S1"
    if start_time == "09:30":
        return "S2"
    if start_time == "12:00":
        return "S3"
    if start_time == "14:30":
        return "S4"
    return None


def get_weather(icao: str, start_time: str, end_time: str):
    """
    PDF-compliant interface.
    """

    slot_id = map_time_to_slot(start_time)

    cache_key = f"{icao}_{start_time}_{end_time}"

    if cache_key in _weather_cache:
        cached = _weather_cache[cache_key]
        if datetime.utcnow() - cached["fetched_at"] < timedelta(minutes=CACHE_TTL_MINUTES):
            return cached
    
    if slot_id and slot_id in WEATHER_SCENARIOS:
        weather_data = WEATHER_SCENARIOS[slot_id]

        result = {
            "ceiling": weather_data["ceiling"],
            "visibility": weather_data["visibility"],
            "wind": weather_data["wind"],
            "fetched_at": datetime.utcnow(),
            "confidence": "HIGH"
        }

        _weather_cache[cache_key] = result
        return result

    return {
        "ceiling": None,
        "visibility": None,
        "wind": None,
        "fetched_at": datetime.utcnow(),
        "confidence": "LOW"
    }