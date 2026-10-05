import hashlib
import os
import re
from pathlib import Path

from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = BASE_DIR / "data" / "chroma"
CHROMA_DIR.mkdir(parents=True, exist_ok=True)


class PersistentMemory:
    """Persistent ChromaDB memory with semantic + keyword retrieval."""

    def __init__(self):
        self.embeddings = OllamaEmbeddings(
            model=os.getenv("OLLAMA_EMBED_MODEL", "nomic-embed-text"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
        )

        self.store = Chroma(
            collection_name="student_productivity_memory_v2",
            embedding_function=self.embeddings,
            persist_directory=str(CHROMA_DIR),
        )

    def _memory_id(self, memory: str) -> str:
        return hashlib.sha256(memory.strip().lower().encode()).hexdigest()

    def _tokens(self, text: str) -> set[str]:
        return set(re.findall(r"[a-zA-Z0-9]+", text.lower()))

    def add(self, memory: str, category: str = "important_fact", importance: float = 0.8):
        memory = memory.strip()
        if not memory:
            return False

        existing = self.all_records()
        normalized = memory.lower()

        for record in existing:
            if record["memory"].strip().lower() == normalized:
                return False

        self.store.add_texts(
            texts=[memory],
            ids=[self._memory_id(memory)],
            metadatas=[{
                "type": "long_term_memory",
                "category": category,
                "importance": float(importance),
            }],
        )
        return True

    def search(self, query: str, k: int = 6) -> list[str]:
        """Combine semantic retrieval with lexical/category matching."""
        if not query.strip():
            return []

        records = self.all_records()
        if not records:
            return []

        # Semantic search from ChromaDB.
        semantic_scores = {}
        try:
            results = self.store.similarity_search_with_score(query, k=min(k, len(records)))
            for doc, distance in results:
                semantic_scores[doc.page_content] = 1.0 / (1.0 + float(distance))
        except Exception:
            semantic_scores = {}

        query_tokens = self._tokens(query)
        q = query.lower()

        ranked = []

        for record in records:
            memory = record["memory"]
            memory_tokens = self._tokens(memory)

            overlap = len(query_tokens & memory_tokens)
            lexical_score = overlap / max(len(query_tokens), 1)

            # Give useful category boosts for natural questions.
            category = record["category"]
            category_boost = 0.0

            if any(word in q for word in ["project", "building", "build", "developing", "working on"]):
                if category == "project":
                    category_boost += 0.45

            if any(word in q for word in ["study", "studying", "morning", "learn", "learning"]):
                if category in {"study_preference", "skill_goal"}:
                    category_boost += 0.35

            if any(word in q for word in ["goal", "improve", "skill"]):
                if category == "skill_goal":
                    category_boost += 0.35

            semantic = semantic_scores.get(memory, 0.0)

            # Importance helps stable long-term facts without dominating retrieval.
            importance = float(record.get("importance", 0.8))
            score = (
                0.50 * semantic
                + 0.35 * lexical_score
                + category_boost
                + 0.05 * importance
            )

            ranked.append((score, memory))

        ranked.sort(key=lambda item: item[0], reverse=True)

        return [memory for score, memory in ranked[:k]]

    def all_records(self) -> list[dict]:
        data = self.store.get(
            include=["documents", "metadatas"]
        )

        documents = data.get("documents") or []
        metadatas = data.get("metadatas") or []

        records = []
        for i, document in enumerate(documents):
            metadata = metadatas[i] if i < len(metadatas) else {}
            records.append({
                "memory": document,
                "category": metadata.get("category", "important_fact"),
                "importance": metadata.get("importance", 0.8),
            })

        return records

    def all_memories(self, limit: int = 100) -> list[str]:
        return [r["memory"] for r in self.all_records()[:limit]]

    def clear(self):
        data = self.store.get()
        ids = data.get("ids") or []

        if ids:
            self.store.delete(ids=ids)
