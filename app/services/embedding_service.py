# services/embedding_service.py

from app.utils.scraping_utils import WebScraper
from openai import OpenAI
from app.dao.embedding_dao import EmbeddingDAO
from app.models.schemas import TrainRequest, ContentType
from typing import Optional
from app.utils.file_extractor import FileExtractor
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferMemory
from langchain.chains import LLMChain
from langchain.vectorstores.chroma import Chroma
from .memory_service import MemoryService
import chromadb
import os
from langchain.embeddings import OpenAIEmbeddings
from app.utils.context import get_bot_role

class EmbeddingService:
    def __init__(self):
        self.client = OpenAI()
        self.embedding_dao = EmbeddingDAO()
        self.scraper = WebScraper()
        self.file_extractor = FileExtractor()
        self.embedding_function = OpenAIEmbeddings(model="text-embedding-ada-002")
        self.chat_model = ChatOpenAI(
            model="gpt-4o",
            temperature=0.7
        )
        
        # Use the ChromaDB client from the DAO instead of creating a new one
        self.chroma_client = self.embedding_dao.client
        self.memory_service = MemoryService()

    def get_system_prompt(self):
        bot_role = get_bot_role()
        bot_role = bot_role.replace(" assistant", "")

        # Your original system message
        system_message = f"""You're the {bot_role} assistant: For greetings or introductions, respond briefly and naturally without bullet points. For content questions, start with a brief intro (5-10 words), then use concise bullet points based on context. Only answer content questions using provided context/memory. If information is missing, say 'I'm only able to answer questions based on the provided context.' Default to English unless user's question is in another language."""
        # system_message = f"""You're the {bot_role} assistant: Start with a brief intro (5-10 words), then use concise bullet points (max 2 sentences each) based on provided context and memory. Incorporate relevant details from prior conversations stored in memory where applicable. Default to English unless the user's question is in a different language."""
        # system_message = """You're EngageBay's CRM assistant: Start with a brief intro (5-10 words), then use concise bullet points (max 2 sentences each) based only on provided context. Reply in the question's language or default to English."""

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_message),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "Context: {context}\n\nQuestion: {input}\n\nAnswer based strictly on both memory and context. If the context does not include relevant information, respond with 'I'm only able to answer questions based on the provided context.'")
        ])
        return prompt

    async def process_payload(self, request: TrainRequest):
        # Get content
        if request.type == ContentType.URL:
            content = self.scraper.scrape_url(request.content)
        elif request.type == ContentType.FILE:
            content = await self.file_extractor.extract_text_from_url(request.content)
        else:
            content = self.scraper.extract_text_from_html(request.content)

        # Generate embedding
        embedding = self.generate_embedding(content)
        
        # Store metadata
        metadatas = [
            {
                "url": request.content if request.type in (ContentType.URL, ContentType.PDF) else request.id,
                "id": request.id,
                "type": request.type.value
            }
        ]

        return self.embedding_dao.store_embedding(metadatas, embedding, content, request.id)

    def generate_embedding(self, text):
        # Generate embeddings using OpenAI's `text-embedding-ada-002`
        response = self.embedding_function.embed_query(text)
        return response

    def create_chain(self, conversation_id: str) -> tuple[str, LLMChain]:
        """Create a new chain with conversation-specific memory"""
        conversation_id, memory = self.memory_service.get_memory(conversation_id)
        chain = LLMChain(
            llm=self.chat_model,
            prompt=self.get_system_prompt(),
            memory=memory,
            verbose=False
        )
        return conversation_id, chain

    def _get_vectorstore(self) -> Chroma:
        """Get Chroma vectorstore for current collection"""
        from app.utils.context import get_index_name
        collection_name = get_index_name()
        
        vectorstore = Chroma(
            client=self.chroma_client,
            collection_name=collection_name,
            embedding_function=self.embedding_function
        )
        
        return vectorstore

    def _process_retrieved_documents(self, docs):
        """
        Process retrieved documents and extract context and sources.
        
        Args:
            docs: List of retrieved documents
            
        Returns:
            tuple: (combined_context, sources)
        """
        context_parts = []
        sources = []
        
        for doc in docs:
            context_parts.append(doc.page_content)
            
            metadata = doc.metadata
            source_url = metadata.get('url', 'N/A')
            
            similarity = metadata.get('similarity', 'N/A')
            if similarity == 'N/A' and 'score' in metadata:
                similarity = f"{(1 - metadata['score']):.2%}" if metadata['score'] else 'N/A'
            
            sources.append({
                'url': source_url,
                'similarity': similarity,
                'type': metadata.get('type', 'N/A'),
                'id': metadata.get('id', source_url)
            })

        return ' '.join(context_parts), sources

    def retrieve_answer(self, user_input: str, conversation_id: Optional[str] = None):
        # Get vectorstore for current collection
        retriever = self._get_vectorstore().as_retriever(search_kwargs={"k": 2})
        
        # Get relevant documents
        docs = retriever.get_relevant_documents(user_input)

        # Process documents using the new method
        combined_context, sources = self._process_retrieved_documents(docs)
        
        # Truncate context if too long (approximate token limit)
        max_chars = 40000  # Approximate character limit (~10k tokens)
        if len(combined_context) > max_chars:
            combined_context = combined_context[:max_chars] + "..."

        # Create chain with conversation memory
        conversation_id, chain = self.create_chain(conversation_id)

        #memory_context = " ".join(chat_history)

        # Run the chain
        response = chain.run(
            context=combined_context,
            input=user_input
        )

        self.memory_service.save_memory(conversation_id, chain.memory)

        chat_history = self.memory_service.get_chat_history(conversation_id)
        
        return {
            "conversation_id": conversation_id,
            "answer": response,
            "sources": sources,
            "metadata": {
                "total_sources": len(sources),
                "model_used": "gpt-4o",
                "context_length": len(combined_context),
                "chat_history": chat_history
            }
        }

    def delete_collection(self, collection_name: str) -> bool:
        return self.embedding_dao.delete_collection(collection_name)

    def delete_document(self, doc_id: str) -> bool:
        """Delete a specific document by ID"""
        return self.embedding_dao.delete_document(doc_id)

    def clear_memory(self, conversation_id: str):
        """Clear the conversation history"""
        self.memory_service.clear_memory(conversation_id)