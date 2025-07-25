## Got the data from "Trouble with the Curve"

https://github.com/jacobdanovitch/Trouble-With-The-Curve

# ⚾ ScoutBot

Minimal, production-ready **Retrieval-Augmented Generation (RAG)** chatbot that answers questions about baseball scouting reports (2013 – 2019).  
Front-end built with **Streamlit**, back-end powered by **OpenAI GPT-4o** + **Pinecone** vector search.

<p align="center">
  <img src="https://user-images.githubusercontent.com/..." width="600" alt="ScoutBot screenshot">
</p>

---

## ✨ Features

| Feature | Details |
|---------|---------|
| ⚡ **Fast answers** | RAG pipeline narrows context to just the relevant report chunks (top-K similarity search). |
| 🧠 **Grounded responses** | Strict prompt rules prevent hallucinations—answers cite only retrieved text. |
| 🖥 **Zero-setup UI** | `streamlit run app.py`—that’s it. |
| 🔄 **Session memory** | Streamlit chat preserves Q&A until the page refreshes. |
| 🔒 **Key management** | Uses `.env` file via `python-dotenv` or environment variables—no secrets in code. |

---

## 📚 Architecture

```mermaid
flowchart LR
    %% ── Client ─────────────────
    subgraph Client
        A[Browser] -->|WebSocket| D[Streamlit&nbsp;Server]
    end

    %% ── Server ─────────────────
    subgraph Server
        D -->|"ask()"| F[backend.py]
        F -->|"embed & query"| P[Pinecone&nbsp;Vector&nbsp;DB]
        F -->|"chat completion"| O[OpenAI&nbsp;GPT-4o]
    end
