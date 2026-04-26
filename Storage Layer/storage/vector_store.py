"""
Vector Store - Manages embeddings and semantic search using FAISS.
"""

import os
from typing import Dict, List, Tuple

import faiss
import numpy as np

import config


class VectorStore:
    """
    Manages vector embeddings for semantic memory retrieval.
    Uses FAISS for fast similarity search.
    """

    def __init__(self, llm_client):
        test_embedding = llm_client.embed("dimension test")
        self.dimension = len(test_embedding)
        self.index = faiss.IndexFlatL2(self.dimension)
        self.id_to_index: Dict[str, int] = {}
        self.index_to_id: Dict[int, str] = {}
        self.vectors: Dict[str, List[float]] = {}

        if config.DEBUG:
            print(f"Vector store initialized (dimension: {self.dimension})")

    def add(self, memory_id: str, embedding: List[float]):
        if not embedding or len(embedding) != self.dimension:
            if config.DEBUG:
                print(f"Invalid embedding dimension for {memory_id}")
            return
        self.vectors[memory_id] = embedding
        self._rebuild_from_vectors()

    def search(self, query_embedding: List[float], k: int = 10):
        if not query_embedding or len(query_embedding) != self.dimension:
            if config.DEBUG:
                print("Invalid query embedding")
            return []
        if self.index.ntotal == 0:
            return []

        query_vector = np.array([query_embedding], dtype=np.float32)
        k = min(k, self.index.ntotal)
        distances, indices = self.index.search(query_vector, k)

        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx in self.index_to_id:
                memory_id = self.index_to_id[idx]
                similarity = 1 / (1 + float(dist))
                results.append((memory_id, similarity))
        return results

    def remove(self, memory_id: str):
        if memory_id not in self.vectors:
            return
        del self.vectors[memory_id]
        self._rebuild_from_vectors()

    def rebuild(self, memories: List[Tuple[str, List[float]]]):
        self.vectors = {
            memory_id: embedding
            for memory_id, embedding in memories
            if embedding and len(embedding) == self.dimension
        }
        self._rebuild_from_vectors()

    def save(self, filepath: str):
        try:
            faiss.write_index(self.index, filepath)
            meta_path = f"{filepath}.meta.json"
            with open(meta_path, "w", encoding="utf-8") as f:
                import json
                json.dump({"vectors": self.vectors}, f)
        except Exception as e:
            print(f"Error saving index: {e}")

    def load(self, filepath: str):
        if not os.path.exists(filepath):
            return
        try:
            self.index = faiss.read_index(filepath)
            self.dimension = self.index.d
            meta_path = f"{filepath}.meta.json"
            if os.path.exists(meta_path):
                import json
                with open(meta_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.vectors = data.get("vectors", {})
            self._rebuild_from_vectors()
        except Exception as e:
            print(f"Error loading index: {e}")

    def get_stats(self) -> dict:
        return {
            "total_vectors": self.index.ntotal,
            "dimension": self.dimension,
            "memory_count": len(self.vectors),
        }

    def _rebuild_from_vectors(self):
        self.index = faiss.IndexFlatL2(self.dimension)
        self.id_to_index = {}
        self.index_to_id = {}
        if not self.vectors:
            return

        matrix = np.array(list(self.vectors.values()), dtype=np.float32)
        ids = list(self.vectors.keys())
        self.index.add(matrix)
        for idx, memory_id in enumerate(ids):
            self.id_to_index[memory_id] = idx
            self.index_to_id[idx] = memory_id
