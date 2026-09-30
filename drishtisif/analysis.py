import pandas as pd

from . import extract
from .model import key_terms, score

BANDS = [(0.7, "High"), (0.4, "Medium"), (0.0, "Low")]


def band_for(probability):
    for floor, name in BANDS:
        if probability >= floor:
            return name
    return "Low"


def reasons_for(text, probability, threshold, pipeline):
    energy = extract.find_energy(text)
    barriers = extract.find_barriers(text)
    exposure = extract.find_exposure(text)
    reasons = []
    if probability < threshold:
        reasons.append("No high-energy source with a missing barrier stands out in this report.")
        return reasons
    if energy:
        reasons.append(f"Energy source present: {', '.join(energy[:2])}.")
    if exposure:
        reasons.append(f"A person was exposed to it ('{exposure[0]}').")
    if barriers:
        reasons.append(f"Barrier failed: {', '.join(barriers[:2])}.")
    lowered = text.lower()
    if "no injury" in lowered or "near miss" in lowered:
        reasons.append("Nobody was hurt, but the same conditions could have caused a fatality.")
    terms = key_terms(pipeline, text)
    if terms:
        reasons.append(f"Phrases the model weighed most: {', '.join(terms)}.")
    return reasons


def pattern_for(activity, energy, barriers):
    energy_name = energy[0] if energy else "unclear energy"
    barrier_name = barriers[0] if barriers else "unclear barrier"
    return f"{activity} + {energy_name} + {barrier_name}"


def analyse_one(text, pipeline, threshold, site=None):
    probability = float(score(pipeline, [text])[0])
    energy = extract.find_energy(text)
    barriers = extract.find_barriers(text)
    activity = extract.find_activity(text)
    rules = extract.find_rules(text)
    return {
        "description": text,
        "site": site or extract.find_site(text),
        "sif_probability": round(probability, 3),
        "sif_flag": probability >= threshold,
        "band": band_for(probability),
        "rules": rules,
        "primary_rule": rules[0] if rules else "No specific rule",
        "activity": activity,
        "energy": energy[0] if energy else "Unclear",
        "barrier": barriers[0] if barriers else "Unclear",
        "pattern": pattern_for(activity, energy, barriers),
        "reasons": reasons_for(text, probability, threshold, pipeline),
    }


def analyse_frame(frame, pipeline, threshold):
    frame = frame.copy().reset_index(drop=True)
    texts = frame["description"].astype(str)
    probabilities = score(pipeline, texts)
    energy = [extract.find_energy(text) for text in texts]
    barriers = [extract.find_barriers(text) for text in texts]
    rules = [extract.find_rules(text) for text in texts]
    frame["activity"] = [extract.find_activity(text) for text in texts]
    if "site" not in frame.columns:
        frame["site"] = [extract.find_site(text) for text in texts]
    frame["sif_probability"] = probabilities.round(3)
    frame["sif_flag"] = probabilities >= threshold
    frame["band"] = [band_for(value) for value in probabilities]
    frame["primary_rule"] = [found[0] if found else "No specific rule" for found in rules]
    frame["energy"] = [found[0] if found else "Unclear" for found in energy]
    frame["barrier"] = [found[0] if found else "Unclear" for found in barriers]
    frame["pattern"] = [
        pattern_for(activity, e, b) for activity, e, b in zip(frame["activity"], energy, barriers)
    ]
    if "date" in frame.columns:
        frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    return frame


def pick_text_column(frame):
    if "description" in frame.columns:
        return "description"
    text_columns = [name for name in frame.columns if frame[name].dtype == object]
    if not text_columns:
        return None
    return max(text_columns, key=lambda name: frame[name].astype(str).str.len().mean())


def site_density(scored):
    grouped = scored.groupby("site").agg(reports=("sif_flag", "size"), sif=("sif_flag", "sum"))
    grouped["density"] = (grouped["sif"] / grouped["reports"] * 100).round(1)
    return grouped.sort_values("density", ascending=False).reset_index()


def activity_density(scored, minimum=5):
    grouped = scored.groupby("activity").agg(reports=("sif_flag", "size"), sif=("sif_flag", "sum"))
    grouped = grouped[grouped["reports"] >= minimum]
    grouped["density"] = (grouped["sif"] / grouped["reports"] * 100).round(1)
    return grouped.sort_values("density", ascending=False).reset_index()


def recurring_patterns(scored, limit=8):
    flagged = scored[scored["sif_flag"]]
    counts = flagged["pattern"].value_counts().head(limit)
    return counts.rename_axis("pattern").reset_index(name="reports")


def focus_lines(scored):
    lines = []
    flagged = scored[scored["sif_flag"]]
    if flagged.empty:
        return ["No report is flagged at this threshold."]
    sites = site_density(scored)
    top = sites.iloc[0]
    site_reports = flagged[flagged["site"] == top["site"]]
    lines.append(
        f"{top['site']} has the highest SIF-precursor density: {top['density']:.0f}% of its reports "
        f"({int(top['sif'])} of {int(top['reports'])}) carry fatal potential."
    )
    if not site_reports.empty:
        lines.append(f"Most repeated pattern there: {site_reports['pattern'].value_counts().index[0]}.")
    activities = activity_density(scored[scored["activity"] != "Other"])
    if not activities.empty:
        lines.append(f"Riskiest activity overall: {activities.iloc[0]['activity']} ({activities.iloc[0]['density']:.0f}% flagged).")
    barrier_counts = flagged[flagged["barrier"] != "Unclear"]["barrier"].value_counts()
    if not barrier_counts.empty:
        lines.append(f"Barrier that fails most often: {barrier_counts.index[0]} ({barrier_counts.iloc[0]} reports).")
    return lines
