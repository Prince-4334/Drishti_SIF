import pandas as pd
import pytest

from drishtisif import analysis, extract, model, reviews


@pytest.fixture(scope="module")
def pipeline():
    return model.load_model()


def test_risky_report_is_flagged(pipeline):
    text = "Rigger was standing under the suspended load while the crane was lifting. No injury occurred."
    result = analysis.analyse_one(text, pipeline, 0.5)
    assert result["sif_flag"]
    assert result["primary_rule"] in ("Safe Mechanical Lifting", "Line of Fire")
    assert result["reasons"]


def test_routine_report_is_not_flagged(pipeline):
    text = "Register entry was missed by the security guard. Reminder issued."
    assert not analysis.analyse_one(text, pipeline, 0.5)["sif_flag"]


def test_extraction_finds_site_and_activity():
    text = "Welder started gas cutting near pump P-204 at Jaisalmer without hot work permit."
    assert extract.find_site(text) == "Jaisalmer"
    assert extract.find_activity(text) == "Hot work"
    assert "Hot Work" in extract.find_rules(text)


def test_frame_analysis_and_density(pipeline):
    frame = pd.DataFrame(
        {
            "description": [
                "Worker entered the tank without oxygen testing at Moran.",
                "Loose cables on the walkway at Moran.",
            ]
        }
    )
    scored = analysis.analyse_frame(frame, pipeline, 0.5)
    density = analysis.site_density(scored)
    assert density.loc[0, "reports"] == 2
    assert density.loc[0, "sif"] == 1


def test_rejected_review_flips_label():
    log = pd.DataFrame(
        {"description": ["a", "b"], "predicted_flag": [1, 1], "decision": ["Confirm", "Reject"]}
    )
    rows = reviews.as_training_rows(log)
    assert list(rows["sif_label"]) == [1, 0]
