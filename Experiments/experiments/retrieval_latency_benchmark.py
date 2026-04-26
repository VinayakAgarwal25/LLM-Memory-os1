"""
Retrieval Latency Benchmark Framework.
"""

import argparse
import os
import statistics
import sys
import time

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(PROJECT_ROOT, "Main Application"))

from main import MemoryOS


def run_benchmark(warmup: int, iterations: int):
    memory_os = MemoryOS()
    memory_os.memory_store.reset()

    for i in range(warmup):
        memory_os.process_turn(f"My preference number {i} is option {i % 7}")

    timings = []
    for i in range(iterations):
        query = f"What are my preferences about option {i % 7}?"
        start = time.perf_counter()
        memory_os.process_turn(query)
        timings.append((time.perf_counter() - start) * 1000)

    p50 = statistics.median(timings)
    p95 = statistics.quantiles(timings, n=20)[18] if len(timings) >= 20 else max(timings)
    print(f"Latency p50: {p50:.2f} ms")
    print(f"Latency p95: {p95:.2f} ms")
    print(f"Latency mean: {statistics.mean(timings):.2f} ms")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--warmup", type=int, default=30)
    parser.add_argument("--iterations", type=int, default=100)
    args = parser.parse_args()
    run_benchmark(args.warmup, args.iterations)
