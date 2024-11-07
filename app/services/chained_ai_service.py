from langchain.memory import ConversationBufferWindowMemory
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import ConversationalRetrievalChain
from langchain.prompts import SystemMessagePromptTemplate, HumanMessagePromptTemplate, ChatPromptTemplate
from langchain.schema import Document
from app.dao.embedding_dao import EmbeddingDAO
import uuid
from typing import Dict, Any
from datetime import datetime

class ChainedAIService:
    _instance = None
    _memories = {}
    _last_accessed = {}

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ChainedAIService, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return
            
        self.embeddings = OpenAIEmbeddings()
        self.embedding_dao = EmbeddingDAO()
        self.llm = ChatOpenAI(temperature=0.7)
        self.memory_ttl = 3600
        self._initialized = True

    def _create_retriever(self):
        """Create a custom retriever that uses EmbeddingDAO"""
        class CustomRetriever:
            def __init__(self, embedding_dao, embeddings):
                self.embedding_dao = embedding_dao
                self.embeddings = embeddings

            async def aget_relevant_documents(self, query: str):
                # Get embedding for query
                query_embedding = self.embeddings.embed_query(query)
                
                # Query the embedding dao
                results = self.embedding_dao.query_embedding([query_embedding])
                
                # Convert to Document objects
                documents = []
                for idx, content in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][idx] if results['metadatas'] else {}
                    documents.append(Document(
                        page_content=content,
                        metadata=metadata
                    ))
                
                return documents

            def get_relevant_documents(self, query: str):
                # Synchronous version if needed
                raise NotImplementedError("Please use async version")

        return CustomRetriever(self.embedding_dao, self.embeddings)

    def _cleanup_old_memories(self):
        """Remove memories that haven't been accessed for longer than TTL"""
        current_time = datetime.now()
        expired_keys = [
            k for k, v in self._last_accessed.items()
            if (current_time - v).total_seconds() > self.memory_ttl
        ]
        for k in expired_keys:
            self._memories.pop(k, None)
            self._last_accessed.pop(k, None)

    def _get_or_create_memory(self, memory_id: str = None) -> tuple[ConversationBufferWindowMemory, str]:
        # Periodic cleanup of old memories
        self._cleanup_old_memories()

        if memory_id and memory_id in self._memories:
            # Update last accessed time
            self._last_accessed[memory_id] = datetime.now()
            return self._memories[memory_id], memory_id

        # Create new memory
        new_memory_id = str(uuid.uuid4())
        self._memories[new_memory_id] = ConversationBufferWindowMemory(
            memory_key="chat_history",
            return_messages=True,
            k=10
        )
        self._last_accessed[new_memory_id] = datetime.now()
        
        return self._memories[new_memory_id], new_memory_id

    def _create_system_prompt(self):
        system_template = """You are a helpful assistant. Follow these rules:
        1. Respond in the same language as the user's question
        2. Provide concise answers unless specifically asked for more detail
        3. Format responses in a structured, easy-to-read manner
        """
        return SystemMessagePromptTemplate.from_template(system_template)

    def _create_chat_prompt(self):
        human_template = "{question}"
        human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)
        
        chat_prompt = ChatPromptTemplate.from_messages([
            self._create_system_prompt(),
            human_message_prompt
        ])
        return chat_prompt

    async def get_structured_answer(self, question: str, memory_id: str = None) -> Dict[str, Any]:
        # Get or create memory
        memory, current_memory_id = self._get_or_create_memory(memory_id)

        # Create conversation chain with custom retriever
        qa_chain = ConversationalRetrievalChain.from_llm(
            llm=self.llm,
            retriever=self._create_retriever(),
            memory=memory,
            combine_docs_chain_kwargs={"prompt": self._create_chat_prompt()}
        )

        # Get response
        response = await qa_chain.arun(question)

        # Update last accessed time
        self._last_accessed[current_memory_id] = datetime.now()

        # Prepare structured output
        result = {
            "memory_id": current_memory_id,
            "question": question,
            "answer": response,
            "has_previous_context": memory_id is not None
        }

        return result 