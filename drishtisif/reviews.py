from datetime import datetime
from pathlib import Path

import pandas as pd

REVIEW_FILE = Path(__file__).resolve().parent.parent / "data" / "reviews.csv"
COLUMNS = ["time", "description", "site", "predicted_flag", "probability", "rule", "decision", "comment"]


def save_review(result, decision, comment):
    row = {
        "time": datetime.now().isoformat(timespec="seconds"),
        "description": result["description"],
        "site": result["site"],
        "predicted_flag": int(result["sif_flag"]),
        "probability": result["sif_probability"],
        "rule": result["primary_rule"],
        "decision": decision,
        "comment": comment,
    }
    frame = pd.DataFrame([row], columns=COLUMNS)
    frame.to_csv(REVIEW_FILE, mode="a", header=not REVIEW_FILE.exists(), index=False)


def load_reviews():
    if not REVIEW_FILE.exists():
        return pd.DataFrame(columns=COLUMNS)
    return pd.read_csv(REVIEW_FILE)


def as_training_rows(reviews):
    if reviews.empty:
        return reviews
    truth = reviews["predicted_flag"].where(reviews["decision"] == "Confirm", 1 - reviews["predicted_flag"])
    return pd.DataFrame({"description": reviews["description"], "sif_label": truth.astype(int)})
