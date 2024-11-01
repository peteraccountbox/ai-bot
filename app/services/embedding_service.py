# services/embedding_service.py

import requests
import os
from bs4 import BeautifulSoup
from openai import OpenAI
from app.dao.embedding_dao import EmbeddingDAO

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class EmbeddingService:
    def __init__(self):
        self.embedding_dao = EmbeddingDAO()

    def scrape_text(self, url):
        # Scrape and parse text content from a URL
        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')
        text = ' '.join(p.get_text() for p in soup.find_all('p'))
        return text

    def generate_embedding(self, text):
        # Generate embeddings using OpenAI's `text-embedding-ada-002`
        response = client.embeddings.create(
            model="text-embedding-ada-002",
            input=text
        )
        return response.data[0].embedding

    def store_url_content(self, url):
        # Scrape text, generate embedding, and store in ChromaDB
        content = self.scrape_text(url)
        embedding = self.generate_embedding(content)
        self.embedding_dao.store_embedding(url, embedding, content)

    def retrieve_answer(self, user_input):
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

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You're EngageBay's CRM assistant. Answer in bullet points, max 2 sentences per point."},
                {"role": "user", "content": f"Context: {combined_context}\n\nQuestion: {user_input}\n\nAnswer from context only."}
            ],
            temperature=0.7,
            #max_tokens=3
        )

        # Return both the answer and sources
        return {
            "answer": response.choices[0].message.content.strip(),
            "sources": sources,
            "metadata": {
                "total_sources": len(sources),
                "model_used": "gpt-4",
                "context_length": len(combined_context)
            }
        }