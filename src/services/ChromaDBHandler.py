import chromadb
from chromadb.config import Settings
from backend.src.utils import logging

# Configure logging
logger = logging.set_logger(__name__)

class MathRagDB:
    def __init__(self, embedding_model):
        self.host = "172.16.0.154"
        self.port = 8000
        self.model = embedding_model
    
    def connect_to_db(self):
        """Connect to the remote ChromaDB server"""
        client = chromadb.HttpClient(
            host=self.host,
            port=self.port,
            settings=Settings(allow_reset=True)
        )
        logging.log("Successfully connected to MathRagDB!", logger, 2)
        return client
    
    def get_collection(self, client, collection_name: str):
        """Get existing collection from ChromaDB"""
        try:
            collection = client.get_collection(collection_name)
            logging.log("Successfully got collection from MathRagDB!", logger, 2)
            return collection
        except Exception as e:
            logging.log(f"MathRagDB error getting collection: {e}", logger, 0)
            return None

    def retrieve(self, collection, query_text: str, n_results: int, metadata_filter: dict = None):
        """Search with metadata filtering"""
        
        logging.log(f"Retrieving from MathRagDB with query: {query_text}", logger, 2)
        # Generate embedding for the query
        query_embedding = self.model.embed_query(query_text)
        
        # Prepare query parameters
        query_params = {
            "query_embeddings": [query_embedding],
            "n_results": n_results,
            "include": ['documents', 'metadatas', 'distances']
        }
        
        # Add metadata filter if provided
        if metadata_filter:
            logging.log(f"Using metadata filters: {metadata_filter}", logger, 2)
            query_params["where"] = metadata_filter
        
        # Search with or without metadata filter
        try:
            results = collection.query(**query_params)
            return results['documents'][0] if results['documents'] else []

        except Exception as e:
            logging.log(f"MathRagDB filter search error: {e}", logger, 0)
            return [] 


class PersonaDB:
    def __init__(self, embedding_model):
        self.model = embedding_model
        self.host = "172.16.0.154"
        self.port = 8000

    def connect_to_db(self):
        """Connect to the remote ChromaDB server"""
        client = chromadb.HttpClient(
            host=self.host,
            port=self.port,
            settings=Settings(allow_reset=True)
        )
        logging.log("Successfully connect to PersonaDB!", logger, 2)
        return client
    
    def get_collection(self, client, collection_name: str):
        """Get existing collection from ChromaDB"""
        try:
            collection = client.get_collection(collection_name)
            logging.log("Successfully got collection from PersonaDB!", logger, 2)
            return collection
        except Exception as e:
            logging.log(f"PersonaDB error getting collection: {e}", logger, 0)
            return None

    def retrieve(self, collection, query_text: str, n_results: int, metadata_filter: dict = None):
        """Search with metadata filtering"""

        logging.log(f"Retrieving from PersonDB with query: {query_text}", logger, 2)

        # Generate embedding for the query
        query_embedding = self.model.embed_query(query_text)
        
        # Prepare query parameters
        query_params = {
            "query_embeddings": [query_embedding],
            "n_results": n_results,
            "include": ['documents', 'metadatas', 'distances']
        }
        
        # Add metadata filter if provided
        if metadata_filter:
            logging.log(f"Using metadata filters: {metadata_filter}", logger, 2)
            query_params["where"] = metadata_filter
        
        # Search with or without metadata filter
        try:
            results = collection.query(**query_params)
            return results['documents'][0] if results['documents'] else []

        except Exception as e:
            logging.log(f"PersonaDB filter search error: {e}", logger, 0)
            return [] 

class MathRelatedDB:
    def __init__(self, embedding_model):
        self.model = embedding_model
        #self.session_id = session_id
        self.host = "172.16.0.154"
        self.port = 8000

    
    def connect_to_db(self):
        """Connect to the remote ChromaDB server"""
        client = chromadb.HttpClient(
            host=self.host,
            port=self.port,
            settings=Settings(allow_reset=True)
        )
        logging.log("Successfully connect to MathRelatedDB!", logger, 2)
        return client
    
    def get_collection(self, client, collection_name: str):
        """Get existing collection from ChromaDB"""
        try:
            collection = client.get_collection(collection_name)
            logging.log("Successfully got collection from MathRelatedDB!", logger, 2)
            return collection
        except Exception as e:
            logging.log(f"MathRelatedDB error getting collection: {e}", logger, 0)
            return None
    
    def retrieve(self, collection, query_text: str, n_results: int, metadata_filter: dict = None):
        """Search with metadata filtering"""

        logging.log(f"Retrieving from MathRelatedDB with query: {query_text}", logger, 2)
        
        # Generate embedding for the query
        query_embedding = self.model.embed_query(query_text)
        
        # Prepare query parameters
        query_params = {
            "query_embeddings": [query_embedding],
            "n_results": n_results,
            "include": ['documents', 'metadatas', 'distances']
        }
        
        # Add metadata filter if provided
        if metadata_filter:
            logging.log(f"Using metadata filters: {metadata_filter}", logger, 2)
            query_params["where"] = metadata_filter
        
        # Search with or without metadata filter
        try:
            results = collection.query(**query_params)
            return results['documents'][0] if results['documents'] else []

        except Exception as e:
            logging.log(f"MathRelatedDB filter search error: {e}", logger, 0)
            return [] 

class ProblemDB:
    def __init__(self, embedding_model):
        self.host = "172.16.0.154"
        self.port = 8000
        self.model = embedding_model
    
    def connect_to_db(self):
        """Connect to the remote ChromaDB server"""
        client = chromadb.HttpClient(
            host=self.host,
            port=self.port,
            settings=Settings(allow_reset=True)
        )
        logging.log("Successfully connect to ProblemDB!", logger, 2)
        return client
    
    def get_collection(self, client, collection_name: str):
        """Get existing collection from ChromaDB"""
        try:
            collection = client.get_collection(collection_name)
            logging.log("Successfully got collection from ProblemDB!", logger, 2)
            return collection
        except Exception as e:
            logging.log(f"ProblemDB error getting collection: {e}", logger, 0)
            return None

    def multiple_metadata(self, metadata_filter: dict):
        """Convert metadata filter dict to ChromaDB where clause format"""
        if not metadata_filter:
            return {}
        
        # If only one filter, return it directly
        if len(metadata_filter) == 1:
            key, value = list(metadata_filter.items())[0]
            return {key: value}
        
        # For multiple filters, use $and operator
        conditions = []
        for key, value in metadata_filter.items():
            if key == 'concepts':
                conditions.append({key: {"$in":value}})
            else:
                conditions.append({key: value})
        
        return {"$and": conditions}

    def retrieve(self, collection, query_text: str, metadata_filter: dict, n_results: int):
        """Search with metadata filtering"""
        
        logging.log(f"Retrieving from ProblemDB with query: {query_text}", logger, 2)

        # Generate embedding for the query
        query_embedding = self.model.embed_query(query_text)
        
        # Prepare query parameters
        query_params = {
            "query_embeddings": [query_embedding],
            "n_results": n_results,
            "include": ['documents', 'metadatas', 'distances']
        }
        
        # Add metadata filter if provided
        if metadata_filter:
            # Convert simple dict to ChromaDB where clause format
            where_clause = self.multiple_metadata(metadata_filter)
            logging.log(f"Using metadata filters: {where_clause}", logger, 2)
            query_params["where"] = where_clause
        
        # Search with or without metadata filter
        try:
            results = collection.query(**query_params)
            return results['documents'][0] if results['documents'] else []

        except Exception as e:
            logging.log(f"ProblemDB filter search error: {e}", logger, 0)
            return []
            
    

class ArchivedConversationHistory:
    def __init__(self, embedding_model):
        self.host = "172.16.0.154"
        self.port = 8000
        self.model = embedding_model
    
    def connect_to_db(self):
        """Connect to the remote ChromaDB server"""
        client = chromadb.HttpClient(
            host=self.host,
            port=self.port,
            settings=Settings(allow_reset=True)
        )
        logging.log("Successfully connect to ArchivedDB!", logger, 2)
        return client
    
    def get_collection(self, client, collection_name: str):
        """Get existing collection from ChromaDB"""
        try:
            collection = client.get_collection(collection_name)
            logging.log("Successfully got collection from ArchivedDB!", logger, 2)
            return collection
        except Exception as e:
            logging.log(f"ArchivedDB error getting collection: {e}", logger, 0)
            return None

    def retrieve(self, collection, query_text: str, n_results: int, metadata_filter: dict = None):
        """Search with metadata filtering"""
        
        logging.log(f"Retrieving from ArchivedDB with query: {query_text}", logger, 2)

        # Generate embedding for the query
        query_embedding = self.model.embed_query(query_text)
        
        # Prepare query parameters
        query_params = {
            "query_embeddings": [query_embedding],
            "n_results": n_results,
            "include": ['documents', 'metadatas', 'distances']
        }
        
        # Add metadata filter if provided
        if metadata_filter:
            logging.log(f"Using metadata filters: {metadata_filter}", logger, 2)
            query_params["where"] = metadata_filter
        
        # Search with or without metadata filter
        try:
            results = collection.query(**query_params)
            return results['documents'][0] if results['documents'] else []

        except Exception as e:
            logging.log(f"ArchivedDB filter search error: {e}", logger, 0)
            return [] 
