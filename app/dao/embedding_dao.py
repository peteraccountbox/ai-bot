# dao/embedding_dao.py
import chromadb
import os
from chromadb.config import Settings
from app.utils.context import get_index_name

class EmbeddingDAO:
    def __init__(self):
        try:
            # Use PersistentClient with a local path
            persist_directory = os.getenv("CHROMA_PERSIST_DIR", "./chroma_db")
            
            self.client = chromadb.PersistentClient(
                path=persist_directory,
                settings=Settings(
                    anonymized_telemetry=False,
                    allow_reset=True
                )
            )
            print(f"Successfully connected to ChromaDB at {persist_directory}")
        except Exception as e:
            print(f"Failed to initialize ChromaDB: {str(e)}")
            raise e
    
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

    def get_collection_info(self):
        """Get information about the current collection"""
        collection = self._get_collection()
        return {
            "name": collection.name,
            "count": collection.count()
        }

    def get_similar_documents(self, query_embedding, n_results=10):
        """Get similar documents using embeddings"""
        collection = self._get_collection()
        return collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results,
            include=["documents", "metadatas", "distances"]
        )

       
