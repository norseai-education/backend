import chromadb
from chromadb.config import Settings
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from typing import Dict, Any, Union, List, Optional
from bson import ObjectId
import utils

# Configure logging
logger = utils.set_logger(__name__)

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
        utils.log("Successfully connected to MathRagDB!", logger, 2)
        return client
    
    def get_collection(self, client, collection_name: str):
        """Get existing collection from ChromaDB"""
        try:
            collection = client.get_collection(collection_name)
            utils.log("Successfully got collection from MathRagDB!", logger, 2)
            return collection
        except Exception as e:
            utils.log(f"MathRagDB error getting collection: {e}", logger, 0)
            return None

    def retrieve(self, collection, query_text: str, n_results: int, metadata_filter: dict = None):
        """Search with metadata filtering"""
        
        utils.log(f"Retrieving from MathRagDB with query: {query_text}", logger, 2)
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
            utils.log(f"Using metadata filters: {metadata_filter}", logger, 2)
            query_params["where"] = metadata_filter
        
        # Search with or without metadata filter
        try:
            results = collection.query(**query_params)
            return results['documents'][0] if results['documents'] else []

        except Exception as e:
            utils.log(f"MathRagDB filter search error: {e}", logger, 0)
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
        utils.log("Successfully connect to PersonaDB!", logger, 2)
        return client
    
    def get_collection(self, client, collection_name: str):
        """Get existing collection from ChromaDB"""
        try:
            collection = client.get_collection(collection_name)
            utils.log("Successfully got collection from PersonaDB!", logger, 2)
            return collection
        except Exception as e:
            utils.log(f"PersonaDB error getting collection: {e}", logger, 0)
            return None

    def retrieve(self, collection, query_text: str, n_results: int, metadata_filter: dict = None):
        """Search with metadata filtering"""

        utils.log(f"Retrieving from PersonDB with query: {query_text}", logger, 2)

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
            utils.log(f"Using metadata filters: {metadata_filter}", logger, 2)
            query_params["where"] = metadata_filter
        
        # Search with or without metadata filter
        try:
            results = collection.query(**query_params)
            return results['documents'][0] if results['documents'] else []

        except Exception as e:
            utils.log(f"PersonaDB filter search error: {e}", logger, 0)
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
        utils.log("Successfully connect to MathRelatedDB!", logger, 2)
        return client
    
    def get_collection(self, client, collection_name: str):
        """Get existing collection from ChromaDB"""
        try:
            collection = client.get_collection(collection_name)
            utils.log("Successfully got collection from MathRelatedDB!", logger, 2)
            return collection
        except Exception as e:
            utils.log(f"MathRelatedDB error getting collection: {e}", logger, 0)
            return None
    
    def retrieve(self, collection, query_text: str, n_results: int, metadata_filter: dict = None):
        """Search with metadata filtering"""

        utils.log(f"Retrieving from MathRelatedDB with query: {query_text}", logger, 2)
        
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
            utils.log(f"Using metadata filters: {metadata_filter}", logger, 2)
            query_params["where"] = metadata_filter
        
        # Search with or without metadata filter
        try:
            results = collection.query(**query_params)
            return results['documents'][0] if results['documents'] else []

        except Exception as e:
            utils.log(f"MathRelatedDB filter search error: {e}", logger, 0)
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
        utils.log("Successfully connect to ProblemDB!", logger, 2)
        return client
    
    def get_collection(self, client, collection_name: str):
        """Get existing collection from ChromaDB"""
        try:
            collection = client.get_collection(collection_name)
            utils.log("Successfully got collection from ProblemDB!", logger, 2)
            return collection
        except Exception as e:
            utils.log(f"ProblemDB error getting collection: {e}", logger, 0)
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
        
        utils.log(f"Retrieving from ProblemDB with query: {query_text}", logger, 2)

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
            utils.log(f"Using metadata filters: {where_clause}", logger, 2)
            query_params["where"] = where_clause
        
        # Search with or without metadata filter
        try:
            results = collection.query(**query_params)
            return results['documents'][0] if results['documents'] else []

        except Exception as e:
            utils.log(f"ProblemDB filter search error: {e}", logger, 0)
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
        utils.log("Successfully connect to ArchivedDB!", logger, 2)
        return client
    
    def get_collection(self, client, collection_name: str):
        """Get existing collection from ChromaDB"""
        try:
            collection = client.get_collection(collection_name)
            utils.log("Successfully got collection from ArchivedDB!", logger, 2)
            return collection
        except Exception as e:
            utils.log(f"ArchivedDB error getting collection: {e}", logger, 0)
            return None

    def retrieve(self, collection, query_text: str, n_results: int, metadata_filter: dict = None):
        """Search with metadata filtering"""
        
        utils.log(f"Retrieving from ArchivedDB with query: {query_text}", logger, 2)

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
            utils.log(f"Using metadata filters: {metadata_filter}", logger, 2)
            query_params["where"] = metadata_filter
        
        # Search with or without metadata filter
        try:
            results = collection.query(**query_params)
            return results['documents'][0] if results['documents'] else []

        except Exception as e:
            utils.log(f"ArchivedDB filter search error: {e}", logger, 0)
            return [] 





class MongoDBHandler:
    def __init__(self, connection_uri: str = "mongodb://localhost:27017/"):
        """
        Initialize MongoDB connection handler.
        
        Args:
            connection_uri: MongoDB connection string
                           (default: "mongodb://localhost:27017/")
        """
        self.connection_uri = connection_uri
        self.client = None
        self.db = None
        
    def connect(self, database_name: str) -> bool:
        """
        Connect to a specific database.
        
        Args:
            database_name: Name of the database to connect to
            
        Returns:
            bool: True if connection successful, False otherwise
        """
        try:
            self.client = MongoClient(self.connection_uri)
            self.db = self.client[database_name]
            # Test the connection
            self.client.server_info()
            utils.log("Connected to MongoDBHandler!", logger, 2)
            return True
        except PyMongoError as e:
            utils.log(f"Failed to connect to MongoDB: {e}", logger, 0)
            return False
        
    def is_connected(self) -> bool:
        """Check if the handler is connected to a database."""
        return self.client is not None and self.db is not None    
    
    def close(self) -> None:
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()
            self.client = None
            self.db = None

    def list_collections(self):
        return self.db.list_collection_names()
    
    def create_collection(self, collection_name):
        collection = self.db[collection_name]
        return collection

    def clear_collection(self, collection_name):
        collection = self.db[collection_name]
        result = collection.delete_many({})
        return result
    
    async def insert_document(
        self,
        collection_name: str,
        document: Union[Dict[str, Any], List[Dict[str, Any]]],
        many: bool = False
    ) -> Optional[Union[ObjectId, List[ObjectId]]]:
        """
        Insert one or many documents into a collection.
        
        Args:
            collection_name: Name of the collection
            document: Document(s) to insert
            many: If True, insert many documents
            
        Returns:
            Inserted document ID(s) or None if failed
        """
        if not self.is_connected():
            utils.log("Not connected to database", logger, 1)
            return None
            
        try:
            utils.log("Inserting document to MongoDB", logger, 1)
            collection = self.db[collection_name]
            if many:
                if not isinstance(document, list):
                    utils.log("For many=True, document must be a list", logger, 1)
                    return None
                result = collection.insert_many(document)
                utils.log("Document inserted to MongoDB", logger, 1)
                return result.inserted_ids
            else:
                if isinstance(document, list):
                    document = document[0]  # Take first if list provided
                result = collection.insert_one(document)
                utils.log("Document inserted to MongoDB", logger, 1)
                return result.inserted_id
        except PyMongoError as e:
            utils.log(f"MongoDB error inserting document: {e}", logger, 1)
            return None
    
    def find_documents(
        self,
        collection_name: str,
        query: Optional[Dict[str, Any]] = None,
        projection: Optional[Dict[str, Any]] = None,
        limit: int = 0,
        sort: Optional[List[tuple]] = None
    ) -> List[Dict[str, Any]]:
        """
        Find documents in a collection.
        
        Args:
            collection_name: Name of the collection
            query: Filter query (empty for all documents)
            projection: Fields to include/exclude
            limit: Maximum number of documents to return (0 for no limit)
            sort: List of (field, direction) tuples to sort by
            
        Returns:
            List of matching documents
        """
        if not self.is_connected():
            utils.log("Not connected to MongoDB", logger, 2)
            return []
            
        try:
            collection = self.db[collection_name]
            cursor = collection.find(query or {}, projection)
            
            if sort:
                cursor = cursor.sort(sort)
            if limit > 0:
                cursor = cursor.limit(limit)
                
            return list(cursor)
        except PyMongoError as e:
            utils.log(f"MongoDB error finding documents: {e}", logger, 0)
            return []
    
    def update_document(
        self,
        collection_name: str,
        query: Dict[str, Any],
        update_data: Dict[str, Any],
        many: bool = False,
        upsert: bool = False
    ) -> int:
        """
        Update document(s) in a collection.
        
        Args:
            collection_name: Name of the collection
            query: Filter query to select documents to update
            update_data: Data to update ($set operations will be added automatically)
            many: If True, update all matching documents
            upsert: If True, insert a new document if no match found
            
        Returns:
            Number of documents modified
        """
        if not self.is_connected():
            utils.log("Not connected to MongoDB", logger, 2)
            return 0
            
        try:
            collection = self.db[collection_name]
            # Automatically add $set operator if not present
            if not any(op in update_data for op in ["$set", "$unset", "$inc", "$push"]):
                update_data = {"$set": update_data}
            
            if many:
                result = collection.update_many(query, update_data, upsert=upsert)
            else:
                result = collection.update_one(query, update_data, upsert=upsert)
                
            return result.modified_count
        except PyMongoError as e:
            utils.log(f"MongoDB error updating documents: {e}", logger, 0)
            return 0
    
    def delete_document(
        self,
        collection_name: str,
        query: Dict[str, Any],
        many: bool = False
    ) -> int:
        """
        Delete document(s) from a collection.
        
        Args:
            collection_name: Name of the collection
            query: Filter query to select documents to delete
            many: If True, delete all matching documents
            
        Returns:
            Number of documents deleted
        """
        if not self.is_connected():
            utils.log("Not connected to MongoDB", logger, 2)
            return 0
            
        try:
            collection = self.db[collection_name]
            if many:
                result = collection.delete_many(query)
            else:
                result = collection.delete_one(query)
            return result.deleted_count
        except PyMongoError as e:
            utils.log(f"MongoDB error deleting documents: {e}", logger, 0)
            return 0
    
    def count_documents(
        self,
        collection_name: str,
        query: Optional[Dict[str, Any]] = None
    ) -> int:
        """
        Count documents in a collection matching a query.
        
        Args:
            collection_name: Name of the collection
            query: Filter query (empty for all documents)
            
        Returns:
            Number of matching documents
        """
        if not self.is_connected():
            utils.log("Not connected to MongoDB", logger, 2)
            return 0
            
        try:
            collection = self.db[collection_name]
            return collection.count_documents(query or {})
        except PyMongoError as e:
            utils.log(f"MongoDB error counting documents: {e}", logger, 0)
            return 0
    
    def __enter__(self):
        """Support for context manager protocol."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure connection is closed when exiting context."""
        self.close()