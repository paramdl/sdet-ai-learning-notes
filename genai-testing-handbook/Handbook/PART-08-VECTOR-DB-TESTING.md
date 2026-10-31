# PART 8 — Vector Database Testing

> **Goal of this part:** test the storage layer under RAG. Vector databases fail in ways relational databases do not: they return *wrong-but-plausible* results with no error, no exception, and no log entry. That property makes them uniquely dangerous and uniquely worth testing.

---

## 8.1 The concepts, quickly

### Vector
> **Imagine this…** A list of numbers describing a piece of text, the way `[height, weight, age]` describes a person. Text embeddings just use 384–3072 numbers instead of 3, and no single number means anything on its own.

**Technically.** A fixed-length array of floats. The dimension is fixed by the embedding model and cannot vary within a collection.

### Similarity and distance metrics 🔴

| Metric | Formula (intuition) | Range | Use when |
|---|---|---|---|
| **Cosine similarity** | Angle between the two arrows | −1 to 1 (0–1 in practice for text) | **Default for text.** Ignores magnitude, compares direction/meaning |
| **Cosine distance** | 1 − cosine similarity | 0 to 2 | What most DBs actually store and sort by |
| **Euclidean (L2)** | Straight-line distance between the points | 0 to ∞ | When magnitude carries meaning; some image embeddings |
| **Dot / inner product** | Projection of one onto the other | −∞ to ∞ | When vectors are already normalised — then it equals cosine, and is faster |

**The trap, and the test that catches it:** if vectors are **normalised** (unit length), cosine and dot product give the same ranking. If they are **not** normalised, dot product favours long vectors — meaning longer documents rank higher regardless of relevance. This produces a subtly biased retriever that no error message will ever reveal.

```
TC-VDB-001  Metric and normalisation consistency
Steps:      1. Read the metric configured on the collection/index
            2. Read the metric the embedding model was trained for
            3. Check whether stored vectors are unit-normalised
Expected:   All three agree. If dot product is used, vectors ARE normalised.
Failure:    Silent ranking bias — longer chunks systematically outrank
            shorter, more relevant ones
Detection:  Correlate chunk length with retrieval rank across the golden
            set. A strong positive correlation is the smoking gun.
Priority:   High   Severity: Major
```

### Indexing 🔴
A brute-force scan compares the query to every vector: perfectly accurate, unusably slow past a few hundred thousand rows. Real systems use **approximate nearest neighbour (ANN)** indexes.

| Index | How it works (intuition) | Trade-off knobs |
|---|---|---|
| **HNSW** | A multi-layer graph you descend, like a skip list | `m` (connections), `ef_construction` (build quality), `ef_search` (query effort) |
| **IVF / IVFFlat** | Cluster vectors, search only the nearest clusters | `lists` (clusters), `probes` (clusters searched) |
| **Flat** | Exhaustive scan | None — exact, slow |

**The single most important fact about ANN indexes for a tester:**

> **An approximate index does not guarantee correct results. It trades recall for speed, and the amount it trades is a configuration setting.**

This means **the index is a quality parameter, not just a performance parameter**. A team that tunes `ef_search` down to hit a latency target has silently degraded answer quality across the entire product, and no test in a conventional suite would notice.

```
TC-VDB-002  ANN recall vs exact search
Method:     1. Run 100 golden queries with the ANN index → results_ann
            2. Run the same queries with exact/flat search → results_exact
            3. recall = |results_ann ∩ results_exact| / |results_exact|
Expected:   recall@10 ≥ 0.95 at the configured search parameters
Value:      Quantifies exactly what the speed optimisation cost in quality.
            This is THE test that vector-DB tuning discussions need and
            almost never have.
Priority:   High   Automatable: Yes
```

---

## 8.2 PostgreSQL + pgvector — worked

The most common enterprise choice, because the operational cost of a new database is often higher than the benefit.

### Schema and index
```sql
CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE chunks (
  id          BIGSERIAL PRIMARY KEY,
  doc_id      TEXT   NOT NULL,
  tenant_id   TEXT   NOT NULL,              -- isolation
  acl_groups  TEXT[] NOT NULL DEFAULT '{}', -- document-level permissions
  chunk_text  TEXT   NOT NULL,
  chunk_index INT    NOT NULL,
  metadata    JSONB  NOT NULL DEFAULT '{}',
  embedding   VECTOR(1536) NOT NULL,        -- MUST match the model
  created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- HNSW index. vector_cosine_ops MUST match the operator used in queries.
CREATE INDEX chunks_embedding_idx ON chunks
  USING hnsw (embedding vector_cosine_ops)
  WITH (m = 16, ef_construction = 64);

-- Filter columns need their own indexes, or every query full-scans them.
CREATE INDEX chunks_tenant_idx ON chunks (tenant_id);
CREATE INDEX chunks_meta_idx   ON chunks USING gin (metadata);
```

### The query
```sql
-- <=> is cosine DISTANCE. Similarity = 1 - distance.
SET LOCAL hnsw.ef_search = 100;   -- higher = better recall, slower

SELECT id, doc_id, chunk_text,
       1 - (embedding <=> $1::vector) AS similarity
FROM chunks
WHERE tenant_id = $2                       -- isolation, IN the query
  AND acl_groups && $3::text[]             -- permission overlap
ORDER BY embedding <=> $1::vector
LIMIT 5;
```

### The tests that matter

```sql
-- TC-VDB-003  Dimension integrity. A mismatch throws on insert, which is
-- good — but assert the column matches the CURRENT model config.
SELECT atttypmod FROM pg_attribute
WHERE attrelid = 'chunks'::regclass AND attname = 'embedding';

-- TC-VDB-004  Orphan detection: chunks with no embedding, or vice versa.
SELECT COUNT(*) FROM chunks WHERE embedding IS NULL;              -- must be 0

-- TC-VDB-005  Tenant completeness (cross-tenant leak precursor).
SELECT COUNT(*) FROM chunks WHERE tenant_id IS NULL OR tenant_id = '';  -- 0

-- TC-VDB-006  Zero vectors — match everything or nothing depending on metric.
SELECT COUNT(*) FROM chunks
WHERE embedding <=> array_fill(0, ARRAY[1536])::vector = 0;       -- must be 0

-- TC-VDB-007  Exact duplicates wasting top-K slots.
SELECT chunk_text, COUNT(*) FROM chunks
GROUP BY chunk_text HAVING COUNT(*) > 1;

-- TC-VDB-008  Is the index actually being used? A sequential scan here
-- means the index is missing, invalid, or the operator does not match
-- the ops class — a very common and totally silent misconfiguration.
EXPLAIN ANALYZE
SELECT id FROM chunks ORDER BY embedding <=> $1::vector LIMIT 5;
-- Expect: "Index Scan using chunks_embedding_idx"
-- Fail:   "Seq Scan on chunks"
```

**`TC-VDB-008` is the highest-value query in this part.** A vector index that is not being used still returns *correct* results — just slowly. Teams discover it at 10× scale, in production, during an incident. `EXPLAIN ANALYZE` finds it in one second.

### The metric-mismatch bug, demonstrated
```sql
-- Index built for cosine:
CREATE INDEX ... USING hnsw (embedding vector_cosine_ops);

-- But the query uses L2:
SELECT ... ORDER BY embedding <-> $1::vector LIMIT 5;
--                            ^^^ WRONG OPERATOR

-- Postgres does not error. It cannot use the cosine index, so it either
-- falls back to a sequential scan (slow but correct for L2) or, in some
-- configurations, produces a different ranking than intended.
-- Either way: no exception, no log, wrong or slow behaviour.
```

```
TC-VDB-009  Operator/ops-class agreement
Method:     Parse the application's query for the distance operator; read
            the index definition from pg_indexes; assert they correspond
            (<=> ↔ vector_cosine_ops, <-> ↔ vector_l2_ops,
             <#> ↔ vector_ip_ops)
Priority:   High   Automatable: Yes — a 20-line test that catches a bug
            class with zero natural symptoms
```

---

## 8.3 A dedicated vector DB — Qdrant worked

```python
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue

client = QdrantClient(url="http://localhost:6333")

# Collection config — Distance.COSINE must match the embedding model.
client.recreate_collection(
    collection_name="docs",
    vectors_config=VectorParams(size=1536, distance=Distance.COSINE),
)

# Search WITH a tenant filter applied at the engine level (pre-filtering),
# not by filtering results afterwards in Python.
hits = client.search(
    collection_name="docs",
    query_vector=query_vec,
    query_filter=Filter(must=[
        FieldCondition(key="tenant_id", match=MatchValue(value="tenant-a"))
    ]),
    limit=5,
    with_payload=True,
)
```

### Pre-filtering vs post-filtering — a correctness issue, not just performance

> **Imagine this…** You want the 5 nearest restaurants that are open now. **Pre-filtering** searches only open restaurants and returns the nearest 5 — correct. **Post-filtering** finds the 5 nearest restaurants overall, then removes the closed ones — and hands you 2 results, or none.

```
TC-VDB-010  Filtered search completeness
Steps:      In a corpus where tenant A owns 5% of documents, run a
            tenant-A-filtered search with limit=10
Expected:   10 results from tenant A (assuming ≥10 exist)
Failure:    Fewer than 10 results, or zero — proof of post-filtering.
            Users of small tenants get systematically worse retrieval,
            and nobody notices because the results returned are valid.
Priority:   High   Severity: Major   Automatable: Yes
```

This is a genuinely subtle bug that produces a real, unfair user experience: the smaller your tenant, the worse your search. It is invisible unless you specifically test for result *count* under a selective filter.

---

## 8.4 The full vector DB test matrix

| # | Category | Test | Priority |
|---|---|---|---|
| 1 | **Schema** | Dimension matches the embedding model | Critical |
| 2 | Schema | Metric matches model + query operator + index ops class | Critical |
| 3 | Schema | Required metadata fields non-null (tenant, acl, source) | Critical |
| 4 | **Ingest** | All chunks embedded — count parity | High |
| 5 | Ingest | No zero/NaN vectors | High |
| 6 | Ingest | Idempotent upsert — re-ingesting does not duplicate | High |
| 7 | Ingest | Deletion actually removes vectors (not just tombstones a query can still see) | High |
| 8 | Ingest | Update replaces the vector, does not append a stale twin | High |
| 9 | **Search** | ANN recall vs exact ≥ threshold | High |
| 10 | Search | Index is used (`EXPLAIN`) | High |
| 11 | Search | Top-K returns exactly K when K results exist | Medium |
| 12 | Search | Filtered search is pre-filtered (count test) | High |
| 13 | Search | Similarity scores are in the expected range and monotonically ordered | Medium |
| 14 | Search | Empty collection returns empty, not an error | Medium |
| 15 | **Security** | Tenant filter enforced in the engine, not in app code | Critical |
| 16 | Security | ACL/permission filter enforced | Critical |
| 17 | Security | No injection via metadata filter values | High |
| 18 | Security | Embeddings are not exposed via any public API — vectors can be partially inverted to recover source text | High |
| 19 | **Performance** | p95 query latency at production corpus size | High |
| 20 | Performance | Latency under concurrent load | High |
| 21 | Performance | Index build time acceptable for the reindex window | Medium |
| 22 | Performance | Memory footprint at target scale | Medium |
| 23 | **Reliability** | Behaviour when the DB is unavailable — graceful degradation, not a 500 | High |
| 24 | Reliability | Backup and restore preserves vectors and index | High |
| 25 | Reliability | Reindex can run without downtime (or downtime is documented) | Medium |
| 26 | **Data** | Freshness: new document retrievable within SLA | High |
| 27 | Data | Stale document removed within SLA after source deletion | High |

**Item 18 deserves a note.** Embeddings are not a safe one-way hash. Research on embedding inversion has shown that a meaningful portion of the original text can be reconstructed from its vector. ⏳ This is exactly why OWASP added **Vector and Embedding Weaknesses** to the LLM Top 10 (LLM09 in the 2026 list). Treat a vector store as containing the source data, with the same access controls — an API that returns raw vectors is a data-exposure finding.

---

## 8.5 Scale and performance testing

```python
import time, numpy as np

def latency_profile(client, queries, k=5, runs=3):
    """Latency at a given corpus size and search-parameter setting.
    Report p95, not mean — the mean hides the tail users actually feel."""
    lats = []
    for q in queries * runs:
        t0 = time.perf_counter()
        client.search(q, k=k)
        lats.append((time.perf_counter() - t0) * 1000)
    return {
        "p50_ms": round(float(np.percentile(lats, 50)), 1),
        "p95_ms": round(float(np.percentile(lats, 95)), 1),
        "p99_ms": round(float(np.percentile(lats, 99)), 1),
        "max_ms": round(max(lats), 1),
    }
```

**The scaling test that matters:** run the same profile at 10K, 100K, and 1M vectors. Vector search latency should grow roughly logarithmically with an ANN index. **Linear growth means the index is not being used** — the same defect as `TC-VDB-008`, caught from the performance side.

**The recall/latency curve.** Sweep the search-effort parameter (`ef_search` / `probes`) and plot recall against p95 latency. This single chart is what a team needs to choose a setting, and it converts a guess into a decision:

| ef_search | recall@10 | p95 latency |
|---|---|---|
| 40 | 0.86 | 12 ms |
| 100 | 0.95 | 24 ms |
| 200 | 0.98 | 41 ms |
| 400 | 0.99 | 78 ms |

---

## 8.6 Choosing a vector store — what a tester should know

| Option | Notes for testing |
|---|---|
| **pgvector** (Postgres) | Easiest to test — you have SQL, transactions, `EXPLAIN`, and existing tooling. Good to very large scale for most business corpora |
| **Qdrant** | Rust-based, strong filtering, easy local Docker instance. Good pre-filtering semantics |
| **Weaviate** | Built-in hybrid search and modules; more concepts to learn |
| **Milvus** | Built for very large scale; heavier to operate; more moving parts to test |
| **Chroma** | Simplest for local labs and prototypes; not the usual production choice |
| **Pinecone** | Managed service; less to operate, less to inspect. You cannot run `EXPLAIN` on someone else's cluster — test through behaviour instead |

**The tester's bias should be toward whatever you can inspect.** A managed service removes operational risk and removes your visibility with it; your tests must then be entirely black-box, which raises the value of the recall-vs-exact test (`TC-VDB-002`), because it is the only way to verify quality you cannot see.

---

## 8.7 Self-check

1. Why can a wrong distance operator produce no error and still be a serious bug?
2. What does an ANN index trade away, and how do you measure exactly how much?
3. How do you prove a vector index is not being used?
4. What is the difference between pre-filtering and post-filtering, and which user gets hurt by the wrong one?
5. Why is an API that returns raw embeddings a data-exposure finding?
6. Your search latency grows linearly with corpus size. What is the first thing you check?
7. Why must tenant isolation live in the query rather than in application code?

---

**Next:** [PART-09-AGENT-TESTING.md](PART-09-AGENT-TESTING.md) — agents, tool calling, and the highest-severity failure modes in modern AI systems.
