"""
ChromaDB Seeding Script
Populates ChromaDB collections with fake data for development/testing
"""
import chromadb
import time
import sys
import os
from chromadb.config import Settings
from chromadb.utils import embedding_functions

def wait_for_chromadb(host="chromadb", port=8000, max_retries=30):
    """Wait for ChromaDB to be ready"""
    print(f"Waiting for ChromaDB at {host}:{port}...")
    
    for i in range(max_retries):
        try:
            client = chromadb.HttpClient(
                host=host,
                port=port,
                settings=Settings(anonymized_telemetry=False)
            )
            client.heartbeat()
            print("✓ ChromaDB is ready!")
            return client
        except Exception as e:
            if i < max_retries - 1:
                print(f"Waiting for ChromaDB... ({i+1}/{max_retries})")
                time.sleep(2)
            else:
                print(f"Failed to connect to ChromaDB after {max_retries} attempts")
                raise e
    
    return None

def get_ollama_embedding_function():
    """Get Ollama embedding function for consistency with backend"""
    ollama_host = os.getenv("OLLAMA_HOST", "http://ollama:11434")
    
    # Wait for Ollama to be ready
    print(f"\nWaiting for Ollama at {ollama_host}...")
    import requests
    
    for i in range(60):  # Increased to 60 retries (2 minutes)
        try:
            # Try to access the Ollama API
            response = requests.get(f"{ollama_host}/api/tags", timeout=5)
            if response.status_code == 200:
                print("✓ Ollama is ready!")
                
                # Verify nomic-embed-text model is available
                models = response.json().get('models', [])
                model_names = [m.get('name', '') for m in models]
                
                if any('nomic-embed-text' in name for name in model_names):
                    print("✓ Found nomic-embed-text model in Ollama")
                else:
                    print(f"⚠ Warning: nomic-embed-text not found in Ollama models: {model_names}")
                    print("  Attempting to use it anyway...")
                
                break
        except Exception as e:
            if i < 59:
                print(f"Waiting for Ollama... ({i+1}/60) - {type(e).__name__}")
                time.sleep(2)
            else:
                print(f"⚠ Warning: Ollama not ready after 120 seconds: {e}")
                print("  Using default embeddings instead")
                return None
    
    # Create Ollama embedding function
    try:
        ollama_ef = embedding_functions.OllamaEmbeddingFunction(
            url=f"{ollama_host}/api/embeddings",
            model_name="nomic-embed-text"
        )
        print("✓ Using Ollama embeddings (nomic-embed-text)")
        return ollama_ef
    except Exception as e:
        print(f"⚠ Warning: Failed to create Ollama embedding function: {e}")
        print("  Using default embeddings instead")
        return None

def create_collections(client, embedding_function=None):
    """Create required ChromaDB collections with specified embedding function"""
    collections = [
        'AMC8_math',
        'student_persona', 
        'math_related',
        'AMC8_problems',
        'conversation_history'
    ]
    
    created_collections = {}
    
    for collection_name in collections:
        try:
            # Try to get existing collection
            collection = client.get_collection(
                name=collection_name,
                embedding_function=embedding_function
            )
            print(f"✓ Collection '{collection_name}' already exists")
            created_collections[collection_name] = collection
        except Exception:
            # Create new collection if it doesn't exist
            collection = client.create_collection(
                name=collection_name,
                embedding_function=embedding_function
            )
            print(f"✓ Created collection '{collection_name}'")
            created_collections[collection_name] = collection
    
    return created_collections

def seed_amc8_math(collection):
    """Seed AMC8_math collection with sample math problems and solutions"""
    
    # Check if already seeded
    if collection.count() > 0:
        print(f"  Collection already has {collection.count()} items, skipping seed")
        return
    
    documents = [
        # Arithmetic problems
        "What is 25 + 37? Solution: To add 25 + 37, we can break it down: 25 + 30 = 55, then 55 + 7 = 62. Answer: 62",
        "Calculate 144 ÷ 12. Solution: 144 ÷ 12 = 12 because 12 × 12 = 144. Answer: 12",
        "What is 8 × 7? Solution: 8 × 7 = 56. We can verify by adding 8 seven times. Answer: 56",
        "Simplify 3/4 + 1/4. Solution: Since denominators are the same, add numerators: 3 + 1 = 4, so 4/4 = 1. Answer: 1",
        "What is 100 - 43? Solution: 100 - 43 = 57. We can check: 57 + 43 = 100. Answer: 57",
        
        # Fractions
        "Reduce 12/16 to lowest terms. Solution: Find GCD(12,16) = 4. Divide both by 4: 12÷4 = 3, 16÷4 = 4. Answer: 3/4",
        "What is 2/3 × 3/4? Solution: Multiply numerators: 2×3=6. Multiply denominators: 3×4=12. Simplify 6/12 = 1/2. Answer: 1/2",
        "Convert 0.75 to a fraction. Solution: 0.75 = 75/100. Simplify by dividing by 25: 75÷25=3, 100÷25=4. Answer: 3/4",
        
        # Geometry basics
        "Find the area of a rectangle with length 8 and width 5. Solution: Area = length × width = 8 × 5 = 40. Answer: 40 square units",
        "What is the perimeter of a square with side length 6? Solution: Perimeter = 4 × side = 4 × 6 = 24. Answer: 24",
        "A triangle has angles 60°, 70°, and x°. Find x. Solution: Sum of angles = 180°. So 60 + 70 + x = 180, 130 + x = 180, x = 50°. Answer: 50°",
        
        # Order of operations
        "Calculate 3 + 4 × 2. Solution: PEMDAS - multiply first: 4×2=8, then add: 3+8=11. Answer: 11",
        "Evaluate (5 + 3) × 2. Solution: Parentheses first: 5+3=8, then multiply: 8×2=16. Answer: 16",
        "What is 20 - 3 × 4? Solution: Multiply first: 3×4=12, then subtract: 20-12=8. Answer: 8",
        
        # Percentages
        "What is 25% of 80? Solution: 25% = 1/4, so 80÷4 = 20. Or 0.25×80 = 20. Answer: 20",
        "If 20 is 40% of a number, what is the number? Solution: Let x be the number. 0.40x = 20, so x = 20÷0.40 = 50. Answer: 50",
    ]
    
    metadatas = [
        {"topic": "arithmetic", "difficulty": "easy", "type": "addition"},
        {"topic": "arithmetic", "difficulty": "easy", "type": "division"},
        {"topic": "arithmetic", "difficulty": "easy", "type": "multiplication"},
        {"topic": "fractions", "difficulty": "easy", "type": "addition"},
        {"topic": "arithmetic", "difficulty": "easy", "type": "subtraction"},
        {"topic": "fractions", "difficulty": "medium", "type": "simplification"},
        {"topic": "fractions", "difficulty": "medium", "type": "multiplication"},
        {"topic": "fractions", "difficulty": "medium", "type": "conversion"},
        {"topic": "geometry", "difficulty": "easy", "type": "area"},
        {"topic": "geometry", "difficulty": "easy", "type": "perimeter"},
        {"topic": "geometry", "difficulty": "medium", "type": "angles"},
        {"topic": "order of operations", "difficulty": "medium", "type": "pemdas"},
        {"topic": "order of operations", "difficulty": "medium", "type": "pemdas"},
        {"topic": "order of operations", "difficulty": "medium", "type": "pemdas"},
        {"topic": "percentages", "difficulty": "medium", "type": "calculation"},
        {"topic": "percentages", "difficulty": "medium", "type": "reverse"},
    ]
    
    ids = [f"math_{i}" for i in range(len(documents))]
    
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    
    print(f"  ✓ Seeded {len(documents)} math problems")

def seed_student_persona(collection):
    """Seed student_persona collection with sample student interactions"""
    
    if collection.count() > 0:
        print(f"  Collection already has {collection.count()} items, skipping seed")
        return
    
    documents = [
        "Student frequently asks for hints before attempting problems independently",
        "Student shows strong understanding of fractions but struggles with word problems",
        "Student prefers visual explanations and diagrams over text-based instructions",
        "Student tends to rush through problems and makes careless arithmetic errors",
        "Student demonstrates excellent problem-solving skills when given sufficient time",
        "Student asks clarifying questions and shows good engagement during lessons",
        "Student has difficulty with multi-step problems but excels at single-step calculations",
        "Student shows persistence and tries multiple approaches when stuck",
    ]
    
    metadatas = [
        {"student_id": "1", "trait": "help_seeking", "timestamp": "2025-10-01"},
        {"student_id": "1", "trait": "strength_weakness", "timestamp": "2025-10-01"},
        {"student_id": "1", "trait": "learning_style", "timestamp": "2025-10-02"},
        {"student_id": "1", "trait": "common_error", "timestamp": "2025-10-02"},
        {"student_id": "1", "trait": "strength", "timestamp": "2025-10-03"},
        {"student_id": "1", "trait": "engagement", "timestamp": "2025-10-03"},
        {"student_id": "1", "trait": "weakness", "timestamp": "2025-10-04"},
        {"student_id": "1", "trait": "persistence", "timestamp": "2025-10-04"},
    ]
    
    ids = [f"persona_{i}" for i in range(len(documents))]
    
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    
    print(f"  ✓ Seeded {len(documents)} student persona entries")

def seed_math_related(collection):
    """Seed math_related collection with general math concepts"""
    
    if collection.count() > 0:
        print(f"  Collection already has {collection.count()} items, skipping seed")
        return
    
    documents = [
        "PEMDAS stands for Parentheses, Exponents, Multiplication/Division, Addition/Subtraction - the order of operations",
        "A prime number is a whole number greater than 1 that has exactly two factors: 1 and itself",
        "The Pythagorean theorem states that in a right triangle, a² + b² = c² where c is the hypotenuse",
        "To find the area of a triangle, use the formula: Area = (base × height) / 2",
        "When adding fractions, you must have a common denominator before adding the numerators",
        "The distributive property: a(b + c) = ab + ac",
        "A factor is a number that divides evenly into another number",
        "The GCD (Greatest Common Divisor) is the largest number that divides two numbers evenly",
        "Complementary angles add up to 90 degrees, supplementary angles add up to 180 degrees",
        "The mean (average) is found by adding all numbers and dividing by the count",
    ]
    
    metadatas = [
        {"concept": "order of operations", "category": "algebra"},
        {"concept": "prime numbers", "category": "number theory"},
        {"concept": "pythagorean theorem", "category": "geometry"},
        {"concept": "triangle area", "category": "geometry"},
        {"concept": "fractions", "category": "arithmetic"},
        {"concept": "distributive property", "category": "algebra"},
        {"concept": "factors", "category": "number theory"},
        {"concept": "gcd", "category": "number theory"},
        {"concept": "angles", "category": "geometry"},
        {"concept": "mean", "category": "statistics"},
    ]
    
    ids = [f"concept_{i}" for i in range(len(documents))]
    
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    
    print(f"  ✓ Seeded {len(documents)} math concept entries")

def seed_amc8_problems(collection):
    """Seed AMC8_problems collection with sample competition problems"""
    
    if collection.count() > 0:
        print(f"  Collection already has {collection.count()} items, skipping seed")
        return
    
    documents = [
        "Problem: Mary has 3 times as many apples as Tom. Together they have 24 apples. How many apples does Mary have? Solution: Let x = Tom's apples. Then 3x = Mary's apples. x + 3x = 24, 4x = 24, x = 6. Mary has 3(6) = 18 apples. Answer: 18",
        "Problem: A rectangle has a perimeter of 30 cm. If the length is 9 cm, what is the width? Solution: Perimeter = 2(length + width). 30 = 2(9 + w), 30 = 18 + 2w, 12 = 2w, w = 6 cm. Answer: 6 cm",
        "Problem: What is the next number in the sequence: 2, 5, 11, 23, ...? Solution: Pattern: multiply by 2 and add 1. 2×2+1=5, 5×2+1=11, 11×2+1=23, 23×2+1=47. Answer: 47",
        "Problem: A square has the same perimeter as a rectangle with length 8 and width 4. What is the side length of the square? Solution: Rectangle perimeter = 2(8+4) = 24. Square perimeter = 4s = 24, s = 6. Answer: 6",
        "Problem: If 5 pencils cost $2.50, how much do 8 pencils cost? Solution: Cost per pencil = $2.50 ÷ 5 = $0.50. 8 pencils = 8 × $0.50 = $4.00. Answer: $4.00",
    ]
    
    metadatas = [
        {"difficulty": "medium", "topic": "algebra", "year": "2024"},
        {"difficulty": "easy", "topic": "geometry", "year": "2024"},
        {"difficulty": "medium", "topic": "patterns", "year": "2023"},
        {"difficulty": "medium", "topic": "geometry", "year": "2023"},
        {"difficulty": "easy", "topic": "proportions", "year": "2024"},
    ]
    
    ids = [f"amc8_{i}" for i in range(len(documents))]
    
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    
    print(f"  ✓ Seeded {len(documents)} AMC8 problems")

def seed_conversation_history(collection):
    """Seed conversation_history collection with sample conversations"""
    
    if collection.count() > 0:
        print(f"  Collection already has {collection.count()} items, skipping seed")
        return
    
    # This collection is typically populated during runtime, so we'll just add a few examples
    documents = [
        "Student: Can you help me with fractions?",
        "Teacher: Of course! Let's start with adding fractions. Do you know how to find a common denominator?",
        "Student: Not really, can you explain?",
        "Teacher: Sure! When adding fractions like 1/3 + 1/4, we need to find a common denominator. What number do both 3 and 4 divide into evenly?",
        "Student: Is it 12?",
        "Teacher: Excellent! Yes, 12 is the least common multiple of 3 and 4. Now, can you convert 1/3 to twelfths?",
    ]
    
    metadatas = [
        {"student_id": "1", "role": "student", "timestamp": "2025-10-04T10:00:00"},
        {"student_id": "1", "role": "teacher", "timestamp": "2025-10-04T10:00:05"},
        {"student_id": "1", "role": "student", "timestamp": "2025-10-04T10:00:15"},
        {"student_id": "1", "role": "teacher", "timestamp": "2025-10-04T10:00:20"},
        {"student_id": "1", "role": "student", "timestamp": "2025-10-04T10:00:30"},
        {"student_id": "1", "role": "teacher", "timestamp": "2025-10-04T10:00:35"},
    ]
    
    ids = [f"conv_{i}" for i in range(len(documents))]
    
    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )
    
    print(f"  ✓ Seeded {len(documents)} conversation entries")

def main():
    """Main seeding function"""
    print("\n" + "="*50)
    print("ChromaDB Seeding Script")
    print("="*50 + "\n")
    
    # Connect to ChromaDB
    client = wait_for_chromadb(host="chromadb", port=8000)
    
    # Get Ollama embedding function
    embedding_function = get_ollama_embedding_function()
    
    # Create collections with embedding function
    print("\nCreating collections...")
    collections = create_collections(client, embedding_function)
    
    # Seed each collection
    print("\nSeeding collections with fake data...")
    
    print("\n1. Seeding AMC8_math...")
    seed_amc8_math(collections['AMC8_math'])
    
    print("\n2. Seeding student_persona...")
    seed_student_persona(collections['student_persona'])
    
    print("\n3. Seeding math_related...")
    seed_math_related(collections['math_related'])
    
    print("\n4. Seeding AMC8_problems...")
    seed_amc8_problems(collections['AMC8_problems'])
    
    print("\n5. Seeding conversation_history...")
    seed_conversation_history(collections['conversation_history'])
    
    # Summary
    print("\n" + "="*50)
    print("Seeding Complete!")
    print("="*50)
    print("\nCollection Summary:")
    for name, collection in collections.items():
        count = collection.count()
        print(f"  • {name}: {count} items")
    print()

if __name__ == "__main__":
    try:
        main()
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error during seeding: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
