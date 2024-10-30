from dotenv import load_dotenv
import os
import chromadb

load_dotenv()

# Connect to ChromaDB server
client = chromadb.HttpClient(
    host=os.getenv("CHROMA_HOST"),
    port=int(os.getenv("CHROMA_PORT"))
)

# Test the connection
try:
    # Create or get collection
    collection = client.get_or_create_collection("my_collection")
    print("Successfully connected to ChromaDB!")
    
    # Optional: Add some test data
    collection.add(
        documents=["This is a test document"],
        ids=["test1"]
    )
    
except Exception as e:
    print(f"Connection error: {e}")

