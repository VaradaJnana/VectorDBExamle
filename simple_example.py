import numpy as np
from sentence_transformers import SentenceTransformer
import faiss
import chromadb
from chromadb.config import Settings

# Sample data and chunking
def chunk_text(text, chunk_size=50):
    return [text[i:i+chunk_size] for i in range(0, len(text), chunk_size)]

text = "Vector databases are used for similarity search and retrieval in AI applications. This example demonstrates chunking and storing text in FAISS and Chroma."
chunks = chunk_text(text)

# Generate embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')
embeddings = model.encode(chunks)

# FAISS Example
faiss_index = faiss.IndexFlatL2(embeddings.shape[1])
faiss_index.add(np.array(embeddings))
faiss_results = faiss_index.search(np.array([embeddings[0]]), k=3)
print("FAISS Results:", faiss_results)

# Chroma Example
client = chromadb.Client(Settings(anonymized_telemetry=False))
collection = client.create_collection(name="demo")
for i, emb in enumerate(embeddings):
    collection.add(documents=[chunks[i]], embeddings=[emb.tolist()], ids=[str(i)])
chroma_results = collection.query(query_embeddings=[embeddings[0].tolist()], n_results=3)
print("Chroma Results:", chroma_results)
