# dao/embedding_dao.py
import chromadb
import os
import logging

logger = logging.getLogger(__name__)

class EmbeddingDAO:
    def __init__(self):
        # Connect to ChromaDB server
        self.client = chromadb.HttpClient(
            host=os.getenv("CHROMA_HOST", "localhost"),
            port=int(os.getenv("CHROMA_PORT", "8484"))
        )
        
        # Initialize ChromaDB client
        self.collection = self.client.get_or_create_collection("client_collection")

    def store_embedding(self, url, embedding, content):
        # Store embedding and content in ChromaDB
        self.collection.add(
            documents=[content],
            metadatas=[{"url": url}],
            embeddings=[embedding],
            ids=[url]  # For single vector
        )

    def query_embedding(self, embedding, n_results=10):
        # Retrieve the top `n_results` similar documents
        result = self.collection.query(
            query_embeddings=embedding,    # Unpack the first embedding
            n_results=n_results            # Use limit instead of n_results
        )

        return result

    def delete_by_url(self, url: str) -> bool:
        # Delete entries where metadata.url matches the given url
        self.collection.delete(
            where={"url": url}
        )

        return True
       
