"""
Memory Scalability Stress Test (1000+ turns).
"""

import argparse
import os
import random
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(PROJECT_ROOT, "Main Application"))

from main import MemoryOS


def run(turns: int):
    memory_os = MemoryOS()
    memory_os.memory_store.reset()

    templates = [
        "My name is User{n}",
        "I like topic{n}",
        "I work at company{n}",
        "I am learning skill{n}",
        "I prefer style{n}",
        "What should I do next for goal{n}?",
    ]

    for i in range(1, turns + 1):
        msg = random.choice(templates).format(n=i % 100)
        memory_os.process_turn(msg)
        if i % 100 == 0:
            stats = memory_os.memory_store.get_stats()
            print(f"Turn {i}: active={stats['total_active']} archived={stats['archived_count']}")

    final_stats = memory_os.memory_store.get_stats()
    print("Final Stats:", final_stats)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--turns", type=int, default=1200)
    args = parser.parse_args()
    run(args.turns)
