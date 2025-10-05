#!/usr/bin/env python3
"""
Initialize ChromaDB collections for NorseAI
This script creates the required collections in ChromaDB if they don't exist.
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.services.ChromaDBHandler import ChromaDBHandler
from src.utils import logging

logger = logging.set_logger(__name__)

# Collections required by the application
REQUIRED_COLLECTIONS = [
    "AMC8_math",
    "student_persona",
    "math_related",
    "AMC8_problems",
    "conversation_history"
]

def initialize_collections():
    """Initialize all required ChromaDB collections"""
    print("🔄 Initializing ChromaDB collections...")
    print("=" * 50)
    
    try:
        db_handler = ChromaDBHandler()
        
        # Get existing collections
        existing_collections = db_handler.client.list_collections()
        existing_names = [col.name for col in existing_collections]
        
        print(f"\n📋 Existing collections: {existing_names}")
        print()
        
        # Create missing collections
        for collection_name in REQUIRED_COLLECTIONS:
            if collection_name in existing_names:
                print(f"✅ Collection '{collection_name}' already exists")
            else:
                print(f"🔨 Creating collection '{collection_name}'...")
                try:
                    db_handler.client.create_collection(
                        name=collection_name,
                        metadata={"description": f"NorseAI collection for {collection_name}"}
                    )
                    print(f"✅ Successfully created '{collection_name}'")
                except Exception as e:
                    print(f"❌ Failed to create '{collection_name}': {e}")
        
        print()
        print("=" * 50)
        print("✅ ChromaDB initialization complete!")
        print()
        
        # Verify all collections exist
        updated_collections = db_handler.client.list_collections()
        updated_names = [col.name for col in updated_collections]
        
        print(f"📊 Total collections: {len(updated_names)}")
        for name in updated_names:
            print(f"   • {name}")
        
        # Check if any required collections are missing
        missing = set(REQUIRED_COLLECTIONS) - set(updated_names)
        if missing:
            print(f"\n⚠️  Warning: Missing collections: {missing}")
            return False
        else:
            print(f"\n✅ All required collections are present!")
            return True
            
    except Exception as e:
        print(f"\n❌ Error initializing ChromaDB: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = initialize_collections()
    sys.exit(0 if success else 1)
