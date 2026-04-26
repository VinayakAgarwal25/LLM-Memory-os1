"""
Latency vs Memory Count Performance Analysis.
"""

import argparse
import os
import statistics
import sys
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(PROJECT_ROOT, "Main Application"))

from main import MemoryOS


def run(points):
    memory_os = MemoryOS()
    memory_os.memory_store.reset()

    for point in points:
        while memory_os.memory_store.get_stats()["total_active"] < point:
            i = memory_os.memory_store.get_stats()["total_active"]
            memory_os.process_turn(f"My key fact {i} is value {i}")

        samples = []
        for _ in range(8):
            start = time.perf_counter()
            memory_os.process_turn("What do you remember about me?")
            samples.append((time.perf_counter() - start) * 1000)

        print(f"memories={point}, mean_ms={statistics.mean(samples):.2f}, p95_ms={max(samples):.2f}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--points", default="25,50,100,200,400")
    args = parser.parse_args()
    points = [int(x.strip()) for x in args.points.split(",") if x.strip()]
    run(points)
