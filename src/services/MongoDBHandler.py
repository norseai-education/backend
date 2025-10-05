from pymongo import MongoClient
from pymongo.errors import PyMongoError
from typing import Dict, Any, Union, List, Optional
from bson import ObjectId
from ..utils import logging
from ..config.settings import settings

# Configure logging
logger = logging.set_logger(__name__)

class MongoDBHandler:
    def __init__(self, connection_uri: str = None):
        """
        Initialize MongoDB connection handler.
        
        Args:
            connection_uri: MongoDB connection string
                           (default: from settings based on environment)
        """
        self.connection_uri = connection_uri or settings.mongodb_url
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
            logging.log("Connected to MongoDBHandler!", logger, 2)
            return True
        except PyMongoError as e:
            logging.log(f"Failed to connect to MongoDB: {e}", logger, 0)
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

    def list_databases(self):
        self.client = MongoClient(self.connection_uri)
        return self.client.list_database_names()
    
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
            logging.log("Not connected to database", logger, 1)
            return None
            
        try:
            logging.log("Inserting document to MongoDB", logger, 1)
            collection = self.db[collection_name]
            if many:
                if not isinstance(document, list):
                    logging.log("For many=True, document must be a list", logger, 1)
                    return None
                result = collection.insert_many(document)
                logging.log("Document inserted to MongoDB", logger, 1)
                return result.inserted_ids
            else:
                if isinstance(document, list):
                    document = document[0]  # Take first if list provided
                result = collection.insert_one(document)
                logging.log("Document inserted to MongoDB", logger, 1)
                return result.inserted_id
        except PyMongoError as e:
            logging.log(f"MongoDB error inserting document: {e}", logger, 1)
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
            logging.log("Not connected to MongoDB", logger, 2)
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
            logging.log(f"MongoDB error finding documents: {e}", logger, 0)
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
            logging.log("Not connected to MongoDB", logger, 2)
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
            logging.log(f"MongoDB error updating documents: {e}", logger, 0)
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
            logging.log("Not connected to MongoDB", logger, 2)
            return 0
            
        try:
            collection = self.db[collection_name]
            if many:
                result = collection.delete_many(query)
            else:
                result = collection.delete_one(query)
            return result.deleted_count
        except PyMongoError as e:
            logging.log(f"MongoDB error deleting documents: {e}", logger, 0)
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
            logging.log("Not connected to MongoDB", logger, 2)
            return 0
            
        try:
            collection = self.db[collection_name]
            return collection.count_documents(query or {})
        except PyMongoError as e:
            logging.log(f"MongoDB error counting documents: {e}", logger, 0)
            return 0
    
    def __enter__(self):
        """Support for context manager protocol."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensure connection is closed when exiting context."""
        self.close()