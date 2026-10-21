# Saare numbers PLACEHOLDER hain. ICAR / IRRI / IGKV se verify karo.
# low = is nami (%) se kam ho to sinchai; rain_skip = 3 din mein itni baarish (mm) aaye to sinchai mat karo
CROPS = {
    "rice_dsr": {
        "name": "Dhaan (DSR)", "name_hi": "धान", "alt": "soybean", "sow_min": 22,
        "stages": {
            "sowing":        {"kc": 1.05, "critical": False, "low": 25, "rain_skip": 15},
            "tillering":     {"kc": 1.10, "critical": True,  "low": 30, "rain_skip": 15},
            "flowering":     {"kc": 1.20, "critical": True,  "low": 35, "rain_skip": 15},
            "grain_filling": {"kc": 0.90, "critical": True,  "low": 30, "rain_skip": 15},
        }},
    "wheat": {
        "name": "Gehu", "name_hi": "गेहूं", "alt": "chana", "sow_min": 18,
        "stages": {
            "sowing":        {"kc": 0.40, "critical": False, "low": 20, "rain_skip": 12},
            "crown_root":    {"kc": 0.70, "critical": True,  "low": 22, "rain_skip": 12},
            "tillering":     {"kc": 1.00, "critical": True,  "low": 22, "rain_skip": 12},
            "flowering":     {"kc": 1.15, "critical": True,  "low": 25, "rain_skip": 12},
            "grain_filling": {"kc": 0.60, "critical": True,  "low": 22, "rain_skip": 12},
        }},
    "chana": {
        "name": "Chana", "name_hi": "चना", "alt": "wheat", "sow_min": 15,
        "stages": {
            "sowing":      {"kc": 0.40, "critical": False, "low": 15, "rain_skip": 10},
            "branching":   {"kc": 0.80, "critical": True,  "low": 17, "rain_skip": 10},
            "flowering":   {"kc": 1.00, "critical": True,  "low": 18, "rain_skip": 10},
            "pod_filling": {"kc": 0.85, "critical": True,  "low": 17, "rain_skip": 10},
        }},
    "soybean": {
        "name": "Soybean", "name_hi": "सोयाबीन", "alt": "chana", "sow_min": 20,
        "stages": {
            "sowing":      {"kc": 0.40, "critical": False, "low": 22, "rain_skip": 15},
            "flowering":   {"kc": 1.10, "critical": True,  "low": 28, "rain_skip": 15},
            "pod_filling": {"kc": 1.00, "critical": True,  "low": 26, "rain_skip": 15},
        }},
}