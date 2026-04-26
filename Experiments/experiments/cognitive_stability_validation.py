"""
Cognitive Stability Validation Experiments.
"""

import argparse
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(PROJECT_ROOT, "Main Application"))

from main import MemoryOS


def run(turns: int):
    memory_os = MemoryOS()
    memory_os.memory_store.reset()

    for i in range(turns):
        if i % 10 == 0:
            memory_os.process_turn("My favorite editor is VS Code")
        else:
            memory_os.process_turn(f"Random filler text number {i}")

    response = memory_os.process_turn("What is my favorite editor?")
    print("Final recall response:", response)
    stats = memory_os.memory_store.get_stats()
    print("Stability stats:", stats)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turns", type=int, default=300)
    args = parser.parse_args()
    run(args.turns)
