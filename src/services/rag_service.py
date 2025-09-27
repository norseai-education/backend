import chromadb
from chromadb.config import Settings
from backend.src.utils import logging
from backend.src.services.ChromaDBHandler import ChromaDBHandler
from backend.src.services.models import embedding_model

# Configure logging
logger = logging.set_logger(__name__)
db_handler = ChromaDBHandler()

class MathRagDB:
    def __init__(self, embedding_model = embedding_model):
        self.host = "172.16.0.154"
        self.port = 8000
        self.model = embedding_model
        self.db_handler = db_handler.get_collection("AMC8_math")

    def retrieve(self, query_text: str, n_results: int, metadata_filter: dict = None):
        """Search with metadata filtering"""
        result = db_handler.query(self.model, self.db_handler, query_text, n_results, metadata_filter)
        return result['documents'][0]


class PersonaDB:
    def __init__(self, embedding_model = embedding_model):
        self.model = embedding_model
        self.db_handler = db_handler.get_collection("student_persona")
        self.host = "172.16.0.154"
        self.port = 8000

    def retrieve(self, query_text: str, n_results: int, metadata_filter: dict = None):
        """Search with metadata filtering"""

        result = db_handler.query(self.model, self.db_handler, query_text, n_results, metadata_filter)
        return result['documents'][0]

class MathRelatedDB:
    def __init__(self, embedding_model = embedding_model):
        self.model = embedding_model
        self.db_handler = db_handler.get_collection("math_related")
        self.host = "172.16.0.154"
        self.port = 8000
    
    def retrieve(self, query_text: str, n_results: int, metadata_filter: dict = None):
        """Search with metadata filtering"""
        result = db_handler.query(self.model, self.db_handler, query_text, n_results, metadata_filter)
        return result['documents'][0]

class ProblemDB:
    def __init__(self, embedding_model = embedding_model):
        self.host = "172.16.0.154"
        self.port = 8000
        self.model = embedding_model
        self.db_handler = db_handler.get_collection("AMC8_problems")

    def retrieve(self, query_text: str, n_results: int):
        """Search with metadata filtering"""
        result = db_handler.query(self.model, self.db_handler, query_text, n_results)
        return result['documents'][0], result['metadatas'][0] #, result['ids'][0]


class ArchivedConversationHistory:
    def __init__(self, embedding_model = embedding_model):
        self.host = "172.16.0.154"
        self.port = 8000
        self.model = embedding_model
        self.db_handler = db_handler.get_collection("conversation_history")

    def retrieve(self, query_text: str, n_results: int, metadata_filter: dict = None):
        """Search with metadata filtering"""
        result = db_handler.query(self.model, self.db_handler, query_text, n_results, metadata_filter)
        return result['documents'][0]
