#!/usr/bin/env python3
"""
Run seed_chromadb.py locally (outside Docker) for development/testing
"""

import sys
import os

# Add backend/src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Set environment variables for local development
os.environ.setdefault('OLLAMA_HOST', 'http://localhost:11434')

# Import and run the seed script
from seed_chromadb import main

if __name__ == "__main__":
    print("🌱 Running ChromaDB Seed Script (Local Development)")
    print("=" * 60)
    print("⚠️  Warning: This will seed ChromaDB running on localhost:8000")
    print("=" * 60)
    print()
    
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
