"""
Memory Growth Test
Tests if memory size remains stable over many turns (forgetting works)
"""

import sys
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(PROJECT_ROOT, "Main Application"))

from main import MemoryOS
import config


def test_growth():
    """
    Test memory growth over many conversation turns
    """
    print("📈 Memory Growth Test")
    print("=" * 60)
    print("Testing if memory size remains stable over time\n")
    
    # Initialize
    memory_os = MemoryOS()
    memory_os.memory_store.reset()
    
    # Simulate many turns
    turns = [
        # Important facts (should be remembered)
        "My name is Alex",
        "I study at MIT",
        "I'm majoring in computer science",
        "I want to work in AI research",
        
        # Medium importance (might be remembered)
        "I like Python programming",
        "I'm learning machine learning",
        "I prefer backend development",
        
        # Low importance (should be forgotten)
        "The weather is nice today",
        "I had coffee this morning",
        "Traffic was bad",
        "I'm feeling good",
        "Thanks for the help",
        
        # More important facts
        "I'm working on a research project",
        "I'm applying for internships",
        
        # More filler
        "How are you?",
        "What time is it?",
        "Tell me something interesting",
        "That's cool",
        "Okay thanks",
    ]
    
    # Track memory counts
    checkpoints = [5, 10, 15, 20]
    memory_counts = []
    
    print("💬 Simulating conversation turns...")
    print("-" * 60)
    
    for i, turn in enumerate(turns, 1):
        # Process turn
        memory_os.process_turn(turn)
        
        # Check at intervals
        if i in checkpoints:
            stats = memory_os.memory_store.get_stats()
            total = stats['total_active']
            memory_counts.append((i, total))
            
            print(f"Turn {i:3d}: {total:2d} active memories | \"{turn[:40]}...\"")
    
    # Force aging to show forgetting
    print("\n⏰ Forcing memory aging...")
    memory_os.aging.force_age()
    
    final_stats = memory_os.memory_store.get_stats()
    print(f"After aging: {final_stats['total_active']} active memories")
    
    # Results
    print("\n" + "=" * 60)
    print("📊 RESULTS")
    print("=" * 60)
    
    print("\nMemory growth over time:")
    for turn_num, count in memory_counts:
        print(f"  Turn {turn_num:3d}: {count:2d} memories")
    
    # Check if growth is bounded
    final_count = memory_counts[-1][1]
    
    print(f"\nFinal memory count: {final_count}")
    
    if final_count <= 15:
        print("✅ EXCELLENT: Memory growth is well controlled!")
        print("   The system is successfully forgetting unimportant information.")
    elif final_count <= 25:
        print("⚠️ GOOD: Memory growth is acceptable")
        print("   Some optimization possible for forgetting.")
    else:
        print("❌ WARNING: Memory growing too large")
        print("   Forgetting mechanism may need adjustment.")
    
    # Show what was remembered
    print("\n🧠 Memories that survived:")
    memories = memory_os.memory_store.get_all_memories()
    
    long_term = [m for m in memories if m.tier == "long_term"]
    short_term = [m for m in memories if m.tier == "short_term"]
    
    print(f"\nLong-term ({len(long_term)}):")
    for mem in long_term:
        print(f"  • {mem.content} (importance: {mem.importance:.2f})")
    
    print(f"\nShort-term ({len(short_term)}):")
    for mem in short_term[:5]:  # Show first 5
        print(f"  • {mem.content} (importance: {mem.importance:.2f})")
    
    if len(short_term) > 5:
        print(f"  ... and {len(short_term) - 5} more")
    
    print(f"\n📦 Archived: {final_stats['archived_count']} memories")


if __name__ == "__main__":
    test_growth()
