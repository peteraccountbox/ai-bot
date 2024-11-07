from langchain.memory import ConversationBufferMemory
from typing import Dict, Optional, Any, Tuple, List
from langchain.schema import BaseMessage
from langchain.schema.messages import HumanMessage, AIMessage
import uuid
import json
from redis import Redis
import os

class MemoryService:
    def __init__(self):
        # Initialize Redis client
        self.redis = Redis(host=os.getenv("REDIS_HOST", "localhost"), port=os.getenv("REDIS_PORT", 6379), db=os.getenv("REDIS_DB", 0), decode_responses=True)

    def generate_conversation_id(self) -> str:
        # Generate a unique conversation ID
        return str(uuid.uuid4())

    def serialize_memory(self, memory: ConversationBufferMemory) -> str:
        # Convert the ConversationBufferMemory object to a JSON-serializable format
        return json.dumps({
            "chat_memory": [{
                "role": msg.type,
                "content": msg.content
            } for msg in memory.chat_memory.messages],
            "memory_key": memory.memory_key,
            "input_key":memory.input_key,
            "return_messages": memory.return_messages
        })

    def deserialize_memory(self, data: str) -> ConversationBufferMemory:
        # Convert JSON data back to a ConversationBufferMemory object
        loaded_data = json.loads(data)
        memory = ConversationBufferMemory(
            memory_key=loaded_data["memory_key"],
            return_messages=loaded_data["return_messages"],
            input_key=loaded_data["input_key"]
        )
        
        # Convert messages to appropriate types based on role
        memory.chat_memory.messages = [
            HumanMessage(content=msg["content"]) if msg["role"] == "human" 
            else AIMessage(content=msg["content"])
            for msg in loaded_data["chat_memory"]
        ]
        return memory

    def get_memory(self, conversation_id: Optional[str] = None) -> Tuple[str, ConversationBufferMemory]:
        # Generate new conversation ID if none is provided
        if not conversation_id:
            conversation_id = self.generate_conversation_id()

        # Retrieve memory from Redis
        memory_data = self.redis.get(f"memory:{conversation_id}")

        # Deserialize memory if found
        if memory_data:
            memory = self.deserialize_memory(memory_data)
        else:
            # Create a new empty memory if no existing data
            memory = ConversationBufferMemory(
                return_messages=True,
                memory_key="chat_history",
                input_key = "input",
            )

        return conversation_id, memory

    def save_memory(self, conversation_id: str, memory: ConversationBufferMemory) -> None:
        # Serialize and save the memory object in Redis
        serialized_memory = self.serialize_memory(memory)
        self.redis.set(
            f"memory:{conversation_id}",
            serialized_memory,
            ex=86400  # 24 hours expiry
        )

    def clear_memory(self, conversation_id: str) -> None:
        # Delete memory from Redis
        self.redis.delete(f"memory:{conversation_id}")

    def get_chat_history(self, conversation_id: str) -> List[Dict[str, Any]]:
        # Retrieve and deserialize chat history
        memory_data = self.redis.get(f"memory:{conversation_id}")
        if memory_data:
            memory = self.deserialize_memory(memory_data)
            return [{
                "role": msg.type,
                "content": msg.content
            } for msg in memory.chat_memory.messages]
        return []
