# Atelier AI — Premium Multi-Agent Blog Studio

A Streamlit UI for a LangGraph research → review → write → review → edit workflow.

## Setup

```bash
pip install -r requirements.txt
cp .env.example .env
```

Replace the placeholder in `.env` with your Groq API key. On Windows, copy `.env.example` to `.env` manually or use `copy .env.example .env`.

```bash
streamlit run app.py
```

## Notes
- Research and draft review are powered by LangGraph interrupts and resumed with `Command`.
- The graph uses an in-memory checkpointer: projects do not survive server restarts.
- Research revisions are not capped; draft revisions are capped at three.
- The supplied `agent.py` uses `openai/gpt-oss-20b` through Groq. Check your account's model access.
- No API keys should be committed to GitHub.
