"""
Conversation Simulator
Generates realistic multi-turn conversations for testing
"""

import sys
import os
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.append(os.path.join(PROJECT_ROOT, "Main Application"))

from main import MemoryOS
import random


class ConversationSimulator:
    """
    Simulates realistic conversations for testing
    """
    
    def __init__(self):
        self.memory_os = MemoryOS()
        
        # Conversation templates
        self.templates = {
            "introduction": [
                "Hi, my name is {name}",
                "I'm {name}, nice to meet you",
                "Hello, I'm {name}"
            ],
            "education": [
                "I study at {university}",
                "I'm a student at {university}",
                "I go to {university}",
                "I'm studying {major} at {university}"
            ],
            "goals": [
                "I want to work at {company}",
                "My goal is to join {company}",
                "I'm aiming for a job at {company}"
            ],
            "skills": [
                "I'm learning {skill}",
                "I know {skill}",
                "I'm good at {skill}"
            ],
            "preferences": [
                "I prefer {preference}",
                "I like {preference}",
                "I enjoy {preference}"
            ],
            "questions": [
                "What should I learn next?",
                "Can you help me with {topic}?",
                "What do you think about {topic}?",
                "How can I improve my {skill}?",
                "Give me advice on {topic}"
            ],
            "filler": [
                "Thanks",
                "That's helpful",
                "Got it",
                "Okay",
                "Cool",
                "Interesting",
                "I see"
            ]
        }
        
        # Data pools
        self.data = {
            "names": ["Alex", "Sarah", "John", "Emma", "Michael", "Lisa"],
            "universities": ["MIT", "Stanford", "Berkeley", "Harvard", "CMU"],
            "companies": ["Google", "Meta", "Microsoft", "Amazon", "Apple"],
            "majors": ["Computer Science", "Engineering", "Data Science", "AI"],
            "skills": ["Python", "machine learning", "algorithms", "web development"],
            "preferences": ["backend over frontend", "Linux over Windows", "tabs over spaces"],
            "topics": ["career", "interviews", "projects", "skills", "learning"]
        }
    
    def generate_turn(self, turn_type: str) -> str:
        """
        Generate a single conversation turn
        
        Args:
            turn_type: Type of turn to generate
        
        Returns:
            Generated text
        """
        if turn_type not in self.templates:
            return "Hello"
        
        template = random.choice(self.templates[turn_type])
        
        # Fill in placeholders
        result = template
        for key, values in self.data.items():
            placeholder = f"{{{key}}}"
            if placeholder in result:
                result = result.replace(placeholder, random.choice(values))
        
        # Handle any remaining placeholders
        for key in ["topic", "skill", "preference"]:
            placeholder = f"{{{key}}}"
            if placeholder in result:
                result = result.replace(placeholder, "programming")
        
        return result
    
    def simulate_conversation(self, num_turns: int = 50, reset: bool = True):
        """
        Simulate a complete conversation
        
        Args:
            num_turns: Number of turns to simulate
            reset: Whether to reset memory before starting
        """
        if reset:
            self.memory_os.memory_store.reset()
        
        print(f"🎭 Simulating {num_turns}-turn conversation...")
        print("=" * 60)
        
        # Conversation structure
        structure = [
            ("introduction", 1),
            ("education", 1),
            ("skills", 2),
            ("goals", 1),
            ("questions", 5),
            ("filler", 3),
            ("questions", 5),
            ("filler", 2),
        ]
        
        turns = []
        for turn_type, count in structure:
            for _ in range(count):
                turns.append(turn_type)
        
        # Fill remaining with questions and filler
        while len(turns) < num_turns:
            if random.random() < 0.7:
                turns.append("questions")
            else:
                turns.append("filler")
        
        # Shuffle a bit (but keep intro at start)
        intro = turns[:2]
        rest = turns[2:]
        random.shuffle(rest)
        turns = intro + rest
        
        # Run simulation
        for i, turn_type in enumerate(turns[:num_turns], 1):
            user_message = self.generate_turn(turn_type)
            
            print(f"\nTurn {i}/{num_turns}")
            print(f"User: {user_message}")
            
            response = self.memory_os.process_turn(user_message)
            print(f"Bot: {response[:100]}...")
            
            # Show stats every 10 turns
            if i % 10 == 0:
                stats = self.memory_os.memory_store.get_stats()
                print(f"\n📊 Stats: {stats['total_active']} active memories")
        
        # Final stats
        print("\n" + "=" * 60)
        print("📊 FINAL STATISTICS")
        print("=" * 60)
        
        stats = self.memory_os.memory_store.get_stats()
        print(f"Total turns: {num_turns}")
        print(f"Short-term memories: {stats['short_term_count']}")
        print(f"Long-term memories: {stats['long_term_count']}")
        print(f"Archived memories: {stats['archived_count']}")
        print(f"Total active: {stats['total_active']}")
        
        # Show some memories
        print("\n🧠 Sample Memories:")
        memories = self.memory_os.memory_store.get_all_memories()[:5]
        for i, mem in enumerate(memories, 1):
            print(f"  {i}. {mem.content} (importance: {mem.importance:.2f})")


def main():
    """
    Main demo function
    """
    import argparse
    
    parser = argparse.ArgumentParser(description="Simulate conversations")
    parser.add_argument("--turns", type=int, default=50, help="Number of turns")
    parser.add_argument("--demo", action="store_true", help="Run demo mode")
    
    args = parser.parse_args()
    
    simulator = ConversationSimulator()
    
    if args.demo:
        print("🎬 DEMO MODE: Running impressive demonstration")
        print()
        simulator.simulate_conversation(num_turns=100, reset=True)
    else:
        simulator.simulate_conversation(num_turns=args.turns, reset=True)


if __name__ == "__main__":
    main()
