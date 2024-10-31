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
        # Generate embedding for user input and query ChromaDB for top 10 results
        user_embedding = self.generate_embedding(user_input)
        #print(user_embedding)

        results = self.embedding_dao.query_embedding(user_embedding, n_results=10)
        #print("Query result:", results)  # Add this temporarily to see the structure

        # Get documents from the raw response
        documents = results.get('documents', [[]])[0]
        combined_context = ' '.join(documents)
       
        print(combined_context)

        #text-davinci-003
        #gpt-4o-mini
        #gpt-4
        # Use OpenAI's language model to generate an answer
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that answers questions based on the provided context."},
                {"role": "user", "content": f"Context: {combined_context}\n\nQuestion: {user_input}\n\nAnswer the question based only on the provided context."}
            ],
            temperature=0.7,
            max_tokens=300
        )
        return response.choices[0].message.content.strip()