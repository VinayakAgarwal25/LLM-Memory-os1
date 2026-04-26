"""
Memory Lifecycle Visualization Dashboard (CLI plotting helper).
"""

import json
import os
from collections import Counter
from datetime import datetime


def load_memories(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def print_summary(data):
    short_term = data.get("short_term", [])
    long_term = data.get("long_term", [])
    archived = data.get("archived", [])
    print("Memory Lifecycle Summary")
    print("=" * 40)
    print(f"Short-term: {len(short_term)}")
    print(f"Long-term: {len(long_term)}")
    print(f"Archived: {len(archived)}")

    by_key = Counter([m.get("key", "unknown") for m in short_term + long_term])
    print("\nTop keys:")
    for key, count in by_key.most_common(10):
        print(f"- {key}: {count}")

    now = datetime.now()
    avg_age = []
    for mem in short_term + long_term:
        created = mem.get("created_at")
        if not created:
            continue
        try:
            avg_age.append((now - datetime.fromisoformat(created)).days)
        except Exception:
            pass
    if avg_age:
        print(f"\nAverage active memory age(days): {sum(avg_age)/len(avg_age):.2f}")


if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    default_path = os.path.join(project_root, "Main Application", "data", "memories.json")
    data = load_memories(default_path)
    print_summary(data)
