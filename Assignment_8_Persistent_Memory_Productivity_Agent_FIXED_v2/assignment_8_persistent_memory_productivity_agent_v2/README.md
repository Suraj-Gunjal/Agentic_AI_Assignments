# Assignment 8 — Persistent Memory Productivity Agent

## LangGraph + ChromaDB + Ollama

This project implements a student productivity assistant with persistent
long-term memory.

The agent can:

- extract useful long-term information from user messages
- classify memories into useful categories
- store memories permanently in ChromaDB
- retrieve memories using semantic and keyword matching
- use retrieved memories to answer future questions
- continue working after restarting the application

## Architecture

```text
                         USER MESSAGE
                              |
                              v
                    +-------------------+
                    | Memory Extraction |
                    |     LangGraph     |
                    +---------+---------+
                              |
                              v
                     Store if useful
                              |
                              v
                    +-------------------+
                    | Persistent Memory |
                    |     ChromaDB      |
                    +---------+---------+
                              |
                              v
                    Hybrid Memory Search
                    /                 \
             Semantic Search      Keyword/
              Embeddings          Category Match
                    \                 /
                     +-------+-------+
                             |
                             v
                     Relevant Memories
                             |
                             v
                    +-------------------+
                    |   Ollama LLM      |
                    | Answer Generation |
                    +---------+---------+
                              |
                              v
                            USER
```

## Technologies

- LangGraph — agent workflow/state graph
- ChromaDB — persistent vector database
- Ollama — local LLM and embedding models
- Streamlit — web interface

## 1. Create virtual environment

Windows:

```bash
python -m venv .venv
.venv\Scripts\activate
```

## 2. Install packages

```bash
pip install -r requirements.txt
```

## 3. Install Ollama models

```bash
ollama pull llama3.2:3b
ollama pull nomic-embed-text
```

Check:

```bash
ollama list
```

You should see both models.

If Ollama is already running, do NOT run `ollama serve` again.

## 4. Start the application

```bash
streamlit run app.py
```

Open:

```text
http://localhost:8501
```

## Demonstration

First enter:

```text
I prefer studying DSA in the morning.
```

Then:

```text
I am building a flood prediction project.
```

Then:

```text
My goal is to improve Java problem solving.
```

Then:

```text
I prefer simple project documentation.
```

Now ask:

```text
What project am I building?
```

Expected answer:

```text
You are building a flood prediction project.
```

Also try:

```text
What do you remember about my study preferences?
What should I work on in the morning?
What am I trying to improve?
How do I prefer my project documentation?
```

## Why this version is more reliable

The original simple memory agent depended almost entirely on semantic vector search.

This version combines:

1. ChromaDB semantic similarity
2. keyword overlap
3. memory categories
4. importance
5. deterministic memory extraction fallback
6. duplicate detection

Therefore a query such as:

```text
What project am I building?
```

can still retrieve:

```text
User is building a flood prediction project.
```

even when pure embedding similarity is not strong enough.

## Important

This project is completely local after the Ollama models are downloaded.

No paid cloud API is required.

`data/chroma/` contains the persistent local memory database.

Deleting that folder resets the persistent memory.
