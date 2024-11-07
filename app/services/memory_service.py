from langchain.memory import ConversationBufferMemory
from typing import Dict, Optional
import uuid

class MemoryService:
    def __init__(self):
        self.conversations: Dict[str, ConversationBufferMemory] = {}

    def generate_conversation_id(self) -> str:
        return str(uuid.uuid4())

    def get_memory(self, conversation_id: Optional[str] = None) -> tuple[str, ConversationBufferMemory]:
        # Generate new ID if none provided
        if not conversation_id:
            conversation_id = self.generate_conversation_id()
            
        if conversation_id not in self.conversations:
            self.conversations[conversation_id] = ConversationBufferMemory(
                return_messages=True,
                memory_key="chat_history",
                input_key="input"
            )
        return conversation_id, self.conversations[conversation_id]

    def clear_memory(self, conversation_id: str) -> None:
        if conversation_id in self.conversations:
            self.conversations[conversation_id].clear()
            del self.conversations[conversation_id]

    def get_chat_history(self, conversation_id: str) -> list:
        _, memory = self.get_memory(conversation_id)
        return memory.load_memory_variables({}).get("chat_history", [])

    def cleanup_inactive_sessions(self, max_age_hours: int = 24) -> None:
        # Implement cleanup logic for old sessions
        pass 