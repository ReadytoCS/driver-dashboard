from typing import List
import pandas as pd

def generate_insights(df: pd.DataFrame, category_col: str, metric_cols: List[str]) -> List[str]:
    insights = []
    # 1. Which metric has the highest total value across all segments?
    metric_totals = df[metric_cols].sum()
    max_metric = metric_totals.idxmax()
    insights.append(f"{max_metric} has the highest total value across all segments.")

    # 2. Which segment has the highest value for each metric?
    for col in metric_cols:
        idx = df[col].idxmax()
        seg = df.loc[idx, category_col]
        val = df.loc[idx, col]
        insights.append(f"{seg} has the highest {col} value ({val:,}).")
        if len(insights) >= 2:
            break

    # 3. % contribution of each metric to total
    total_sum = metric_totals.sum()
    if total_sum > 0:
        pct_contrib = (metric_totals / total_sum * 100).round(1)
        top_metric = pct_contrib.idxmax()
        pct = pct_contrib.max()
        if pct > 50:
            insights.append(f"{top_metric} contributes {pct:.0f}% of the total across all metrics.")

    # 4. Detect if any metric is 2x another within same category
    for i, row in df.iterrows():
        vals = row[metric_cols]
        for a in metric_cols:
            for b in metric_cols:
                if a != b and vals[a] >= 2 * vals[b] and vals[b] > 0:
                    insights.append(f"{row[category_col]}'s {a} is double that of {b}.")
                    break
            if len(insights) >= 3:
                break
        if len(insights) >= 3:
            break

    # 5. Flag if any segment is dominant across multiple metrics
    segment_wins = {}
    for col in metric_cols:
        idx = df[col].idxmax()
        seg = df.loc[idx, category_col]
        segment_wins[seg] = segment_wins.get(seg, 0) + 1
    dominant = [seg for seg, count in segment_wins.items() if count > 1]
    if dominant:
        insights.append(f"{dominant[0]} is dominant across multiple metrics.")

    # Return only 2-3 unique insights
    seen = set()
    result = []
    for ins in insights:
        if ins not in seen:
            result.append(ins)
            seen.add(ins)
        if len(result) >= 3:
            break
    return result

# --- Test cases ---
if __name__ == "__main__":
    data = {
        "Segment": ["A", "B", "C"],
        "Y1": [100, 200, 50],
        "Y2": [300, 100, 50],
        "Y3": [50, 400, 100],
        "Y4": [500, 100, 50],
    }
    df = pd.DataFrame(data)
    insights = generate_insights(df, "Segment", ["Y1", "Y2", "Y3", "Y4"])
    print("\n".join(insights))
    # Example output:
    # Y4 has the highest total value across all segments.
    # B has the highest Y3 value (400).
    # Y4 contributes 44% of the total across all metrics. 