"""
Memory Accuracy and Relevance Evaluation Metrics.
"""

import argparse
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(PROJECT_ROOT, "Main Application"))

from main import MemoryOS


def run():
    memory_os = MemoryOS()
    memory_os.memory_store.reset()

    facts = [
        ("My name is Sarah", "sarah"),
        ("I work at OpenAI", "openai"),
        ("I live in Boston", "boston"),
        ("I like sushi", "sushi"),
        ("I am learning Rust", "rust"),
    ]

    for fact, _ in facts:
        memory_os.process_turn(fact)

    total = 0
    correct = 0
    for fact, expected in facts:
        total += 1
        response = memory_os.process_turn(f"What did I say about: {fact}?")
        if expected in response.lower():
            correct += 1

    accuracy = correct / total if total else 0
    print(f"Accuracy: {correct}/{total} ({accuracy:.2%})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.parse_args()
    run()
