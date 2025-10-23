import chromadb
from chromadb.config import Settings
from src.utils import logging
from src.services.ChromaDBHandler import ChromaDBHandler
from src.services.models import embedding_model

# Configure logging
logger = logging.set_logger(__name__)
db_handler = ChromaDBHandler()

class MathRagDB:
    def __init__(self, embedding_model = embedding_model):
        self.model = embedding_model
        self.collection = db_handler.get_collection("AMC8_math")

    def retrieve(self, query_text: str, n_results: int, metadata_filter: dict = None):
        """Search with metadata filtering"""
        result = db_handler.query(self.model, self.collection, query_text, n_results, metadata_filter)
        return result['documents'][0]


class PersonaDB:
    def __init__(self, embedding_model = embedding_model):
        self.model = embedding_model
        self.collection = db_handler.get_collection("student_persona")

    def retrieve(self, query_text: str, n_results: int, metadata_filter: dict = None):
        """Search with metadata filtering"""

        result = db_handler.query(self.model, self.collection, query_text, n_results, metadata_filter)
        return result['documents'][0]

class MathRelatedDB:
    def __init__(self, embedding_model = embedding_model):
        self.model = embedding_model
        self.collection = db_handler.get_collection("math_related")
    
    def retrieve(self, query_text: str, n_results: int, metadata_filter: dict = None):
        """Search with metadata filtering"""
        result = db_handler.query(self.model, self.collection, query_text, n_results, metadata_filter)
        return result['documents'][0]

class ProblemDB:
    def __init__(self, embedding_model = embedding_model):
        self.model = embedding_model
        self.collection = db_handler.get_collection("AMC8_problems")

    def retrieve(self, query_text: str, n_results: int):
        """Search with metadata filtering"""
        result = db_handler.query(self.model, self.collection, query_text, n_results)
        # logging.log(f"Retrieved problems: {result}", logger, 2)
        return result['documents'][0], result['metadatas'][0], result['ids'][0]


class ArchivedConversationHistory:
    def __init__(self, embedding_model = embedding_model):
        self.model = embedding_model
        self.collection = db_handler.get_collection("conversation_history")

    def retrieve(self, query_text: str, n_results: int, metadata_filter: dict = None):
        """Search with metadata filtering"""
        result = db_handler.query(self.model, self.collection, query_text, n_results, metadata_filter)
        return result['documents'][0]
