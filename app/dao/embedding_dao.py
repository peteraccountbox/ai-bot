# dao/embedding_dao.py
import chromadb
import os
from app.utils.context import get_index_name

class EmbeddingDAO:
    def __init__(self):
        self.client = chromadb.HttpClient(
            host=os.getenv("CHROMA_HOST", "localhost"),
            port=int(os.getenv("CHROMA_PORT", "8484"))
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
       

       
