"""
Latency Test
Compares response time with and without Memory OS
"""

import sys
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(PROJECT_ROOT, "Main Application"))

from main import MemoryOS
from llm.client import LLMClient
import config
import time


def test_latency():
    """
    Test response latency with and without memory system
    """
    print("⚡ Latency Test")
    print("=" * 60)
    print("Comparing response times with and without Memory OS\n")
    
    # Test queries
    test_queries = [
        "What should I learn next?",
        "Give me study advice",
        "How can I improve my skills?",
        "What career path should I take?",
        "Help me prepare for interviews"
    ]
    
    # Setup
    memory_os = MemoryOS()
    memory_os.memory_store.reset()
    llm_client = LLMClient()
    
    # Pre-load some context
    print("📝 Loading context into memory...")
    context_turns = [
        "I'm a computer science student at Stanford",
        "I'm learning Python and machine learning",
        "I want to work at a tech company",
        "I'm preparing for technical interviews",
        "I'm weak at system design"
    ]
    
    for turn in context_turns:
        memory_os.process_turn(turn)
    
    print(f"✓ Loaded {len(memory_os.memory_store.get_all_memories())} memories\n")
    
    # Test 1: WITH Memory OS
    print("🧠 Test 1: WITH Memory OS")
    print("-" * 60)
    
    with_memory_times = []
    
    for query in test_queries:
        start_time = time.time()
        response = memory_os.process_turn(query)
        end_time = time.time()
        
        elapsed = end_time - start_time
        with_memory_times.append(elapsed)
        
        print(f"  Query: {query}")
        print(f"  Time: {elapsed:.2f}s")
        print()
    
    avg_with_memory = sum(with_memory_times) / len(with_memory_times)
    
    # Test 2: WITHOUT Memory OS (direct LLM)
    print("\n🤖 Test 2: WITHOUT Memory OS (Direct LLM)")
    print("-" * 60)
    
    without_memory_times = []
    
    # Build a huge context string (simulating full history)
    full_context = "\n".join(context_turns)
    
    for query in test_queries:
        # Simulate loading full chat history
        full_message = f"Previous conversation:\n{full_context}\n\nCurrent question: {query}"
        
        start_time = time.time()
        response = llm_client.chat(
            system_prompt=config.SYSTEM_PROMPT,
            user_message=full_message
        )
        end_time = time.time()
        
        elapsed = end_time - start_time
        without_memory_times.append(elapsed)
        
        print(f"  Query: {query}")
        print(f"  Time: {elapsed:.2f}s")
        print()
    
    avg_without_memory = sum(without_memory_times) / len(without_memory_times)
    
    # Results
    print("\n" + "=" * 60)
    print("📊 RESULTS")
    print("=" * 60)
    
    print(f"Average time WITH Memory OS:    {avg_with_memory:.2f}s")
    print(f"Average time WITHOUT Memory OS: {avg_without_memory:.2f}s")
    
    if avg_with_memory < avg_without_memory:
        speedup = avg_without_memory / avg_with_memory
        print(f"\n⚡ Speedup: {speedup:.2f}x FASTER with Memory OS!")
    else:
        slowdown = avg_with_memory / avg_without_memory
        print(f"\n⚠️ Warning: {slowdown:.2f}x SLOWER with Memory OS")
    
    print("\nNote: Results may vary based on:")
    print("  - API latency")
    print("  - Network conditions")
    print("  - Number of memories stored")


if __name__ == "__main__":
    test_latency()
