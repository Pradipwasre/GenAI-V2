# Adaptive RAG — Complete Blueprint (Theory → Code)

> Stack (2026): `langchain` / `langchain-core` (v0.3+ style), `langgraph` (v0.6+ / 1.x), `langchain-openai`, `langchain-community`, FAISS. **No legacy imports** (`langchain_experimental`, old `langchain.chains`, or deprecated `ChatOpenAI` kwargs).

---

## 1. What is Adaptive RAG?

**Adaptive RAG** is a question-answering architecture that **routes each incoming question to the best retrieval / answering strategy at runtime**, instead of forcing every query through the same fixed pipeline.

In a *naive RAG* pipeline, every question does this:

```
question → embed → similarity search → stuff into prompt → answer
```

Problems with that:
- Easy questions ("What is the deductible?") get the same heavy treatment as hard ones.
- Ambiguous questions retrieve poor documents, and the model confidently hallucinates on top of them.
- Questions whose answers simply aren't in the knowledge base get fabricated instead of escalated.

**Adaptive RAG fixes this with a router at the front and quality gates in the loop.** The LangGraph-powered version (the canonical one from the LangGraph team) gives every question its own optimal path.

## 2. How it works — the decision logic

Each question flows through these **five decisions**:

| # | Decision | Made by | Outcome |
|---|----------|---------|---------|
| 1 | Is this question answerable from our KB, does it need the web, or can the LLM just answer? | **Router (LLM)** | `vectorstore` / `websearch` / `direct` |
| 2 | Are the retrieved documents actually relevant? | **Retrieval Grader (LLM)** | relevant → generate; irrelevant → rewrite question → re-retrieve |
| 3 | After up to N rewrite attempts, was anything relevant found? | **State counter** | found → generate; exhausted → web search fallback |
| 4 | Does the generated answer avoid hallucination (grounded in the docs)? | **Hallucination Grader** | grounded → answer check; not grounded → regenerate |
| 5 | Does the answer actually address the question? | **Answer Grader** | useful → return to user; not useful → rewrite question → re-retrieve |

## 3. Blueprint — the graph structure

```
                    ┌──────────────┐
   question ──────► │   ROUTER     │ ──direct──► LLM answers from parametric knowledge
                    └──────┬───────┘
                           │ vectorstore
                           ▼
                    ┌──────────────┐     irrelevant (retry ≤ 2)
                    │  RETRIEVE    │ ───────────────────────────────┐
                    │ (FAISS +     │                                ▼
                    │ embeddings)  │                        ┌──────────────┐
                    └──────┬───────┘                        │   REWRITE    │
                           │ relevant                        │ QUESTION     │
                           ▼                                 └──────┬───────┘
                    ┌──────────────┐                              │ retry
                    │   GENERATE   │                              ▼
                    │  (RAG chain) │                        (back to RETRIEVE)
                    └──────┬───────┘
                           ▼
                    ┌──────────────┐
                    │ HALLUCINATION│ ──not grounded──► (regenerate, retry ≤ 1)
                    │   GRADER     │
                    └──────┬───────┘
                           │ grounded
                           ▼
                    ┌──────────────┐
                    │ ANSWER       │ ──not useful──► REWRITE QUESTION
                    │ GRADER       │
                    └──────┬───────┘
                           │ useful
                           ▼
                        RETURN
```

Two extra edges from the router:
- `websearch` → goes straight to web search (Tavily in this notebook), then generation.
- If retrieval + rewrite is exhausted (3 tries, nothing relevant) → falls back to **web search** instead of giving up.

## 4. Components used (all current 2026 APIs)

| Component | Module | Role |
|---|---|---|
| `StateGraph`, `START`, `END` | `langgraph.graph` | Graph compiler |
| `@tool` | `langchain_core.tools` | Retriever-as-tool for the router |
| `MessagesState` | `langgraph.graph.message` | State schema |
| `ChatPromptTemplate`, `StrOutputParser` | `langchain_core.prompts` / `langchain_core.output_parsers` | Prompting & parsing |
| `ChatOpenAI` | `langchain_openai` | LLM for all graders/router/generator |
| `OpenAIEmbeddings` | `langchain_openai` | Embeddings |
| `FAISS` | `langchain_community.vectorstores` | Local vector store |
| `RecursiveCharacterTextSplitter` | `langchain_text_splitters` | Chunking |
| `TavilySearchResults` | `langchain_community.tools.tavily_search` | Web fallback |
| `tool_condition`, `tools_condition` | `langgraph.prebuilt` | Router → tool/agent edges |

## 5. State design

```python
class AdaptiveRAGState(MessagesState):
    question: str          # original user question
    documents: list        # retrieved/approved documents
    generation: str        # current draft answer
    web_search_count: int  # web-search budget
    max_web_searches: int
    max_rewrite_tries: int
```

Every node reads what it needs from state and returns a partial update — that is the whole LangGraph contract.

## 6. Typical runs (what you should see in the notebook)

1. **In-scope question** → router picks `vectorstore` → docs graded relevant → answer → hallucination pass → answer pass → done.
2. **Out-of-scope question** (e.g., "Who won the World Cup 2026?") → router picks `vectorstore` → nothing relevant → rewrite ×2 → web search fallback → answer grounded in search results.
3. **Ambiguous question** → router → retrieval graded irrelevant → question rewritten ("clarified") → second retrieval succeeds.

---

## 7. Notebook map

| Cell block | File section | What it does |
|---|---|---|
| 1 | Setup | Installs/imports, env vars |
| 2 | KB ingestion | Loads `company_docs/*.txt`, chunks, embeds, builds FAISS index |
| 3 | Grading chains | Router, retrieval grader, hallucination grader, answer grader, generator, rewriter |
| 4 | Tools & nodes | Retriever tool, web search, node functions |
| 5 | Graph assembly | `StateGraph` + all conditional edges + compile |
| 6 | Demo runs | The 3 scenarios above with full traces |
