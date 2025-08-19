from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
from bs4 import BeautifulSoup
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings
import faiss
import numpy as np

app = Flask(__name__)
CORS(app)


# Utility functions
import re
def clean_text(text):
    text = text.replace("\xa0", " ").replace("Â¶", "")
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def chunk_text(text, chunk_size=300):
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    return [clean_text(chunk) for chunk in chunks]

# Model and DB cache
model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.Client(Settings(anonymized_telemetry=False))
collection = None
faiss_index = None
chunks = None

def process_docs():
    global collection, faiss_index, chunks
    url = "https://docs.python.org/3/library/functions.html"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    text = soup.get_text()
    chunk_size = 300
    chunks = chunk_text(text, chunk_size)
    embeddings = model.encode(chunks)
    # Chroma
    collection = client.create_collection("python_docs")
    for i, emb in enumerate(embeddings):
        collection.add(documents=[chunks[i]], embeddings=[emb.tolist()], ids=[str(i)])
    # FAISS
    faiss_index = faiss.IndexFlatL2(embeddings.shape[1])
    faiss_index.add(np.array(embeddings))

@app.route('/query', methods=['POST'])
def query():
    global collection, faiss_index, chunks
    data = request.get_json()
    query_text = data.get('query', '')
    # Lazy load and process docs on first query
    if collection is None or faiss_index is None or chunks is None:
        process_docs()
    query_emb = model.encode([query_text])[0]
    # Chroma search
    chroma_results = collection.query(query_embeddings=[query_emb.tolist()], n_results=2)
    # FAISS search
    D, I = faiss_index.search(np.array([query_emb]), k=2)
    faiss_chunks = [chunks[idx] for idx in I[0]]
    chroma_clean = [clean_text(c) for c in chroma_results['documents'][0]]
    faiss_clean = [clean_text(f) for f in faiss_chunks]
    return jsonify({
        'chroma': chroma_clean,
        'faiss': faiss_clean
    })

import os

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
