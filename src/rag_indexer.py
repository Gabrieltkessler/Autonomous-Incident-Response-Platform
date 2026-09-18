import os
import faiss
import glob
from typing import List, Dict
from sentence_transformers import SentenceTransformer

class RunbookVectorStore:
    """Indexes engineering runbooks into a local FAISS vector store for semantic retrieval."""
    
    def __init__(self, runbook_dir: str = "data/runbooks"):
        self.runbook_dir = runbook_dir
        # Load lightweight local embedding model
        self.embedder = SentenceTransformer("all-MiniLM-L6-v2")
        self.documents: List[Dict[str, str]] = []
        self.index = None

    def load_and_index_runbooks(self):
        """Reads markdown runbooks, generates embeddings, and populates FAISS index."""
        md_files = glob.glob(os.path.join(self.runbook_dir, "*.md"))
        
        if not md_files:
            raise FileNotFoundError(f"No runbooks found in {self.runbook_dir}")

        for filepath in md_files:
            with open(filepath, "r", encoding="utf-8") as f:
                content = f.read()
                filename = os.path.basename(filepath)
                self.documents.append({"source": filename, "content": content})

        # Generate embeddings for all runbooks
        contents = [doc["content"] for doc in self.documents]
        embeddings = self.embedder.encode(contents, convert_to_numpy=True)

        # Initialize FAISS vector index (384 dimensions for all-MiniLM-L6-v2)
        dimension = embeddings.shape[1]
        self.index = faiss.IndexFlatL2(dimension)
        self.index.add(embeddings)
        
        print(f"Successfully indexed {len(self.documents)} runbooks into FAISS.")

    def search(self, query: str, top_k: int = 1) -> List[Dict[str, str]]:
        """Searches FAISS vector store for the most relevant runbook matching the query."""
        if self.index is None:
            raise ValueError("Index is empty. Call load_and_index_runbooks() first.")

        query_vector = self.embedder.encode([query], convert_to_numpy=True)
        distances, indices = self.index.search(query_vector, top_k)

        results = []
        for idx in indices[0]:
            if idx < len(self.documents):
                results.append(self.documents[idx])
        return results

if __name__ == "__main__":
    store = RunbookVectorStore()
    store.load_and_index_runbooks()

    # Query using extracted entities from our earlier log parser
    test_query = "HTTP 500 failure route /api/v1/checkout database cluster timeout"
    results = store.search(test_query, top_k=1)

    print("\n--- RAG Vector Search Result ---")
    print(f"Matched Source: {results[0]['source']}")
    print("\nMatched Document Content:")
    print(results[0]['content'])