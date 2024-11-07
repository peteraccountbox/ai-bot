# services/embedding_service.py

from app.utils.scraping_utils import WebScraper
from openai import OpenAI
from app.dao.embedding_dao import EmbeddingDAO
from app.models.schemas import TrainRequest, ContentType
from typing import Optional
from app.utils.file_extractor import FileExtractor

class EmbeddingService:
    def __init__(self):
        self.client = OpenAI()
        self.embedding_dao = EmbeddingDAO()
        self.scraper = WebScraper()
        self.file_extractor = FileExtractor()

    async def process_payload(self, request: TrainRequest):
        # Get content
        if request.type == ContentType.URL:
            content = self.scraper.scrape_url(request.content)
        elif request.type == ContentType.FILE:
            content = await self.file_extractor.extract_text_from_url(request.content)
        else:
            content = self.scraper.extract_text_from_html(request.content)
    
        print(content)

        # Generate embedding
        embedding = self.generate_embedding(content)
        
        # Store metadata
        metadatas = [
            {
                "url": request.content if request.type in (ContentType.URL, ContentType.FILE) else request.id,
                "id": request.id,
                "type": request.type.value
            }
        ]

        return self.embedding_dao.store_embedding(metadatas, embedding, content, request.id)

    def generate_embedding(self, text):
        # Generate embeddings using OpenAI's `text-embedding-ada-002`
        response = self.client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding

    def retrieve_answer(self, user_input: str):
        user_embedding = self.generate_embedding(user_input)
        results = self.embedding_dao.query_embedding(user_embedding, n_results=10)

        # Get both documents and metadata
        documents = results.get('documents', [[]])[0]
        metadatas = results.get('metadatas', [[]])[0]
        distances = results.get('distances', [[]])[0] if 'distances' in results else []

        # Combine documents with their sources
        context_parts = []
        sources = []
        
        for doc, meta, dist in zip(documents, metadatas, distances):
            source_url = meta.get('url', 'N/A') if meta else 'N/A'
            similarity = 1 - dist if dist else 0
            
            # Add to context with source reference
            context_parts.append(f"{doc}")
            # Keep track of sources
            sources.append({
                'url': source_url,
                'similarity': f"{similarity:.2%}"
            })

        combined_context = ' '.join(context_parts)

        response = self.client.chat.completions.create(
            model="gpt-4o",
            messages = [
                    {
                        "role": "system",
                        "content": (
                               "You're EngageBay's CRM assistant: Start with a brief intro (5-10 words), then use concise bullet points (max 2 sentences each) based only on provided context. Reply in the question's language or default to English."
                        )
                    },
                    {
                        "role": "user",
                        "content": (
                            f"Context: {combined_context}\n\n"
            f"Question: {user_input}\n\n"
            "Answer using only the context, in the same language."
                        )
                    }
            ],
            temperature=0.7,
            #max_tokens=3
        )

        return {
            "answer": response.choices[0].message.content.strip(),    
            "sources": sources,
            "metadata": {
                "total_sources": len(sources),
                "model_used": "gpt-4o",
                "context_length": len(combined_context)
            }
        }

    def delete_collection(self, collection_name: str) -> bool:
        return self.embedding_dao.delete_collection(collection_name)

    def delete_document(self, doc_id: str) -> bool:
        """Delete a specific document by ID"""
        return self.embedding_dao.delete_document(doc_id)