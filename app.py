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

# Step 1: Fetch Python docs
url = "https://docs.python.org/3/library/functions.html"
response = requests.get(url)
soup = BeautifulSoup(response.text, "html.parser")
text = soup.get_text()

# Step 2: Chunk text
chunk_size = 300
import re
def clean_text(text):
    # Remove stray encoding chars and excessive whitespace
    text = text.replace("\xa0", " ").replace("Â¶", "")
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def chunk_text(text, chunk_size=300):
    chunks = [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]
    return [clean_text(chunk) for chunk in chunks]
chunks = chunk_text(text, chunk_size)

# Step 3: Embeddings
model = SentenceTransformer("all-MiniLM-L6-v2")
embeddings = model.encode(chunks)

# Step 4: Store in Chroma
client = chromadb.Client(Settings(anonymized_telemetry=False))
collection = client.create_collection("python_docs")
for i, emb in enumerate(embeddings):
    collection.add(documents=[chunks[i]], embeddings=[emb.tolist()], ids=[str(i)])

# Step 4b: Store in FAISS
faiss_index = faiss.IndexFlatL2(embeddings.shape[1])
faiss_index.add(np.array(embeddings))

@app.route('/query', methods=['POST'])
def query():
    data = request.get_json()
    query_text = data.get('query', '')
    query_emb = model.encode([query_text])[0]
    # Chroma search
    chroma_results = collection.query(query_embeddings=[query_emb.tolist()], n_results=2)
    # FAISS search
    D, I = faiss_index.search(np.array([query_emb]), k=2)
    faiss_chunks = [chunks[idx] for idx in I[0]]
    # Clean up results for readability
    chroma_clean = [clean_text(c) for c in chroma_results['documents'][0]]
    faiss_clean = [clean_text(f) for f in faiss_chunks]
    return jsonify({
        'chroma': chroma_clean,
        'faiss': faiss_clean
    })

if __name__ == '__main__':
    app.run(debug=True)
