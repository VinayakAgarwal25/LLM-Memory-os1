"""
Memory Accuracy Test
Tests if the system correctly remembers and recalls facts
"""

import sys
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(PROJECT_ROOT, "Main Application"))

from main import MemoryOS
import config

# Temporarily disable verbose logging for cleaner output
original_debug = config.DEBUG
original_verbose = config.VERBOSE
config.DEBUG = False
config.VERBOSE = False


def test_accuracy():
    """
    Test memory accuracy across multiple turns
    """
    print("🧪 Memory Accuracy Test")
    print("=" * 60)
    print("This test checks if the system correctly remembers facts\n")
    
    # Initialize system
    memory_os = MemoryOS()
    memory_os.memory_store.reset()  # Start fresh
    
    # Test data: facts to remember
    test_facts = [
        ("My name is Sarah", "name"),
        ("I study computer science at Stanford", "education"),
        ("I'm learning Python programming", "skill"),
        ("I want to work at Google", "goal"),
        ("I'm weak at algorithms", "weakness"),
    ]
    
    # Phase 1: Store facts
    print("📝 Phase 1: Storing facts...")
    for fact, _ in test_facts:
        response = memory_os.process_turn(fact)
        print(f"  ✓ Stored: {fact}")
    
    print(f"\n💾 Total memories stored: {len(memory_os.memory_store.get_all_memories())}")
    
    # Phase 2: Filler turns (simulate conversation)
    print("\n💬 Phase 2: Having irrelevant conversations...")
    filler_turns = [
        "How's the weather?",
        "What's 2+2?",
        "Tell me a joke",
        "What's AI?",
        "Thanks for the help"
    ]
    
    for turn in filler_turns:
        memory_os.process_turn(turn)
        print(f"  ✓ Turn: {turn}")
    
    # Phase 3: Test recall
    print("\n🔍 Phase 3: Testing recall...")
    queries = [
        ("What's my name?", "name", "Sarah"),
        ("Where do I study?", "education", "Stanford"),
        ("What programming language am I learning?", "skill", "Python"),
        ("What company do I want to work at?", "goal", "Google"),
        ("What am I weak at?", "weakness", "algorithms"),
    ]
    
    correct = 0
    total = len(queries)
    
    for query, category, expected_keyword in queries:
        response = memory_os.process_turn(query)
        
        # Check if expected keyword is in response
        if expected_keyword.lower() in response.lower():
            print(f"  ✅ PASS: {query}")
            print(f"     Response: {response[:80]}...")
            correct += 1
        else:
            print(f"  ❌ FAIL: {query}")
            print(f"     Expected '{expected_keyword}' in response")
            print(f"     Got: {response[:80]}...")
    
    # Results
    print("\n" + "=" * 60)
    print("📊 RESULTS")
    print("=" * 60)
    accuracy = (correct / total) * 100
    print(f"Accuracy: {correct}/{total} ({accuracy:.1f}%)")
    
    if accuracy >= 80:
        print("✅ EXCELLENT: Memory system is working well!")
    elif accuracy >= 60:
        print("⚠️ GOOD: Memory system is decent, but could be better")
    else:
        print("❌ POOR: Memory system needs improvement")
    
    # Show memory stats
    stats = memory_os.memory_store.get_stats()
    print(f"\nMemory Statistics:")
    print(f"  Short-term: {stats['short_term_count']}")
    print(f"  Long-term: {stats['long_term_count']}")
    print(f"  Total active: {stats['total_active']}")


if __name__ == "__main__":
    # Run test
    test_accuracy()
    
    # Restore config
    config.DEBUG = original_debug
    config.VERBOSE = original_verbose
