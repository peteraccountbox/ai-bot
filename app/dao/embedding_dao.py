# dao/embedding_dao.py
import os
from dotenv import load_dotenv
import chromadb
from chromadb.config import Settings
from app.utils.context import get_index_name

class EmbeddingDAO:
    def __init__(self):
        # Load environment variables
        load_dotenv()
        
        # Use os.environ.get() instead of os.getenv()
        chroma_host = os.environ.get("CHROMA_SERVER_HOST") or "localhost"
        chroma_port = int(os.environ.get("CHROMA_SERVER_HTTP_PORT") or "8000")
        
        # Debug print
        print(f"Chroma Config - Host: {chroma_host}, Port: {chroma_port}")
        
        self.client = chromadb.Client(
            Settings(
                chroma_server_host=chroma_host,
                chroma_server_http_port=chroma_port,
                anonymized_telemetry=False
            )
        )
    
    def _get_collection(self):
        # Get collection name from thread local
        collection_name = get_index_name()
        print(f"Using collection: {collection_name}")
        return self.client.get_or_create_collection(collection_name)

    def store_embedding(self, metadatas, embedding, content, title):
        collection = self._get_collection()
        collection.add(
            documents=[content],
            metadatas=metadatas,
            embeddings=[embedding],
            ids=[title]
        )

    def query_embedding(self, embedding, n_results=10):
        collection = self._get_collection()
        return collection.query(
            query_embeddings=embedding,
            n_results=n_results
        )

    def delete_collection(self, collection_name: str) -> bool:
        # Check if collection exists
        if collection_name in [col.name for col in self.client.list_collections()]:
            self.client.delete_collection(collection_name)
            return True
        
        return False

    def delete_document(self, doc_id: str) -> bool:
        """Delete a specific document by ID from the collection"""
        collection = self._get_collection()
        # ChromaDB delete by IDs
        collection.delete(
            ids=[doc_id]
        )
        return True
       

       
