# Vector Database Example

This project demonstrates how to chunk text, generate embeddings, and store them in FAISS and Chroma vector databases for similarity search.

## Features
- Text chunking
- Embedding generation using Sentence Transformers
- Storing and searching with FAISS
- Storing and searching with Chroma

## Usage
1. (Recommended) Set up a virtual environment:
   ```bash
   python -m venv .venv
   source .venv/Scripts/activate  # On Windows
   # Or use: source .venv/bin/activate  # On macOS/Linux
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the example:
   ```bash
   python app.py
   ```
