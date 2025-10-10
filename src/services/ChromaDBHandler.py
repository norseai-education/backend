import chromadb
from chromadb.config import Settings
from typing import List, Dict, Optional, Union

class ChromaDBHandler:
    #def __init__(self, host: str = "172.16.0.154", port: int = 8000):
    def __init__(self, host: str = "chromadb.local", port: int = 8000):
        """
        Initialize the ChromaDB client
        
        Args:
            host: Chroma DB server host
            port: Chroma DB server port
        """
        self.client = chromadb.HttpClient(
            host=host,
            port=port,
            settings=Settings(allow_reset=True)
        )
    
    def create_collection(self, collection_name: str, metadata: Optional[Dict] = None) -> chromadb.Collection:
        """
        Create a new collection
        
        Args:
            collection_name: Name of the collection to create
            metadata: Optional metadata for the collection
            
        Returns:
            The created collection
        """
        return self.client.create_collection(name=collection_name, metadata=metadata)
    
    def get_collection(self, collection_name: str) -> chromadb.Collection:
        """
        Get an existing collection
        
        Args:
            collection_name: Name of the collection to retrieve
            
        Returns:
            The requested collection
        """
        return self.client.get_collection(name=collection_name)
    
    def add_documents(
        self,
        collection_name: str,
        documents: List[str],
        ids: List[str],
        metadatas: Optional[List[Dict]] = None,
        embeddings: Optional[List[List[float]]] = None,
        embedding_model: Optional[object] = None
    ) -> None:
        """
        Add documents to a collection
        
        Args:
            collection_name: Name of the collection
            documents: List of document texts
            ids: List of unique IDs for each document
            metadatas: Optional list of metadata dictionaries
            embeddings: Optional pre-computed embeddings
            embedding_model: Optional custom embedding model to generate embeddings
        """
        collection = self.get_collection(collection_name)
        
        # Generate embeddings using custom model if provided and embeddings not provided
        if embedding_model is not None and embeddings is None:
            embeddings = embedding_model.embed_documents(documents)
        
        collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas,
            embeddings=embeddings
        )
    
    def query(self, model, collection, query_text: str, n_results: int, metadata_filter: dict = None):
        # Generate embedding for the query
        query_embedding = model.embed_query(query_text)
        
        # Prepare query parameters
        query_params = {
            "query_embeddings": [query_embedding],
            "n_results": n_results,
            "include": ['documents', 'metadatas', 'distances']
        }
        
        # Add metadata filter if provided
        if metadata_filter:
            query_params["where"] = metadata_filter
        
        # Search with or without metadata filter
        try:
            results = collection.query(**query_params)
            return results if results['documents'] else []

        except Exception as e:
            return e
    
    def update_documents(
        self,
        collection_name: str,
        ids: List[str],
        documents: Optional[List[str]] = None,
        metadatas: Optional[List[Dict]] = None,
        embeddings: Optional[List[List[float]]] = None
    ) -> None:
        """
        Update documents in a collection
        
        Args:
            collection_name: Name of the collection
            ids: List of document IDs to update
            documents: Updated document texts (optional)
            metadatas: Updated metadata (optional)
            embeddings: Updated embeddings (optional)
        """
        collection = self.get_collection(collection_name)
        collection.update(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
            embeddings=embeddings
        )
    
    def delete_documents(
        self,
        collection_name: str,
        ids: List[str]
    ) -> None:
        """
        Delete documents from a collection
        
        Args:
            collection_name: Name of the collection
            ids: List of document IDs to delete
        """
        collection = self.get_collection(collection_name)
        collection.delete(ids=ids)
    
    def delete_collection(self, collection_name: str) -> None:
        """
        Delete an entire collection
        
        Args:
            collection_name: Name of the collection to delete
        """
        self.client.delete_collection(name=collection_name)
    
    def list_collections(self) -> List[chromadb.Collection]:
        """
        List all collections
        
        Returns:
            List of collection objects
        """
        return self.client.list_collections()
    
    def get_all_ids(self, collection_name: str) -> List[str]:
        """
        Get all document IDs from a collection
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            List of all document IDs in the collection
        """
        collection = self.get_collection(collection_name)
        # Use get() method to retrieve all documents
        results = collection.get()
        return results['ids'] if results['ids'] else []
    
    def get_all_documents(self, collection_name: str, include_metadata: bool = True) -> Dict:
        """
        Get all documents from a collection
        
        Args:
            collection_name: Name of the collection
            include_metadata: Whether to include metadata in the results
            
        Returns:
            Dictionary containing documents, IDs, and optionally metadata
        """
        collection = self.get_collection(collection_name)
        
        # include_fields = ['documents', 'ids']
        # if include_metadata:
        #     include_fields.append('metadatas')
            
        results = collection.get()
        return results
    
    def get_collection_count(self, collection_name: str) -> int:
        """
        Get the total number of documents in a collection
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            Number of documents in the collection
        """
        collection = self.get_collection(collection_name)
        results = collection.get()
        return len(results['ids']) if results['ids'] else 0

# Example usage
# if __name__ == "__main__":
#     try:
#         db_manager = ChromaDBHandler(host="172.16.0.154", port=8000)
#         print("Successfully connected to Chroma DB server")
        
#         # Test connection by listing collections
#         collections = db_manager.list_collections()
#         print(f"Existing collections: {[col.name for col in collections]}")
        
#         # Create a collection
#         collection = db_manager.create_collection("test_collection")
        
        # # Add documents
        # db_manager.add_documents(
        #     collection_name="test_collection",
        #     documents=["This is document 1", "This is document 2"],
        #     ids=["doc1", "doc2"],
        #     metadatas=[{"source": "web"}, {"source": "database"}]
        # )
        
        # # Query documents
        # results = db_manager.query(
        #     collection_name="test_collection",
        #     query_texts=["document"],
        #     n_results=2
        # )
        # print(results)
        
        # # Update a document
        # db_manager.update_documents(
        #     collection_name="test_collection",
        #     ids=["doc1"],
        #     documents=["This is updated document 1"],
        #     metadatas=[{"source": "updated"}]
        # )
        
        # # Delete a document
        # db_manager.delete_documents(
        #     collection_name="test_collection",
        #     ids=["doc2"]
        # )
        
        # # Delete the collection
        # db_manager.delete_collection("test_collection")        

    # except Exception as e:
    #     print(f"Error connecting to Chroma DB: {e}")
