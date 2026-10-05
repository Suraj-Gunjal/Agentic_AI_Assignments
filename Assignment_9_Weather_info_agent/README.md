# Weather AI Agent

Complete Agentic AI assignment using FastAPI, Open-Meteo and optional Ollama.

## Run on Windows
```bash
python -m venv venv
venv\\Scripts\\activate
pip install -r requirements.txt
```

Optional local LLM:
```bash
ollama pull gemma3:4b
ollama serve
```

Start:
```bash
uvicorn app.main:app --reload
```

Open http://127.0.0.1:8000

The agent resolves a natural-language location with Open-Meteo geocoding, calls the live forecast API, and uses Ollama to turn structured weather data into an AI brief. If Ollama is unavailable, a fallback summary keeps the application functional.
