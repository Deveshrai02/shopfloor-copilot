
# Shopfloor Copilot

Automotive manufacturing operators spend significant time manually searching SOPs for escalation thresholds, role responsibilities, and procedure steps — and separately querying production dashboards for OEE, defect counts, and downtime logs. Both tasks interrupt the floor and introduce latency when fast decisions matter. Shopfloor Copilot puts both information sources behind a single plain-language interface: operators ask questions in the same way they would ask a colleague, and the agent determines whether to retrieve from the SOP knowledge base, fetch live MES data, or raise a formal incident ticket — without the operator needing to know which system holds the answer.

> 🎬 **Link:** https://huggingface.co/spaces/drai2/shopfloor-copilot

---

## Architecture

```
User message
     │
     ▼
┌──────────────────────────────────────┐
│  LangGraph ReAct Agent               │
│  Model: claude-haiku-4-5             │
│                                      │
│  ┌─────────────┐  tool_calls?        │
│  │ agent node  │──────────────────►  │
│  │  (LLM)      │                     │
│  └─────────────┘ ◄────────────────── │
│         │         tool results       │
│         │ no tool calls              │
│         ▼                            │
│        END                           │
└──────────────────────────────────────┘
         │
         ▼ routes to one of three tools
┌─────────────────────────────────────────────────────┐
│  Tool 1: retrieve_sop                               │
│    FAISS (IndexFlatIP) + all-MiniLM-L6-v2           │
│    500-char sliding window chunks, cosine sim       │
│    Searches 6 SOP documents (~60 chunks)            │
│                                                     │
│  Tool 2: get_live_line_data                         │
│    GET /oee/{line} · /quality/{line}                │
│        /downtime/{line}                             │
│    Mock MES API (FastAPI) on localhost:8000         │
│    Lines: TRIM-01, TRIM-02, FA-01, FA-02, EV-BAT   │
│                                                     │
│  Tool 3: create_incident_ticket                     │
│    POST /tickets                                    │
│    Severity: low / medium / high                    │
└─────────────────────────────────────────────────────┘
```

**Stack:** Python 3.11 · LangGraph · langchain-anthropic · FAISS · sentence-transformers · FastAPI · Streamlit · Docker

---

## Evaluation Results

Tested against 22 questions across four categories using `eval/run_eval.py`:

| Category | Correct | Total | Accuracy |
|---|---|---|---|
| SOP / Document retrieval | 8 | 8 | 100% |
| Live MES data lookup | 8 | 8 | 100% |
| Ticket creation | 3 | 3 | 100% |
| Out-of-scope (no tool expected) | 3 | 3 | 100% |
| **Overall** | **22** | **22** | **100%** |

Model: `claude-haiku-4-5` · Run: 2026-06-18 · Full results: [`eval/results.json`](eval/results.json)

The out-of-scope questions verify that the agent correctly withholds tool calls for general knowledge questions ("What is OEE?") and off-topic requests ("Write me a Python script"), rather than invoking a tool unnecessarily.

---

## Project Structure

```
shopfloor-copilot/
├── app/
│   ├── agent.py            # LangGraph StateGraph — agent + tools nodes
│   ├── tools.py            # @tool functions: retrieve_sop, get_live_line_data, create_incident_ticket
│   ├── rag.py              # FAISS ingestion and retrieval pipeline
│   ├── mock_mes_api.py     # FastAPI MES simulator
│   └── streamlit_app.py    # Chat UI
├── data/
│   ├── sops/               # 6 Markdown SOP documents
│   └── index/              # FAISS index + chunk metadata (built at runtime)
├── eval/
│   ├── test_questions.json # 22 evaluation questions with expected tool labels
│   ├── run_eval.py         # Evaluation harness
│   └── results.json        # Latest eval output
├── Dockerfile              # For local docker-compose
├── Dockerfile.spaces       # For Hugging Face Spaces (single container)
├── docker-compose.yml
└── requirements.txt
```

---

## Run Locally

**Prerequisites:** Python 3.11+, an [Anthropic API key](https://console.anthropic.com/settings/api-keys)

```bash
git clone https://github.com/<your-username>/shopfloor-copilot
cd shopfloor-copilot
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# edit .env and set ANTHROPIC_API_KEY=sk-ant-...

# Build the FAISS index (run once)
python -m app.rag

# Terminal 1 — MES API
uvicorn app.mock_mes_api:app --port 8000

# Terminal 2 — Streamlit UI
streamlit run app/streamlit_app.py
# → http://localhost:8501
```

**With Docker:**

```bash
docker compose up --build
# Streamlit → http://localhost:8501
# MES API   → http://localhost:8000
```

---

## Run the Evaluation

```bash
# With the MES API running on :8000 and the FAISS index built:
python -m eval.run_eval

# Run a specific subset of questions:
python -m eval.run_eval --ids 1,9,17,20
```

Results are saved to `eval/results.json`.

---

## Data Disclosure

All MES data — OEE figures, defect counts, downtime events, and quality metrics — is **procedurally generated** by `app/mock_mes_api.py`. No real manufacturing equipment or production data is connected. Values are designed to fall within credible automotive manufacturing ranges but represent no actual plant or production line. The SOP documents are illustrative examples written for this project and do not represent any organisation's internal procedures.
