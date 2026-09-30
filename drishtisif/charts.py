import pandas as pd
import plotly.graph_objects as go

BLUE = "#2a78d6"
ORANGE = "#eb6834"
INK = "#0b0b0b"
MUTED = "#52514e"
GRID = "#e6e5e1"
HEAT = [[0.0, "#fdf0ea"], [0.35, "#f7b79a"], [0.7, "#eb6834"], [1.0, "#7a2a0e"]]


def _style(fig, height=320):
    fig.update_layout(
        height=height,
        margin=dict(l=8, r=70, t=8, b=8),
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=MUTED, size=13),
        legend=dict(orientation="h", y=-0.12),
    )
    return fig


def _hbar(labels, values, texts, height=320):
    fig = go.Figure(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            marker=dict(color=ORANGE, cornerradius=4),
            text=texts,
            textposition="outside",
            cliponaxis=False,
            hoverinfo="skip",
        )
    )
    fig.update_yaxes(autorange="reversed", showgrid=False, tickfont=dict(color=INK))
    fig.update_xaxes(showgrid=True, gridcolor=GRID, zeroline=False, showticklabels=False)
    if len(values):
        fig.update_xaxes(range=[0, max(values) * 1.35])
    fig.update_layout(bargap=0.35, showlegend=False)
    return _style(fig, height)


def flag_donut(scored):
    flagged = int(scored["sif_flag"].sum())
    routine = int(len(scored) - flagged)
    share = flagged / max(len(scored), 1) * 100
    fig = go.Figure(
        go.Pie(
            labels=["SIF potential", "Routine"],
            values=[flagged, routine],
            hole=0.62,
            sort=False,
            marker=dict(colors=[ORANGE, BLUE], line=dict(color="#fcfcfb", width=2)),
            textinfo="value",
            textfont=dict(color="#ffffff", size=14),
        )
    )
    fig.add_annotation(text=f"{share:.0f}%", showarrow=False, font=dict(size=30, color=INK), y=0.54)
    fig.add_annotation(text="flagged", showarrow=False, font=dict(size=13, color=MUTED), y=0.42)
    return _style(fig, 300)


def rule_bars(scored):
    counts = scored[scored["sif_flag"]]["primary_rule"].value_counts()
    if counts.empty:
        return _hbar([], [], [])
    return _hbar(list(counts.index), list(counts.values), [str(v) for v in counts.values], 330)


def density_bars(density, label_column="site"):
    texts = [f"{row.density:.0f}%  ({int(row.sif)} of {int(row.reports)})" for row in density.itertuples()]
    return _hbar(list(density[label_column]), list(density["density"]), texts, 330)


def heatmap(scored):
    flagged = scored[scored["sif_flag"]]
    if flagged.empty:
        return _style(go.Figure(), 330)
    table = pd.crosstab(flagged["site"], flagged["activity"])
    fig = go.Figure(
        go.Heatmap(
            z=table.values,
            x=list(table.columns),
            y=list(table.index),
            colorscale=HEAT,
            xgap=2,
            ygap=2,
            text=table.values,
            texttemplate="%{text}",
            hovertemplate="%{y} / %{x}: %{z} flagged<extra></extra>",
            colorbar=dict(thickness=10, title=dict(text="flagged")),
        )
    )
    fig.update_xaxes(tickangle=-35, tickfont=dict(color=INK, size=12))
    fig.update_yaxes(autorange="reversed", tickfont=dict(color=INK))
    return _style(fig, 360)


def barrier_bars(scored):
    counts = scored[scored["sif_flag"]]["barrier"].value_counts()
    return _hbar(list(counts.index), list(counts.values), [str(v) for v in counts.values], 330)


def pattern_bars(patterns):
    return _hbar(list(patterns["pattern"]), list(patterns["reports"]), [str(v) for v in patterns["reports"]], 360)


def trend_line(scored):
    dated = scored.dropna(subset=["date"]).copy()
    if dated.empty:
        return None
    dated["month"] = dated["date"].dt.to_period("M").dt.to_timestamp()
    monthly = dated.groupby("month").agg(reports=("sif_flag", "size"), flagged=("sif_flag", "sum"))
    monthly["share"] = (monthly["flagged"] / monthly["reports"] * 100).round(1)
    fig = go.Figure(
        go.Scatter(
            x=monthly.index,
            y=monthly["share"],
            mode="lines+markers",
            line=dict(color=ORANGE, width=2),
            marker=dict(size=8, color=ORANGE, line=dict(color="#fcfcfb", width=2)),
            hovertemplate="%{x|%b %Y}: %{y}% flagged<extra></extra>",
        )
    )
    fig.update_yaxes(title="% of reports flagged", gridcolor=GRID, zeroline=False, rangemode="tozero")
    fig.update_xaxes(showgrid=False, tickformat="%b %y")
    fig.update_layout(showlegend=False)
    return _style(fig, 300)
