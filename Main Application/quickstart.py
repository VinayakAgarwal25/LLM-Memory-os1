#!/usr/bin/env python3
"""
Quick Start Script for Memory OS.
"""

import os
import subprocess
import sys

import requests

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

REQ_FILE = os.path.join(PROJECT_ROOT, "Configuration", "requirements.txt")
MAIN_APP = os.path.join(SCRIPT_DIR, "main.py")
SIMULATOR = os.path.join(PROJECT_ROOT, "Demo Tools", "simulator", "conversation_simulator.py")

EXPERIMENTS_DIR = os.path.join(PROJECT_ROOT, "Experiments", "experiments")
TEST_SCRIPTS = [
    "accuracy_test.py",
    "latency_test.py",
    "growth_test.py",
    "retrieval_latency_benchmark.py",
    "scalability_stress_test.py",
    "latency_vs_memory_count.py",
    "memory_accuracy_metrics.py",
    "cognitive_stability_validation.py",
]


def print_header(text):
    print("\n" + "=" * 60)
    print(text)
    print("=" * 60 + "\n")


def check_python():
    version = sys.version_info
    if version.major == 3 and version.minor >= 8:
        print(f"Python {version.major}.{version.minor}.{version.micro} OK")
        return True
    print("Python 3.8+ required")
    return False


def install_dependencies():
    if not os.path.exists(REQ_FILE):
        print(f"Missing requirements file: {REQ_FILE}")
        return False
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "-r", REQ_FILE])
        return True
    except subprocess.CalledProcessError:
        return False


def check_ollama():
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code != 200:
            return False
        models = response.json().get("models", [])
        return bool(models)
    except Exception:
        return False


def run_experiments():
    print("\nExperiment Menu")
    print("1. Legacy tests (accuracy/latency/growth)")
    print("2. Full benchmark suite")
    print("3. Back")
    choice = input("Choice: ").strip()

    if choice == "1":
        for filename in TEST_SCRIPTS[:3]:
            subprocess.run([sys.executable, os.path.join(EXPERIMENTS_DIR, filename)])
    elif choice == "2":
        for filename in TEST_SCRIPTS[3:]:
            command = [sys.executable, os.path.join(EXPERIMENTS_DIR, filename)]
            if filename == "scalability_stress_test.py":
                command.extend(["--turns", "1200"])
            subprocess.run(command)


def main():
    print_header("Memory OS Quick Start")

    if not check_python():
        return

    if not install_dependencies():
        print("Dependency installation failed.")
        return

    if not check_ollama():
        print("Start Ollama and ensure at least one model is installed.")
        return

    print("1. Start interactive chat")
    print("2. Run experiments")
    print("3. Run simulator demo")
    print("4. Exit")
    choice = input("Choice: ").strip()

    if choice == "1":
        subprocess.run([sys.executable, MAIN_APP])
    elif choice == "2":
        run_experiments()
    elif choice == "3":
        subprocess.run([sys.executable, SIMULATOR, "--demo"])


if __name__ == "__main__":
    main()
