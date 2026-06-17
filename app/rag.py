"""
RAG (Retrieval-Augmented Generation) pipeline for Shopfloor Copilot.

Architecture overview for interviews:
--------------------------------------
The pipeline has two phases:

  INGESTION (run once, results saved to disk):
    1. Load .md files from data/sops/
    2. Split each file into overlapping character-level chunks
    3. Embed each chunk with a sentence-transformer model → fixed-length float vectors
    4. Load those vectors into a FAISS index optimised for cosine similarity search
    5. Persist the index and chunk metadata to disk

  RETRIEVAL (called at query time):
    1. Embed the user's query with the same model
    2. Search the FAISS index for the nearest-neighbour vectors
    3. Return the matching text chunks with source metadata and scores

Why FAISS over a managed vector DB?
  For a local/portfolio project, FAISS runs fully in-process with no
  external service dependency. It supports exact nearest-neighbour search
  (IndexFlatIP) which is correct and fast at this data size (<10k chunks).
  In production you would replace this with Pinecone, Weaviate, or pgvector.

Why sentence-transformers "all-MiniLM-L6-v2"?
  It is a 22M-parameter model that runs on CPU in milliseconds per batch,
  produces 384-dimensional embeddings, and consistently ranks well on
  semantic textual similarity benchmarks relative to its size. No API key
  or network call required — important for a self-contained demo.
"""

import json
import os
from pathlib import Path
from dataclasses import dataclass, asdict

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------

_REPO_ROOT  = Path(__file__).resolve().parent.parent
_SOPS_DIR   = _REPO_ROOT / "data" / "sops"
_INDEX_DIR  = _REPO_ROOT / "data" / "index"
_INDEX_FILE = _INDEX_DIR / "faiss.index"
_META_FILE  = _INDEX_DIR / "chunks.json"

# ---------------------------------------------------------------------------
# Model — loaded once at module level so repeated retrieve() calls don't
# reload it. The model is ~90 MB and takes ~1 s to initialise.
# ---------------------------------------------------------------------------

_MODEL_NAME = "all-MiniLM-L6-v2"
_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(_MODEL_NAME)
    return _model


# ---------------------------------------------------------------------------
# Data types
# ---------------------------------------------------------------------------

@dataclass
class Chunk:
    """A single text fragment produced by the chunking step."""
    text: str
    source: str      # filename, e.g. "SOP-FA-019-torque-verification.md"
    doc_id: str      # document_id from the SOP frontmatter if present, else stem
    char_start: int  # character offset in the original document
    chunk_index: int # position of this chunk within its source document


@dataclass
class RetrievalResult:
    """One result returned by retrieve()."""
    text: str
    source: str
    doc_id: str
    chunk_index: int
    score: float     # cosine similarity in [0, 1]; higher is more relevant


# ---------------------------------------------------------------------------
# 1. Ingestion: load and chunk
# ---------------------------------------------------------------------------

def load_and_chunk_documents(
    chunk_size: int = 500,
    overlap: int = 50,
) -> list[Chunk]:
    """
    Read every .md file in data/sops/ and split each into overlapping chunks.

    Chunking strategy — character-level sliding window:
      Each chunk is `chunk_size` characters long. The next chunk starts
      `chunk_size - overlap` characters after the previous one, so the last
      `overlap` characters of chunk N are repeated at the start of chunk N+1.

      Why overlap at all?
        A sentence or clause that falls at a chunk boundary would be split
        across two chunks. Without overlap, neither chunk carries enough
        context to answer a question about that boundary content. With overlap,
        at least one of the two adjacent chunks contains the complete thought.

      Why character-level rather than token- or sentence-level?
        Simplicity and model-agnosticism. Token-level chunking is tighter
        but requires running a tokeniser; sentence-level requires a sentence
        splitter that can mis-fire on numbered lists and tables (common in
        SOPs). Character-level is deterministic, fast, and accurate enough
        for documents of this length and style.

      Why 500 / 50?
        all-MiniLM-L6-v2 accepts up to 256 word-piece tokens (~1,000 chars),
        so 500 chars sits comfortably within one embedding context window.
        50-char overlap (~10%) is sufficient to bridge boundary sentences
        without bloating the index.

    Returns:
        List of Chunk objects, in document order within each file.
    """
    if not _SOPS_DIR.exists():
        raise FileNotFoundError(
            f"SOP directory not found: {_SOPS_DIR}\n"
            "Expected .md files at data/sops/"
        )

    md_files = sorted(_SOPS_DIR.glob("*.md"))
    if not md_files:
        raise FileNotFoundError(f"No .md files found in {_SOPS_DIR}")

    chunks: list[Chunk] = []
    step = chunk_size - overlap  # how far to advance the window each iteration

    for filepath in md_files:
        text = filepath.read_text(encoding="utf-8")
        source = filepath.name

        # Try to extract document_id from YAML frontmatter (--- key: value ---)
        doc_id = filepath.stem  # fallback
        if text.startswith("---"):
            for line in text.splitlines()[1:]:
                if line.strip() == "---":
                    break
                if line.lower().startswith("document_id:"):
                    doc_id = line.split(":", 1)[1].strip()
                    break

        # Sliding window over the document text
        start = 0
        chunk_index = 0
        while start < len(text):
            end = start + chunk_size
            chunk_text = text[start:end].strip()

            if chunk_text:  # skip any empty windows (e.g. trailing whitespace)
                chunks.append(Chunk(
                    text=chunk_text,
                    source=source,
                    doc_id=doc_id,
                    char_start=start,
                    chunk_index=chunk_index,
                ))
                chunk_index += 1

            start += step

    print(f"[rag] Loaded {len(md_files)} documents → {len(chunks)} chunks")
    return chunks


# ---------------------------------------------------------------------------
# 2. Ingestion: embed and index
# ---------------------------------------------------------------------------

def build_faiss_index(
    chunk_size: int = 500,
    overlap: int = 50,
) -> tuple[faiss.Index, list[Chunk]]:
    """
    Embed all SOP chunks and build a FAISS index, then persist both to disk.

    Embedding:
      Each chunk's text is passed through the sentence-transformer to produce
      a 384-dimensional float32 vector. This vector is a dense semantic
      representation: chunks about similar topics have vectors that point in
      similar directions in 384-dimensional space.

    Normalisation:
      Vectors are L2-normalised (divided by their Euclidean magnitude) before
      indexing. After normalisation, the dot product between two vectors equals
      their cosine similarity. This is important: FAISS IndexFlatIP performs
      inner-product (dot product) search, so normalising first means we are
      doing cosine similarity search, which measures angular distance between
      meaning vectors rather than Euclidean distance. Cosine similarity is the
      standard metric for sentence embedding retrieval.

    Index type — IndexFlatIP:
      "Flat" means all vectors are stored explicitly — no compression,
      clustering, or approximation. Every query performs an exact comparison
      against every stored vector. At <10,000 chunks this is fast (sub-ms)
      and returns exact nearest neighbours. Larger deployments would switch
      to IndexIVFFlat or IndexHNSWFlat for approximate search at scale.
      "IP" = inner product.

    Persistence:
      The FAISS index is saved to data/index/faiss.index using FAISS's native
      binary format. Chunk metadata (text, source, doc_id, etc.) is saved as
      JSON because FAISS only stores vectors, not the associated text.
      On load, the two files are paired by position: index row i corresponds
      to chunks[i].

    Returns:
        (faiss_index, list_of_chunks)
    """
    chunks = load_and_chunk_documents(chunk_size=chunk_size, overlap=overlap)
    model  = _get_model()

    texts = [c.text for c in chunks]
    print(f"[rag] Embedding {len(texts)} chunks with {_MODEL_NAME} …")
    # batch_size=64 keeps memory reasonable; encode() handles batching internally
    embeddings = model.encode(texts, batch_size=64, show_progress_bar=True, convert_to_numpy=True)

    # L2-normalise so that IndexFlatIP gives cosine similarity scores
    faiss.normalize_L2(embeddings)

    dimension = embeddings.shape[1]  # 384 for all-MiniLM-L6-v2
    index = faiss.IndexFlatIP(dimension)
    index.add(embeddings)

    # Persist
    _INDEX_DIR.mkdir(parents=True, exist_ok=True)
    faiss.write_index(index, str(_INDEX_FILE))
    with open(_META_FILE, "w", encoding="utf-8") as f:
        json.dump([asdict(c) for c in chunks], f, indent=2, ensure_ascii=False)

    print(f"[rag] Index saved → {_INDEX_FILE}  ({index.ntotal} vectors, dim={dimension})")
    return index, chunks


# ---------------------------------------------------------------------------
# 3. Load
# ---------------------------------------------------------------------------

def load_index() -> tuple[faiss.Index, list[Chunk]]:
    """
    Load the FAISS index and chunk metadata from disk.

    If the index files do not exist (first run, or after deleting data/index/),
    build_faiss_index() is called automatically so the caller never needs to
    worry about whether the index is initialised.

    The index and chunks list are returned rather than stored in a global so
    that the caller controls the lifecycle — useful in tests and for the agent
    which holds them in state.
    """
    if _INDEX_FILE.exists() and _META_FILE.exists():
        print(f"[rag] Loading existing index from {_INDEX_DIR}")
        index = faiss.read_index(str(_INDEX_FILE))
        with open(_META_FILE, encoding="utf-8") as f:
            raw = json.load(f)
        chunks = [Chunk(**item) for item in raw]
        print(f"[rag] Loaded {index.ntotal} vectors, {len(chunks)} chunks")
        return index, chunks

    print("[rag] No existing index found — building from source documents …")
    return build_faiss_index()


# ---------------------------------------------------------------------------
# 4. Retrieval
# ---------------------------------------------------------------------------

def retrieve(
    query: str,
    index: faiss.Index,
    chunks: list[Chunk],
    k: int = 3,
) -> list[RetrievalResult]:
    """
    Find the k most semantically relevant SOP chunks for a natural-language query.

    How it works:
      1. The query string is embedded with the same sentence-transformer model
         used at ingestion time. Using the same model is essential: the query
         vector must live in the same semantic space as the document vectors
         for distance comparisons to be meaningful.
      2. The query vector is L2-normalised (same as at index time).
      3. FAISS.search() returns the k highest inner-product scores and their
         row indices in the index. Because both sets of vectors are normalised,
         these scores are cosine similarities in the range [0, 1].
      4. Each index row i maps directly to chunks[i], so we reconstruct
         RetrievalResult objects with text, source, and score.

    Score interpretation:
      > 0.85  Very high relevance — likely a direct answer
      0.70–0.85  Good relevance — related content
      0.50–0.70  Partial relevance — may contain useful context
      < 0.50  Low relevance — probably not useful; agent should say so

    Args:
        query:  The operator's natural-language question.
        index:  Loaded FAISS index (from load_index()).
        chunks: Parallel list of Chunk metadata (from load_index()).
        k:      Number of results to return. Defaults to 3 — enough context
                for the agent without overloading the LLM context window.

    Returns:
        List of RetrievalResult, sorted by descending similarity score.
    """
    model  = _get_model()
    vector = model.encode([query], convert_to_numpy=True)
    faiss.normalize_L2(vector)

    scores, indices = index.search(vector, k)

    results: list[RetrievalResult] = []
    for score, idx in zip(scores[0], indices[0]):
        if idx == -1:
            # FAISS returns -1 for unfilled slots when k > index.ntotal
            continue
        chunk = chunks[idx]
        results.append(RetrievalResult(
            text=chunk.text,
            source=chunk.source,
            doc_id=chunk.doc_id,
            chunk_index=chunk.chunk_index,
            score=float(score),
        ))

    return results


# ---------------------------------------------------------------------------
# Convenience wrapper — lets callers skip managing index/chunks state
# ---------------------------------------------------------------------------

_cached_index: faiss.Index | None = None
_cached_chunks: list[Chunk] | None = None


def retrieve_simple(query: str, k: int = 3) -> list[RetrievalResult]:
    """
    Stateless retrieve wrapper that manages index loading internally.

    Loads (or builds) the index on first call, then caches it in module-level
    globals so subsequent calls are fast. Suitable for simple scripts and the
    agent tools layer where passing index/chunks objects around is inconvenient.
    """
    global _cached_index, _cached_chunks
    if _cached_index is None or _cached_chunks is None:
        _cached_index, _cached_chunks = load_index()
    return retrieve(query, _cached_index, _cached_chunks, k=k)


# ---------------------------------------------------------------------------
# Standalone test — run with: python -m app.rag
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import textwrap

    print("=" * 60)
    print("Shopfloor Copilot — RAG pipeline self-test")
    print("=" * 60)

    # Force a rebuild so the self-test always reflects current SOP files
    print("\n[1/2] Building index from data/sops/ …\n")
    idx, ch = build_faiss_index()

    sample_queries = [
        "What should I do if the OEE falls below target for three shifts in a row?",
        "Who is responsible for signing off on a quality hold?",
        "What steps are required before handling a high-voltage battery pack?",
        "How do I log a downtime event in MES?",
    ]

    print(f"\n[2/2] Running {len(sample_queries)} sample queries …\n")
    print("-" * 60)

    for query in sample_queries:
        results = retrieve(query, idx, ch, k=3)
        print(f"\nQ: {query}")
        for i, r in enumerate(results, 1):
            preview = textwrap.shorten(r.text, width=120, placeholder=" …")
            print(f"  [{i}] score={r.score:.3f}  source={r.source}")
            print(f"       {preview}")
        print("-" * 60)
