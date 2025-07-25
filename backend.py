"""ScoutBot backend – minimal, production‑ready.

Provides an `ask(question)` function that uses a Retrieval‑Augmented
Generation pipeline (OpenAI → Pinecone) to answer questions about
baseball scouting reports (2013–2019).

Set these environment variables before import/run:
    export OPENAI_API_KEY="sk‑..."
    export PINECONE_API_KEY="pc‑..."
    # Optional, defaults shown:
    export PINECONE_CLOUD="aws"
    export PINECONE_REGION="us‑east‑1"
"""

# ── Imports ────────────────────────────────────────────────────────────────
import os, textwrap
from langchain.schema import SystemMessage, HumanMessage
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from pinecone import Pinecone, ServerlessSpec
from pathlib import Path
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv())

# ── Config ─────────────────────────────────────────────────────────────────
INDEX_NAME = os.getenv("SCOUTBOT_INDEX", "scout-reports-index")
CLOUD      = os.getenv("PINECONE_CLOUD",  "aws")
REGION     = os.getenv("PINECONE_REGION", "us-east-1")
API_KEY    = os.getenv("PINECONE_API_KEY")

if not API_KEY:
    raise EnvironmentError("PINECONE_API_KEY environment variable not set")

# ── Vector DB & Embeddings ────────────────────────────────────────────────
embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
EMBED_DIM  = len(embeddings.embed_query("ping"))

pc = Pinecone(api_key=API_KEY)
if INDEX_NAME not in pc.list_indexes().names():
    raise ValueError(
        f"Pinecone index '{INDEX_NAME}' not found. "
        "Create it (and upsert vectors) before using `ask`."
    )

index = pc.Index(INDEX_NAME)

# ── LLM ────────────────────────────────────────────────────────────────────
llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=0.2)

# ── Helpers ───────────────────────────────────────────────────────────────
def _fmt_source(idx: int, hit: dict, width: int = 90) -> str:
    """Pretty‑print one Pinecone match for CLI/debug."""
    text  = hit["metadata"]["text"].replace("\n", " ").strip()
    first = textwrap.shorten(text, width=width, placeholder="…")
    return f"{idx:02d}. [score {hit['score']:.3f}]  {first}"

# ── Public API ────────────────────────────────────────────────────────────
def ask(question: str, k: int = 6, show_sources: bool = False) -> str:
    """Return answer string; optionally print sources.

    Parameters
    ----------
    question : str
        User query about scouting reports.
    k : int, default 6
        Top‑K chunks to retrieve.
    show_sources : bool, default False
        If True, prints formatted source snippets.

    Returns
    -------
    str
        Answer from the LLM, constrained to provided context.
    """
    # Retrieve context
    vec   = embeddings.embed_query(question)
    hits  = index.query(vector=vec, top_k=k, include_metadata=True)["matches"]
    if not hits:
        return "No relevant information found in the vector database."

    context = "\n\n---\n\n".join(h["metadata"]["text"] for h in hits)

    # LLM prompt
    msgs = [
         SystemMessage(content= "You are Scout-RAG, a baseball scouting assistant. "
        "The user will ask questions about prospects; the only facts you may use "
        "come from the **Context** section below, which consists of one-or-more "
        "scouting-report excerpts. Each excerpt follows this pattern:\n"
        "  SCOUTING REPORT: <Name> — <Pos> (<Year>) | <Narrative> | <Grades>\n\n"

        "RULES you must follow when you craft an answer:\n"
        "1. **Grounding** – Never add information that is not present in the "
        "   context. If the answer is not found, say so briefly.\n"
        "2. **Numeric constraints** – When a question specifies cut-offs "
        "   (e.g., ‘changeup ≥ 55’, ‘sub-20 % strike-out rate’), list ONLY "
        "   players whose grades or stats in the context satisfy EVERY "
        "   condition. Ignore partial matches.\n"
        "3. **Filters** – Obey filters the user implies (handedness, year, "
        "   position, ETA, league, etc.). If a chunk lacks the field, treat "
        "   it as non-qualifying.\n"
        "4. **One row per player** – Mention a player at most once. If the "
        "   context contains duplicates or multiple years, use the one that "
        "   best satisfies the query.\n"
        "5. **Concise output** – Prefer short bullet lists or numbered lists "
        "   (Name – key grades/traits). No paragraphs of fluff.\n"
        "6. **Unambiguous grades** – Quote numeric grades exactly as they "
        "   appear (e.g., ‘Changeup 60’, not ‘plus changeup’).\n"
        "7. **Hallucination check** – After drafting your answer, quickly "
        "   verify each fact against the context. Remove any item that is "
        "   not explicitly supported.\n\n"

        "Respond with the answer first. If the caller passes "
        "`show_sources=True`, the code will print the source snippets "
        "after your answer, so do NOT embed citations or excerpts yourself."
),
        HumanMessage(content=f"Context:\n{context}\n\nQuestion:\n{question}")
    ]
    answer = llm(msgs).content.strip()

    # Optional CLI display
    if show_sources:
        print("\nAnswer:\n", answer, "\n")
        print("### Sources")
        for i, h in enumerate(hits, 1):
            print(_fmt_source(i, h))

    return answer


def similarity_search(query: str, k: int = 4):
    """Return raw Pinecone matches (for debugging)."""
    vec = embeddings.embed_query(query)
    return index.query(vector=vec, top_k=k, include_metadata=True)["matches"]
