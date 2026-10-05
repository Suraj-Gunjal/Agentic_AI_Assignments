import json
import os
import re
from typing import TypedDict

from dotenv import load_dotenv
from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END

from .memory import PersistentMemory

load_dotenv()


class MemoryAgentState(TypedDict, total=False):
    user_message: str
    candidate_memory: str
    should_store: bool
    category: str
    importance: float
    retrieved_memories: list[str]
    answer: str
    memory_stored: bool


class ProductivityMemoryAgent:
    def __init__(self):
        self.memory = PersistentMemory()

        self.llm = ChatOllama(
            model=os.getenv("OLLAMA_MODEL", "llama3.2:3b"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            temperature=0,
        )

        self.graph = self._build_graph()

    def _parse_json(self, text: str) -> dict:
        text = text.strip()

        # Remove common markdown code fences.
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)

        start = text.find("{")
        if start == -1:
            raise ValueError("No JSON object found.")

        decoder = json.JSONDecoder()
        data, _ = decoder.raw_decode(text[start:])
        return data

    def _heuristic_memory(self, message: str) -> dict:
        """Reliable fallback for common student-memory statements."""
        text = message.strip()
        lower = text.lower()

        # Never store obvious questions or commands.
        question_words = (
            "what ", "why ", "how ", "when ", "where ", "which ",
            "who ", "can you ", "do you ", "did you ", "tell me "
        )
        if lower.startswith(question_words):
            return {
                "should_store": False,
                "memory": "",
                "category": "important_fact",
                "importance": 0.0,
            }

        # Project statements.
        project_match = re.search(
            r"(?:i am|i'm|i am currently)\s+"
            r"(?:building|developing|working on)\s+(?:a\s+|an\s+)?(.+?)(?:[.!?]|$)",
            text,
            re.IGNORECASE,
        )
        if project_match:
            project = project_match.group(1).strip()
            return {
                "should_store": True,
                "memory": f"User is building {project}.",
                "category": "project",
                "importance": 0.95,
            }

        # Preference statements.
        preference_match = re.search(
            r"(?:i prefer|i like|i usually|i generally)\s+(.+?)(?:[.!?]|$)",
            text,
            re.IGNORECASE,
        )
        if preference_match:
            preference = preference_match.group(1).strip()
            return {
                "should_store": True,
                "memory": f"User prefers {preference}.",
                "category": "study_preference" if any(
                    x in lower for x in ["study", "studying", "learn", "learning"]
                ) else "personal_preference",
                "importance": 0.9,
            }

        # Goal statements.
        goal_match = re.search(
            r"(?:my goal is to|i want to|i'm trying to|i am trying to)\s+(.+?)(?:[.!?]|$)",
            text,
            re.IGNORECASE,
        )
        if goal_match:
            goal = goal_match.group(1).strip()
            return {
                "should_store": True,
                "memory": f"User wants to {goal}.",
                "category": "skill_goal",
                "importance": 0.9,
            }

        # Explicit memory commands.
        explicit = re.search(
            r"(?:add this in memory|remember that|remember this)\s*[-:]*\s*(.+)",
            text,
            re.IGNORECASE,
        )
        if explicit:
            memory = explicit.group(1).strip()
            return {
                "should_store": bool(memory),
                "memory": memory,
                "category": "important_fact",
                "importance": 0.85,
            }

        return {
            "should_store": False,
            "memory": "",
            "category": "important_fact",
            "importance": 0.0,
        }

    def _extract_memory(self, state: MemoryAgentState):
        message = state["user_message"]

        prompt = f"""
You are a long-term memory extraction agent for a student productivity assistant.

Decide whether the user's message contains information worth remembering across
future conversations.

Useful memories include:
- long-term projects
- study or working preferences
- recurring routines
- long-term learning goals
- stable preferences
- important non-sensitive facts

Do NOT store:
- questions
- greetings
- temporary requests
- ordinary conversational filler
- passwords, secrets, financial details, or sensitive personal information
- vague fragments with no useful meaning

Examples:

User: I am building a flood prediction project.
Output:
{{"should_store": true, "memory": "User is building a flood prediction project.", "category": "project", "importance": 0.95}}

User: I prefer studying DSA in the morning.
Output:
{{"should_store": true, "memory": "User prefers studying DSA in the morning.", "category": "study_preference", "importance": 0.9}}

User: What project am I building?
Output:
{{"should_store": false, "memory": "", "category": "important_fact", "importance": 0}}

Return ONLY one JSON object.

User message:
{message}
"""

        try:
            result = self.llm.invoke(prompt)
            data = self._parse_json(result.content)

            should_store = bool(data.get("should_store", False))
            candidate = str(data.get("memory", "")).strip()

            if should_store and candidate:
                state["should_store"] = True
                state["candidate_memory"] = candidate
                state["category"] = str(
                    data.get("category", "important_fact")
                )
                state["importance"] = float(
                    data.get("importance", 0.8)
                )
                return state

        except Exception:
            pass

        # Deterministic fallback makes the project reliable even when the
        # local model returns malformed JSON or is temporarily unavailable.
        fallback = self._heuristic_memory(message)
        state["should_store"] = fallback["should_store"]
        state["candidate_memory"] = fallback["memory"]
        state["category"] = fallback["category"]
        state["importance"] = fallback["importance"]

        return state

    def _store_memory(self, state: MemoryAgentState):
        stored = False

        if state.get("should_store") and state.get("candidate_memory"):
            stored = self.memory.add(
                state["candidate_memory"],
                category=state.get("category", "important_fact"),
                importance=state.get("importance", 0.8),
            )

        state["memory_stored"] = stored
        return state

    def _retrieve_memory(self, state: MemoryAgentState):
        state["retrieved_memories"] = self.memory.search(
            state["user_message"],
            k=6,
        )
        return state

    def _generate_answer(self, state: MemoryAgentState):
        memories = state.get("retrieved_memories", [])

        if memories:
            memory_text = "\n".join(
                f"- {memory}" for memory in memories
            )
        else:
            memory_text = "No relevant memories were found."

        prompt = f"""
You are a helpful student productivity assistant with persistent long-term memory.

User message:
{state["user_message"]}

Relevant memories retrieved from the memory database:
{memory_text}

Answer the user's question naturally.

Rules:
1. Use retrieved memories when they are relevant.
2. If the user asks what they remember, summarize the relevant memories.
3. If a memory directly answers the question, state it clearly.
4. Never invent a memory.
5. If no relevant memory exists, say that you do not have enough information.
6. Do not mention vector databases, embeddings, retrieval scores, or internal implementation.
7. Keep the answer concise and student-friendly.
"""

        try:
            result = self.llm.invoke(prompt)
            state["answer"] = result.content.strip()
        except Exception:
            # Useful deterministic fallback if the LLM temporarily fails.
            if memories:
                state["answer"] = (
                    "I found these relevant memories:\n"
                    + "\n".join(f"• {m}" for m in memories)
                )
            else:
                state["answer"] = (
                    "I don't have enough relevant information in my memory "
                    "to answer that yet."
                )

        return state

    def _build_graph(self):
        graph = StateGraph(MemoryAgentState)

        graph.add_node("extract_memory", self._extract_memory)
        graph.add_node("store_memory", self._store_memory)
        graph.add_node("retrieve_memory", self._retrieve_memory)
        graph.add_node("generate_answer", self._generate_answer)

        graph.add_edge(START, "extract_memory")
        graph.add_edge("extract_memory", "store_memory")
        graph.add_edge("store_memory", "retrieve_memory")
        graph.add_edge("retrieve_memory", "generate_answer")
        graph.add_edge("generate_answer", END)

        return graph.compile()

    def chat(self, message: str):
        return self.graph.invoke({
            "user_message": message.strip()
        })
