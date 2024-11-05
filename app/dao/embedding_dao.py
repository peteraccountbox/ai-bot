# dao/embedding_dao.py
import chromadb

class EmbeddingDAO:
    def __init__(self):
        self.client = chromadb.HttpClient(
            host="chroma",
            port=8000
        )
        self.collection = self.client.get_or_create_collection("embeddings")

    def store_embedding(self, metadatas, embedding, content, title):
        # Store embedding and content in ChromaDB
        self.collection.add(
            documents=[content],
            metadatas=metadatas,
            embeddings=[embedding],
            ids=[title]
        )

    def query_embedding(self, embedding, n_results=10):
        # Retrieve the top `n_results` similar documents
        result = self.collection.query(
            query_embeddings=embedding,    # Unpack the first embedding
            n_results=n_results            # Use limit instead of n_results
        )

        return result