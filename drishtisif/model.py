from pathlib import Path

import joblib
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import precision_recall_fscore_support
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline

from .lexicon import GENERIC_TERMS
from .synthetic import make_reports

ROOT = Path(__file__).resolve().parent.parent
MODEL_FILE = ROOT / "models" / "sif_model.joblib"
TRAIN_FILE = ROOT / "data" / "training_reports.csv"
CHECK_FILE = ROOT / "data" / "handwritten_checks.csv"


def new_pipeline():
    return make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True),
        LogisticRegression(C=3.0, class_weight="balanced", max_iter=1000),
    )


def training_frame():
    if not TRAIN_FILE.exists():
        TRAIN_FILE.parent.mkdir(exist_ok=True)
        make_reports(2600, seed=7, with_dates=False, label_noise=0.03).to_csv(TRAIN_FILE, index=False)
    return pd.read_csv(TRAIN_FILE)


def fit(frame):
    pipeline = new_pipeline()
    pipeline.fit(frame["description"], frame["sif_label"])
    return pipeline


def train_and_save(extra=None):
    frame = training_frame()
    if extra is not None and len(extra):
        frame = pd.concat([frame, extra], ignore_index=True)
    pipeline = fit(frame)
    MODEL_FILE.parent.mkdir(exist_ok=True)
    joblib.dump(pipeline, MODEL_FILE)
    return pipeline


def load_model():
    if MODEL_FILE.exists():
        return joblib.load(MODEL_FILE)
    return train_and_save()


def score(pipeline, texts):
    return pipeline.predict_proba(list(texts))[:, 1]


def key_terms(pipeline, text, limit=4):
    vectorizer = pipeline.steps[0][1]
    classifier = pipeline.steps[-1][1]
    row = vectorizer.transform([text])
    contribution = row.multiply(classifier.coef_[0]).tocoo()
    names = vectorizer.get_feature_names_out()
    pairs = sorted(zip(contribution.data, contribution.col), reverse=True)
    terms = [names[col] for value, col in pairs if value > 0]
    return [term for term in terms if term not in GENERIC_TERMS][:limit]


def evaluate(threshold=0.5):
    frame = training_frame()
    train, test = train_test_split(frame, test_size=0.25, random_state=3, stratify=frame["sif_label"])
    pipeline = fit(train)
    report = {}
    holdout = score(pipeline, test["description"]) >= threshold
    report["template_holdout"] = _summary(test["sif_label"], holdout)
    checks = pd.read_csv(CHECK_FILE)
    handwritten = score(load_model(), checks["description"]) >= threshold
    report["handwritten"] = _summary(checks["sif_label"], handwritten)
    return report


def _summary(truth, predicted):
    precision, recall, f1, _ = precision_recall_fscore_support(
        truth, predicted, average="binary", zero_division=0
    )
    return {
        "precision": round(float(precision), 3),
        "recall": round(float(recall), 3),
        "f1": round(float(f1), 3),
        "reports": int(len(truth)),
    }
