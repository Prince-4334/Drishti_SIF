RULES = {
    "Energy Isolation": [
        "isolation", "isolated", "lockout", "lock out", "loto", "tag out", "de-energ",
        "energized", "energised", "breaker", "live wire", "stored pressure", "blinded",
        "feeder", "mcc", "not switched off", "switching off",
    ],
    "Hot Work": [
        "hot work", "welding", "welder", "gas cutting", "grinding", "spark", "fire watch",
        "flammable", "flare", "naked flame", "gas testing",
    ],
    "Confined Space": [
        "confined space", "tank", "sump", "manhole", "vessel", "entry point",
        "oxygen", "standby person", "ventilation", "pit",
    ],
    "Line of Fire": [
        "line of fire", "under the suspended", "under the raised", "swing path",
        "swung", "tag line", "hammer union", "releasing pressure", "pressure testing",
        "struck by", "beneath", "slewed", "missed him",
    ],
    "Safe Mechanical Lifting": [
        "crane", "sling", "lift plan", "lifting", "hoist", "rigger", "forklift",
        "load chart", "load dropped", "shackle",
    ],
    "Working at Height": [
        "height", "harness", "scaffold", "lanyard", "derrick platform", "tank roof",
        "handrail", "monkey board", "fall arrest", "pipe rack",
    ],
    "Driving": [
        "driver", "driving", "reversed", "speed", "seatbelt", "seat belt",
        "tanker", "truck", "vehicle", "banksman",
    ],
    "Work Authorization": [
        "permit", "job safety analysis", "jsa", "toolbox", "sign-off", "authoriz",
        "authoris",
    ],
    "Bypassing Safety Controls": [
        "bypass", "jumper", "overrode", "interlock", "disabled", "trip",
        "alarm", "detector",
    ],
}

ENERGY_SOURCES = {
    "Electrical": ["electrical", "panel", "breaker", "live", "energized", "energised", "mcc", "feeder", "fuse"],
    "Suspended load": ["suspended", "crane", "sling", "hoist", "raised load", "lifting", "load"],
    "Pressure / hydrocarbon": ["pressure", "pressurised", "hydrocarbon", "gas smell", "leak", "flange", "flare", "condensate", "h2s"],
    "Fire / ignition": ["welding", "grinding", "gas cutting", "hot work", "spark", "flammable"],
    "Height": ["derrick", "scaffold", "tank roof", "monkey board", "pipe rack", "climbed", "at height", "harness"],
    "Moving vehicle": ["tanker", "truck", "vehicle", "reversed", "driver", "driving"],
    "Toxic / low oxygen": ["confined", "sump", "manhole", "tank for", "inside the", "oxygen", "vessel"],
    "Rotating machinery": ["coupling", "guard", "motor", "compressor", "mud pump"],
}

EXPOSURE_CUES = [
    "started work", "began", "opened", "entered", "went inside", "climbed", "standing",
    "stood", "walked under", "under the", "positioned", "was going on", "carried out",
    "removed", "working", "sitting inside", "took the", "moving", "reversed", "held",
]

BARRIER_FAILURES = {
    "Isolation not verified": [
        "without confirming", "isolation was verified", "not isolated", "without lockout",
        "breaker was found on", "without switching off", "not switched off",
        "isolation was not", "without isolation", "blinded off by mistake",
    ],
    "No work permit": [
        "without a work permit", "without hot work permit", "without entry permit",
        "no permit", "expired permit", "without permit", "without a job safety analysis",
        "without a toolbox talk", "sign-off",
    ],
    "Gas / oxygen test skipped": [
        "without gas testing", "without oxygen testing", "gas detector was not used",
        "before ventilation", "no fire watch",
    ],
    "Unsafe position": [
        "under the suspended", "under the raised", "swing path", "line of fire",
        "while the crane", "as the pipe swung", "still pressurised", "near the hammer union",
    ],
    "Fall protection missing": [
        "without a safety harness", "without anchoring", "incomplete scaffold",
        "handrail removed", "without a fall arrest", "no harness",
    ],
    "Lifting plan / rigging fault": [
        "without a lift plan", "damaged sling", "beyond the load chart", "uncertified rigger",
        "without checking the ground", "no tag line", "tag line was not used",
    ],
    "Safety device bypassed": [
        "bypass", "jumper", "overrode", "disabled", "without approval", "forgot to restore",
        "keep the plant running", "on bypass",
    ],
    "Barricade / supervision missing": [
        "no barricade", "without a standby", "without standby", "no banksman",
        "no one posted", "without wearing a seatbelt", "above the speed limit",
        "while using a mobile phone", "seat belt not", "after a long shift",
    ],
}

ACTIVITIES = {
    "Maintenance": ["maintenance", "repair", "overhaul", "fitter", "coupling"],
    "Electrical work": ["electrician", "panel", "fuse", "feeder", "mcc", "breaker"],
    "Lifting operations": ["crane", "lifting", "sling", "hoist", "forklift", "rigger"],
    "Hot work": ["welding", "welder", "grinding", "gas cutting", "hot work"],
    "Tank / vessel entry": ["tank", "sump", "manhole", "vessel"],
    "Drilling / rig ops": ["rig", "derrick", "mud pump", "casing", "monkey board", "drilling"],
    "Well and pipeline jobs": ["pipeline", "well servicing", "flange", "process line", "gas line", "hammer union"],
    "Vehicle movement": ["driver", "truck", "tanker", "vehicle", "driving"],
    "Working at height": ["scaffold", "tank roof", "pipe rack", "painter"],
    "Housekeeping": ["housekeeping", "walkway", "spill", "wet floor", "store room", "scrap"],
    "Process operation": ["operator", "separator", "trip", "interlock", "alarm", "detector"],
}

SITES = ["Duliajan", "Naharkatiya", "Moran", "Kumchai", "Tinsukia", "Jaisalmer"]

GENERIC_TERMS = {"occurred", "injury", "no injury", "started", "noticed", "stopped", "reported", "was", "and", "the", "not", "no", "supervisor", "in time"}
