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
- Qdrant running instance
- pip (Python package manager)

## Installation

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