"""Ministry definitions with base corruption and capacity parameters."""

MINISTRIES: dict[int, dict] = {
    0:  {"name": "Finance",           "base_leakage": 0.15, "base_capacity": 0.80},
    1:  {"name": "Infrastructure",    "base_leakage": 0.35, "base_capacity": 0.55},
    2:  {"name": "Trade & Industry",  "base_leakage": 0.20, "base_capacity": 0.70},
    3:  {"name": "Labor",             "base_leakage": 0.20, "base_capacity": 0.65},
    4:  {"name": "Health",            "base_leakage": 0.30, "base_capacity": 0.50},
    5:  {"name": "Land & Housing",    "base_leakage": 0.40, "base_capacity": 0.45},
    6:  {"name": "Education",         "base_leakage": 0.25, "base_capacity": 0.55},
    7:  {"name": "Justice",           "base_leakage": 0.15, "base_capacity": 0.75},
    8:  {"name": "Defense",           "base_leakage": 0.30, "base_capacity": 0.70},
    9:  {"name": "Agriculture",       "base_leakage": 0.35, "base_capacity": 0.50},
    10: {"name": "Energy",            "base_leakage": 0.25, "base_capacity": 0.60},
    11: {"name": "Communications",    "base_leakage": 0.20, "base_capacity": 0.65},
}

N_MINISTRIES = len(MINISTRIES)
