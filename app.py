from datetime import date

import pandas as pd
import streamlit as st

from drishtisif import analysis, charts, model, reviews
from drishtisif.lexicon import SITES
from drishtisif.model import ROOT

st.set_page_config(page_title="DrishtiSIF", layout="wide")

st.html(
    """
<style>
.block-container {padding-top: 4rem; max-width: 1250px;}
.brand {font-size: 2.3rem; font-weight: 600; letter-spacing: -0.02em; margin: 0;}
.brand span {color: #eb6834;}
.tagline {color: #52514e; margin: 0 0 1.2rem 0;}
.big {font-size: 2.6rem; font-weight: 600; line-height: 1.1; margin: 0;}
.small {color: #52514e; font-size: 0.9rem; margin: 0;}
</style>
"""
)


@st.cache_resource
def get_model():
    return model.load_model()


@st.cache_data
def demo_reports():
    return pd.read_csv(ROOT / "data" / "demo_reports.csv")


@st.cache_data
def score_reports(frame, threshold, _pipeline):
    return analysis.analyse_frame(frame, _pipeline, threshold)


@st.cache_data
def model_check():
    return model.evaluate()


def load_source():
    choice = st.sidebar.radio("Reports to analyse", ["Demo reports (synthetic)", "Upload my own CSV"])
    if choice.startswith("Demo"):
        return demo_reports()
    upload = st.sidebar.file_uploader("CSV file", type="csv")
    if upload is None:
        st.sidebar.info("Upload a CSV with a free-text column. Optional columns: site, date, report_id.")
        return None
    frame = pd.read_csv(upload)
    column = analysis.pick_text_column(frame)
    if column is None:
        st.sidebar.error("No text column found in this file.")
        return None
    return frame.rename(columns={column: "description"}) if column != "description" else frame


def session_frame():
    rows = st.session_state.get("analysed", [])
    if not rows:
        return pd.DataFrame()
    keep = ["description", "site", "sif_probability", "sif_flag", "band", "primary_rule",
            "activity", "energy", "barrier", "pattern", "date"]
    frame = pd.DataFrame(rows)[keep]
    frame["date"] = pd.to_datetime(frame["date"])
    return frame


def show_result(result, dataset):
    left, middle, right = st.columns(3)
    with left.container(border=True):
        st.html("<p class='small'>SIF potential</p>")
        st.html(f"<p class='big'>{result['sif_probability'] * 100:.0f}%</p>")
        st.html(f"<p class='small'>{result['band']} band</p>")
    with middle.container(border=True):
        st.html("<p class='small'>IOGP Life-Saving Rule</p>")
        st.html(f"<p class='big' style='font-size:1.7rem'>{result['primary_rule']}</p>")
        others = [rule for rule in result["rules"] if rule != result["primary_rule"]]
        st.html(f"<p class='small'>{'Also: ' + ', '.join(others) if others else 'Single rule matched'}</p>")
    with right.container(border=True):
        st.html("<p class='small'>Verdict</p>")
        verdict = "Flag for HSE review" if result["sif_flag"] else "Routine"
        st.html(f"<p class='big' style='font-size:1.7rem'>{verdict}</p>")
        st.html(f"<p class='small'>{result['activity']} at {result['site']}</p>")

    why, pattern = st.columns(2)
    with why.container(border=True):
        st.subheader("Why this could be fatal" if result["sif_flag"] else "Why it looks routine")
        for reason in result["reasons"]:
            st.markdown(f"- {reason}")
    with pattern.container(border=True):
        st.subheader("Failure pattern")
        st.markdown(f"**{result['pattern']}**")
        if dataset is not None and len(dataset):
            seen = int(((dataset["pattern"] == result["pattern"]) & dataset["sif_flag"]).sum())
            st.markdown(f"Seen in **{seen}** flagged reports in the loaded data.")


def review_box(result):
    with st.container(border=True):
        st.subheader("Your review")
        if st.session_state.get("reviewed"):
            st.success("Review saved. Thank you, it will be used the next time the model is retrained.")
            return
        comment = st.text_input("Comment (optional)", key="review_comment")
        agree, disagree, _ = st.columns([1, 1, 4])
        if agree.button("Confirm", type="primary"):
            reviews.save_review(result, "Confirm", comment)
            st.session_state["reviewed"] = True
            st.rerun()
        if disagree.button("Reject"):
            reviews.save_review(result, "Reject", comment)
            st.session_state["reviewed"] = True
            st.rerun()


def analyse_tab(pipeline, threshold, dataset):
    st.markdown("Paste one HSSE report. You get the SIF verdict, the Life-Saving Rule, the reasons and the failure pattern, then you confirm or reject it.")
    with st.form("report_form"):
        text = st.text_area(
            "Report text",
            height=130,
            placeholder="During maintenance of pump P-204, technician started work without confirming electrical isolation. No injury occurred.",
        )
        site = st.selectbox("Site", ["Detect from text"] + SITES)
        submitted = st.form_submit_button("Analyse report", type="primary")
    if submitted:
        if len(text.strip()) < 15:
            st.warning("Please enter a fuller report, at least a sentence.")
        else:
            chosen = None if site == "Detect from text" else site
            result = analysis.analyse_one(text.strip(), pipeline, threshold, chosen)
            result["date"] = date.today().isoformat()
            st.session_state["latest"] = result
            st.session_state["reviewed"] = False
            st.session_state.setdefault("analysed", []).append(result)
    latest = st.session_state.get("latest")
    if latest:
        show_result(latest, dataset)
        review_box(latest)


def dashboard_tab(dataset):
    if dataset is None or dataset.empty:
        st.info("Choose demo reports or upload a CSV in the sidebar.")
        return
    total = len(dataset)
    flagged = int(dataset["sif_flag"].sum())
    sites = analysis.site_density(dataset)
    rules = dataset[dataset["sif_flag"]]["primary_rule"].value_counts()

    cards = st.columns(4)
    values = [
        ("Reports analysed", f"{total:,}"),
        ("Flagged as SIF potential", f"{flagged:,}"),
        ("Highest-density site", sites.iloc[0]["site"]),
        ("Most common rule", rules.index[0] if len(rules) else "None"),
    ]
    for card, (label, value) in zip(cards, values):
        with card.container(border=True):
            st.html(f"<p class='small'>{label}</p>")
            st.html(f"<p class='big' style='font-size:1.8rem'>{value}</p>")

    with st.container(border=True):
        st.subheader("Where to act first")
        for line in analysis.focus_lines(dataset):
            st.markdown(f"- {line}")

    a, b = st.columns([1, 1.4])
    with a.container(border=True):
        st.subheader("SIF potential vs routine")
        st.plotly_chart(charts.flag_donut(dataset), width="stretch")
    with b.container(border=True):
        st.subheader("Life-Saving Rules behind flagged reports")
        st.plotly_chart(charts.rule_bars(dataset), width="stretch")

    c, d = st.columns(2)
    with c.container(border=True):
        st.subheader("SIF-precursor density by site")
        st.caption("Share of a site's reports that carry fatal potential")
        st.plotly_chart(charts.density_bars(sites), width="stretch")
    with d.container(border=True):
        st.subheader("SIF-precursor density by activity")
        st.caption("Share of an activity's reports that carry fatal potential (activities with 5 or more reports)")
        activities = analysis.activity_density(dataset)
        st.plotly_chart(charts.density_bars(activities, "activity"), width="stretch")

    with st.container(border=True):
        st.subheader("Site and activity hotspots")
        st.caption("Number of flagged reports in each site and activity")
        st.plotly_chart(charts.heatmap(dataset), width="stretch")

    e, f = st.columns(2)
    with e.container(border=True):
        st.subheader("Barriers that fail most often")
        st.plotly_chart(charts.barrier_bars(dataset), width="stretch")
    with f.container(border=True):
        st.subheader("Recurring failure patterns")
        st.caption("Activity + energy source + failed barrier")
        st.plotly_chart(charts.pattern_bars(analysis.recurring_patterns(dataset)), width="stretch")

    trend = charts.trend_line(dataset)
    if trend is not None:
        with st.container(border=True):
            st.subheader("Trend over time")
            st.plotly_chart(trend, width="stretch")

    with st.container(border=True):
        st.subheader("Review these first")
        queue = dataset[dataset["sif_flag"]].sort_values("sif_probability", ascending=False).copy()
        if "date" in queue.columns:
            queue["date"] = queue["date"].dt.strftime("%Y-%m-%d")
        columns = [name for name in ["date", "site", "activity", "primary_rule", "sif_probability", "description"] if name in queue.columns]
        st.dataframe(queue[columns].head(25), width="stretch", hide_index=True)
        st.download_button("Download all flagged reports", queue[columns].to_csv(index=False), "flagged_reports.csv", "text/csv")


def review_tab(pipeline):
    log = reviews.load_reviews()
    if log.empty:
        st.info("No reviews yet. Analyse a report and press Confirm or Reject.")
        return
    confirmed = int((log["decision"] == "Confirm").sum())
    st.markdown(f"**{len(log)}** reviews saved: **{confirmed}** confirmed, **{len(log) - confirmed}** rejected.")
    st.dataframe(log.iloc[::-1], width="stretch", hide_index=True)
    if st.button("Retrain model with these reviews", type="primary"):
        model.train_and_save(reviews.as_training_rows(log))
        st.cache_resource.clear()
        st.cache_data.clear()
        st.success("Model retrained. New reports will use the updated model.")


def main():
    st.html("<p class='brand'>Drishti<span>SIF</span></p>")
    st.html("<p class='tagline'>Spot the safety reports that could have cost a life.</p>")

    pipeline = get_model()
    threshold = st.sidebar.slider("SIF flag threshold", 0.30, 0.90, 0.50, 0.05,
                                  help="Lower it to catch more fatal-potential reports at the cost of more false alarms.")
    frame = load_source()
    include_session = st.sidebar.checkbox("Include reports I analysed here", value=True)

    dataset = score_reports(frame, threshold, pipeline) if frame is not None else None
    extra = session_frame()
    if include_session and not extra.empty:
        extra["sif_flag"] = extra["sif_probability"] >= threshold
        dataset = pd.concat([dataset, extra], ignore_index=True) if dataset is not None else extra

    with st.sidebar.expander("How good is the model?"):
        check = model_check()
        st.markdown("Scores use synthetic reports, so treat them as a sanity check, not proof.")
        st.markdown(
            f"Held-out synthetic reports: recall **{check['template_holdout']['recall']:.0%}**, "
            f"precision **{check['template_holdout']['precision']:.0%}**"
        )
        st.markdown(
            f"{check['handwritten']['reports']} hand-written reports: recall "
            f"**{check['handwritten']['recall']:.0%}**, precision **{check['handwritten']['precision']:.0%}**"
        )

    analyse, dashboard, log = st.tabs(["Analyse a report", "Dashboard", "Review log"])
    with analyse:
        analyse_tab(pipeline, threshold, dataset)
    with dashboard:
        dashboard_tab(dataset)
    with log:
        review_tab(pipeline)


main()
