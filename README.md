# AI Bot Project

A conversational AI bot that can process various types of content, generate embeddings, and provide contextual responses.

## Features

- Content Processing:
  - URL Scraping: Extract content from web pages
  - File Processing: Support for files hosted at URLs (PDF, DOCX, etc.)
  - Direct Text Input: Process raw text content

- Embedding Generation:
  - Uses OpenAI's `text-embedding-ada-002` model
  - Stores embeddings with metadata for easy retrieval
  - Supports similarity search for relevant context

## API Endpoints

### Train Endpoint
Train the bot with new content:
```json
POST /train
{
    "type": "URL|FILE|TEXT",
    "content": "URL or text content",
    "title": "Unique title for the content"
}
```

- `type`: Content type (URL, FILE, or TEXT)
- `content`: URL, file path, or raw text content
- `title`: Unique title for the content

## Prerequisites

- Python 3.10+
- OpenAI API key
- Docker (for running Qdrant)
- pip (Python package manager)

## Installation & Setup

1. Clone the repository:
```bash
git clone https://github.com/yourusername/AIBotProject.git
cd AIBotProject
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Start Qdrant using Docker:
```bash
docker pull qdrant/qdrant
docker run -p 6333:6333 -p 6334:6334 \
    -v $(pwd)/qdrant_storage:/qdrant/storage \
    qdrant/qdrant
```

5. Set up environment variables:
```bash
# Create .env file
cp .env.example .env

# Edit .env with your values:
OPENAI_API_KEY=your_api_key
QDRANT_HOST=localhost
QDRANT_PORT=6333
```

6. Start the FastAPI server:
```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at: http://localhost:8000
Swagger documentation: http://localhost:8000/docs

## Development Setup

For development, additional tools are recommended:
```bash
pip install pytest pytest-asyncio black isort flake8
```

Run tests:
```bash
pytest
```

Format code:
```bash
black .
isort .
flake8
```

## Database Management

### Qdrant Collections

The project uses Qdrant vector database. Collections are automatically created on startup, but you can manually manage them:

```python
from qdrant_client import QdrantClient

client = QdrantClient("localhost", port=6333)

# Create collection
client.create_collection(
    collection_name="documents",
    vectors_config={
        "size": 1536,  # OpenAI embedding dimension
        "distance": "Cosine"
    }
)

# List collections
client.get_collections()

# Delete collection
client.delete_collection(collection_name="documents")
```

### Backup & Restore

Backup Qdrant data:
```bash
# Stop the container
docker stop qdrant_container

# Backup the storage directory
cp -r qdrant_storage qdrant_backup

# Restart the container
docker start qdrant_container
```

## Project Structure

```
AIBotProject/
├── app/
│   ├── __init__.py
│   ├── main.py
│   └── services.py
├── .gitignore
├── README.md
└── requirements.txt
```

## Usage

[Add specific instructions on how to run and use your bot]

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## License

[Choose and specify your license]

## Contact

[Your Name] - [Your Email]

Project Link: [https://github.com/yourusername/AIBotProject](https://github.com/yourusername/AIBotProject)
```

You can customize this template by:
1. Adding specific details about your bot's functionality
2. Including any special configuration requirements
3. Adding screenshots or examples
4. Specifying the exact Python version requirements
5. Adding any API keys or environment variables needed
6. Including troubleshooting guides

Would you like me to expand on any particular section?