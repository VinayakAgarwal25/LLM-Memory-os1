"""
Interactive Memory Inspector Panel (terminal-based).
"""

import json
import os


def load_data(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_memories(memories):
    for i, m in enumerate(memories, 1):
        print(f"{i}. [{m.get('tier', 'n/a')}] {m.get('content', '')[:120]}")


def inspect(data):
    active = data.get("short_term", []) + data.get("long_term", [])
    while True:
        print("\nInspector Commands: list, show <idx>, exit")
        cmd = input("> ").strip()
        if cmd == "exit":
            break
        if cmd == "list":
            list_memories(active)
            continue
        if cmd.startswith("show "):
            try:
                idx = int(cmd.split()[1]) - 1
                if idx < 0 or idx >= len(active):
                    print("Invalid index")
                    continue
                print(json.dumps(active[idx], indent=2))
            except Exception:
                print("Usage: show <idx>")
            continue
        print("Unknown command")


if __name__ == "__main__":
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    path = os.path.join(project_root, "Main Application", "data", "memories.json")
    inspect(load_data(path))
