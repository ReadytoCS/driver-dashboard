import pandas as pd
import plotly.graph_objects as go
import numpy as np

# McKinsey-style business color palette for charts
MCKINSEY_COLORS = [
    "#002F6C",  # Steel Blue
    "#5C6770",  # Slate Gray
    "#A6192E",  # Burgundy
    "#007C91",  # Teal
    "#6CACE4",  # Light Blue
    "#B7BF10",  # Olive Green
    "#F2A900",  # Gold
    "#58595B",  # Charcoal
]

MCKINSEY_COLOR_DICT = {
    "Steel Blue": "#002F6C",
    "Slate Gray": "#5C6770",
    "Burgundy": "#A6192E",
    "Teal": "#007C91",
    "Light Blue": "#6CACE4",
    "Olive Green": "#B7BF10",
    "Gold": "#F2A900",
    "Charcoal": "#58595B",
}

# Example usage in Plotly:
# import plotly.express as px
# fig = px.bar(df, x=..., y=..., color=..., color_discrete_sequence=MCKINSEY_COLORS)

def detect_multi_metric(df):
    """Detects if the dataframe has 1 categorical and >=2 numeric columns."""
    df = df.copy()
    # Heuristic: treat first column as category if it's object or 'Unnamed'
    columns = list(df.columns)
    first_col = columns[0]
    if (
        df[first_col].dtype == object
        or first_col.lower().startswith("unnamed")
        or first_col.lower() in ["segment", "category", "index", "id"]
    ):
        cat_col = first_col
    else:
        # fallback: first object column
        obj_cols = [c for c in columns if df[c].dtype == object]
        cat_col = obj_cols[0] if obj_cols else columns[0]
    num_cols = [c for c in columns if c != cat_col and pd.api.types.is_numeric_dtype(df[c])]
    if len(num_cols) >= 2:
        return cat_col, num_cols
    return None, None

def mckinsey_layout(title, x_title, y_title):
    """Returns a Plotly layout dict with McKinsey-style settings."""
    return dict(
        title=dict(text=title, font=dict(family="Inter, Arial, sans-serif", size=22, color="#222"), x=0.01, xanchor="left"),
        font=dict(family="Inter, Arial, sans-serif", size=16, color="#222"),
        plot_bgcolor="white",
        paper_bgcolor="white",
        xaxis=dict(
            title=x_title,
            showgrid=False,
            linecolor="#222",
            linewidth=1,
            ticks="outside",
            ticklen=6,
            tickcolor="#222",
            mirror=True,
            tickfont=dict(size=14),
        ),
        yaxis=dict(
            title=y_title,
            showgrid=False,
            linecolor="#222",
            linewidth=1,
            ticks="outside",
            ticklen=6,
            tickcolor="#222",
            mirror=True,
            tickfont=dict(size=14),
        ),
        margin=dict(l=60, r=30, t=60, b=60),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=15),
        ),
        height=600,
        width=1100,
    )

def grouped_bar_chart(df, cat_col, num_cols):
    fig = go.Figure()
    for i, col in enumerate(num_cols):
        fig.add_trace(
            go.Bar(
                x=df[cat_col],
                y=df[col],
                name=col,
                marker_color=MCKINSEY_COLORS[i % len(MCKINSEY_COLORS)],
            )
        )
    fig.update_layout(
        **mckinsey_layout(
            f"Grouped Bar: {', '.join(num_cols)} by {cat_col}",
            cat_col,
            "Value",
        ),
        barmode="group",
    )
    return fig

def stacked_bar_chart(df, cat_col, num_cols):
    fig = go.Figure()
    for i, col in enumerate(num_cols):
        fig.add_trace(
            go.Bar(
                x=df[cat_col],
                y=df[col],
                name=col,
                marker_color=MCKINSEY_COLORS[i % len(MCKINSEY_COLORS)],
            )
        )
    fig.update_layout(
        **mckinsey_layout(
            f"Stacked Bar: {', '.join(num_cols)} by {cat_col}",
            cat_col,
            "Value",
        ),
        barmode="stack",
    )
    return fig

def radar_chart(df, cat_col, num_cols):
    fig = go.Figure()
    for i, col in enumerate(num_cols):
        fig.add_trace(
            go.Scatterpolar(
                r=df[col],
                theta=df[cat_col],
                fill="toself",
                name=col,
                line_color=MCKINSEY_COLORS[i % len(MCKINSEY_COLORS)],
            )
        )
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                showgrid=False,
                showline=True,
                linewidth=1,
                linecolor="#222",
                tickfont=dict(size=13),
            ),
            angularaxis=dict(
                tickfont=dict(size=13),
                rotation=90,
                direction="clockwise",
            ),
        ),
        showlegend=True,
        **mckinsey_layout(
            f"Radar: {', '.join(num_cols)} by {cat_col}",
            "",
            "",
        ),
    )
    return fig

def generate_insights(df, cat_col, num_cols):
    """Returns 1-3 simple bullet points as insights."""
    insights = []
    # 1. Which segment has the highest value for each metric?
    for col in num_cols:
        idx = df[col].idxmax()
        seg = df.loc[idx, cat_col]
        val = df.loc[idx, col]
        insights.append(f"• {seg} has the highest {col} value ({val:,}).")
        if len(insights) >= 2:
            break
    # 2. Which metric contributes most to the total in any segment?
    if len(num_cols) > 1:
        for i, row in df.iterrows():
            total = row[num_cols].sum()
            if total == 0:
                continue
            max_col = max(num_cols, key=lambda c: row[c])
            pct = 100 * row[max_col] / total
            if pct > 60:
                insights.append(f"• {max_col} contributes over {pct:.0f}% of total in {row[cat_col]}.")
                break
    return insights[:3] 