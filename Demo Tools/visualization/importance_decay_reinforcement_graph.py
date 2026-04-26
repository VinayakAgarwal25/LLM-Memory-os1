"""
Importance Decay and Reinforcement Graphing Interface.
"""

import json
import os


def load_analytics(path):
    rows = []
    if not os.path.exists(path):
        return rows
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                rows.append(json.loads(line))
            except Exception:
                pass
    return rows


def render_ascii(rows):
    print("Reinforcement Delta Trend")
    print("=" * 40)
    for row in rows[-40:]:
        delta = row.get("analytics", {}).get("reinforcement_delta", 0.0)
        bars = "#" * min(50, int(delta * 500))
        print(f"turn={row.get('turn'):>4} {bars}")


if __name__ == "__main__":
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    log_path = os.path.join(root, "Main Application", "data", "analytics.log")
    data = load_analytics(log_path)
    if not data:
        print("No analytics log found.")
    else:
        render_ascii(data)
