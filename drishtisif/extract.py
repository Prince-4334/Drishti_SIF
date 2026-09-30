from .lexicon import (
    ACTIVITIES,
    BARRIER_FAILURES,
    ENERGY_SOURCES,
    EXPOSURE_CUES,
    RULES,
    SITES,
)


def _matches(text, table):
    found = {}
    for name, words in table.items():
        hits = [word for word in words if word in text]
        if hits:
            found[name] = hits
    return found


def _ranked(found):
    return sorted(found, key=lambda name: len(found[name]), reverse=True)


def find_rules(text):
    found = _matches(text.lower(), RULES)
    return _ranked(found)[:3]


def find_energy(text):
    return _ranked(_matches(text.lower(), ENERGY_SOURCES))


def find_barriers(text):
    return _ranked(_matches(text.lower(), BARRIER_FAILURES))


def find_exposure(text):
    lowered = text.lower()
    return [cue for cue in EXPOSURE_CUES if cue in lowered]


def find_activity(text):
    ranked = _ranked(_matches(text.lower(), ACTIVITIES))
    return ranked[0] if ranked else "Other"


def find_site(text):
    for site in SITES:
        if site.lower() in text.lower():
            return site
    return "Unknown"
