# Local RAG System — Project Plan

## 1. Project Goal

Build a basic **Retrieval-Augmented Generation (RAG)** system in Python that can answer questions using a locally stored collection of documentation.

The entire system should run locally without sending documents, embeddings, or prompts to a cloud API.

### Source Documentation Investigation

The initial documentation target is **Ruby 3.4.10**. Before building the ingestion pipeline, we inspected the official Ruby 3.4.10 source repository to determine where the documentation relevant to our initial test questions actually lives.

The investigation started with the repository's `doc/` directory. This showed several documentation categories, including historical changelogs, release notes, contributor documentation, examples, focused API documentation, and language syntax documentation.

A key finding was that much of Ruby's Core API documentation is embedded directly in the Ruby source files as **RDoc comments**, rather than existing entirely as standalone files under `doc/`. We therefore decided to use the relevant Ruby source files as our authoritative raw documentation sources.

#### Documentation sources identified

| Source | Relevant documentation |
| --- | --- |
| `array.c` | `Array#map` and `Array#map!`, including signatures and examples |
| `enum.c` | `Enumerable#map` and `Enumerable#select`, including signatures, descriptions, and examples |
| `hash.c` | `Hash#fetch`, including missing-key behavior, default values, block form, and examples |
| `io.c` | `IO#each_line`, including signatures and examples for reading lines |
| `load.c` | `require` and `require_relative` |
| `doc/syntax/methods.rdoc` | Ruby method/block documentation, including block arguments and passing blocks to methods |

The investigation also confirmed implementation relationships useful for retrieval testing. For example, `Array#map` is defined on `Array`, while `Enumerable` also defines `map`; `IO#each` and `IO#each_line` use the same implementation.

#### Keeping the initial source set small

We deliberately chose **not** to ingest the entire Ruby source repository.

The initial dataset is limited to the six files above because they provide the documentation necessary to answer the initial test questions while keeping the corpus small enough to inspect and understand manually.

We also decided not to treat the C source files as final RAG documents. They contain both useful RDoc and large amounts of implementation detail that are irrelevant to our initial questions. The ingestion pipeline should therefore extract and normalize the relevant RDoc into clean semantic documentation units before chunking and embedding.

The initial raw source set is:

```text
data/raw/ruby/3.4/
├── array.c
├── enum.c
├── hash.c
├── io.c
├── load.c
└── doc/syntax/methods.rdoc
```

The `doc/syntax/methods.rdoc` file should preserve its relative source path when copied into the raw dataset.

### Golden Questions

These six questions define the initial **golden question set** used to evaluate the documentation extraction and retrieval pipeline:

1. **What is the difference between `Array#map` and `Array#each`?**
2. **How does `Hash#fetch` behave when the key doesn't exist?**
3. **How do I read a file line-by-line in Ruby?**
4. **What does `Enumerable#select` return?**
5. **How does Ruby handle blocks passed to methods?**
6. **What is the difference between `require` and `require_relative`?**

These questions exercise several retrieval situations: API documentation, method signatures, examples, return values, missing-key behavior, language-level concepts, and relationships between related APIs.

The golden questions should remain stable while we develop the initial ingestion and retrieval pipeline so that changes to extraction, chunking, embeddings, metadata, or retrieval parameters can be evaluated against the same known questions.

### Next Step — Documentation Extraction

The next implementation step is a small **Python extraction script**.

The script should:

1. Read the selected Ruby source files.
2. Identify and extract the relevant RDoc comments.
3. Clean and normalize the extracted documentation.
4. Preserve useful source information and metadata.
5. Write the resulting semantic documentation units into `data/processed/ruby/3.4/`.
6. Allow us to inspect and validate the processed documents before introducing embeddings or ChromaDB.

The intended pipeline is:

```text
Ruby source files
       ↓
Python RDoc extraction
       ↓
Clean / normalize
       ↓
Semantic documentation units
       ↓
Inspect / validate
       ↓
Text chunking
       ↓
Embeddings
       ↓
ChromaDB
```

The extraction stage should be developed and tested independently before adding LangChain, embeddings, or ChromaDB. This keeps the source-processing step understandable and gives us a clean corpus to use when evaluating retrieval.

### Primary technologies

* **Language:** Python
* **RAG framework:** LangChain
* **Vector database:** ChromaDB
* **LLM:** Qwen3-8B
* **LLM format:** Quantized GGUF
* **LLM inference:** llama.cpp
* **Embedding model:** BGE-small-en-v1.5
* **Operating system:** Omarchy Linux
* **Hardware:** Acer Aspire A14

  * Intel Core Ultra 9 288V
  * Intel Arc integrated graphics
  * 32 GB RAM

---

# 2. High-Level Architecture

```text
                    LOCAL MACHINE
┌──────────────────────────────────────────────────────┐
│                                                      │
│  Documentation                                      │
│  ├── Markdown                                       │
│  ├── TXT                                            │
│  ├── PDF                                            │
│  └── HTML                                           │
│          │                                           │
│          ▼                                           │
│    Document Loader                                   │
│          │                                           │
│          ▼                                           │
│      Text Splitter                                  │
│          │                                           │
│          ▼                                           │
│  BGE-small-en-v1.5                                  │
│     Embedding Model                                 │
│          │                                           │
│          ▼                                           │
│       ChromaDB                                      │
│   ┌─────────────────────┐                           │
│   │ Vector embeddings   │                           │
│   │ Document chunks     │                           │
│   │ Metadata            │                           │
│   └─────────────────────┘                           │
│          │                                           │
│          │ Similarity Search                         │
│          ▼                                           │
│    Relevant Context                                  │
│          │                                           │
│          ▼                                           │
│       Qwen3-8B                                      │
│      Local LLM                                      │
│          │                                           │
│          ▼                                           │
│       Response                                      │
│                                                      │
└──────────────────────────────────────────────────────┘
```

---

# 3. Project Principles

The first version should prioritize **understanding how RAG works** over building the most sophisticated system possible.

### Principles

1. Everything should run locally.
2. Keep each component understandable and independently testable.
3. Avoid unnecessary abstractions during the initial implementation.
4. Use LangChain where it provides useful orchestration.
5. Understand the underlying operations before relying on LangChain abstractions.
6. Make components replaceable so different models can be benchmarked later.
7. Keep the original documentation separate from the vector database.
8. Build the system incrementally and test each stage independently.

---

# 4. Phase 1 — Prepare the Linux/Python Environment

## Objectives

Create an isolated Python development environment and establish the project structure.

### Tasks

* [x] Create project directory
* [x] Create Python virtual environment
* [ ] Establish Git repository
* [ ] Create `.gitignore`
* [ ] Install Python dependencies
* [ ] Verify Python environment
* [ ] Verify LangChain installation
* [ ] Verify Chroma installation
* [ ] Verify local model tooling

### Initial project structure

```text
local-rag/
│
├── data/
│   │
│   ├── raw/
│   │   └── ruby/
│   │       └── 3.4/
│   │
│   ├── processed/
│   │   └── ruby/
│   │       └── 3.4/
│   │
│   └── chroma/
│
├── models/
│
├── src/
│   ├── ingestion/
│   ├── retrieval/
│   ├── generation/
│   └── rag/
│
└── tests/
│
├── .gitignore
├── requirements.txt
└── README.md
```

---

# 5. Phase 2 — Run a Local LLM

## Objective

Get Qwen3-8B running locally before introducing RAG.

### Model

**Qwen3-8B**

Use a quantized GGUF version appropriate for the available hardware.

### Tasks

* [ ] Download model
* [ ] Install/configure llama.cpp
* [ ] Verify CPU inference
* [ ] Investigate Intel Arc/Vulkan acceleration
* [ ] Run basic prompt
* [ ] Measure tokens/second
* [ ] Determine appropriate context size
* [ ] Determine appropriate quantization level

### Success criteria

The following should work without LangChain or Chroma:

```text
Python → llama.cpp → Qwen3-8B → response
```

---

# 6. Phase 3 — Understand Embeddings

## Objective

Understand what an embedding is and how it is used for semantic search.

### Model

**BGE-small-en-v1.5**

### Tasks

* [ ] Download embedding model
* [ ] Generate an embedding for a sentence
* [ ] Inspect embedding dimensions
* [ ] Generate embeddings for multiple sentences
* [ ] Compare semantic similarity
* [ ] Understand cosine similarity
* [ ] Test embedding performance locally

### Example concept

```text
"What is SSH?"
       │
       ▼
Embedding model
       │
       ▼
[0.014, -0.083, 0.021, ...]
```

The resulting vector represents semantic characteristics of the text.

---

# 7. Phase 4 — Document Ingestion

## Objective

Convert local documentation into searchable chunks.

### Initial document format

Start with **Markdown and plain-text files**.

PDF and HTML support can be added afterward.

### Pipeline

```text
Document
   │
   ▼
Load
   │
   ▼
Split into chunks
   │
   ▼
Generate embeddings
   │
   ▼
Store in Chroma
```

### Tasks

* [ ] Load local documents
* [ ] Examine document metadata
* [ ] Implement text chunking
* [ ] Experiment with chunk size
* [ ] Experiment with chunk overlap
* [ ] Generate embeddings
* [ ] Store chunks in Chroma
* [ ] Store useful metadata

### Example metadata

```python
{
    "source": "docs/linux/networking.md",
    "section": "DNS Configuration",
    "chunk": 4
}
```

---

# 8. Phase 5 — ChromaDB

## Objective

Understand Chroma as the vector storage/retrieval layer.

### Tasks

* [ ] Create persistent Chroma collection
* [ ] Insert document chunks
* [ ] Store embeddings
* [ ] Store metadata
* [ ] Query collection
* [ ] Retrieve top-k results
* [ ] Inspect similarity scores
* [ ] Verify persistence after restarting Python

### Important distinction

The original documents remain in:

```text
docs/
```

Chroma stores the searchable representation:

```text
chroma_db/
```

The system should retain enough metadata to identify where each retrieved chunk originated.

---

# 9. Phase 6 — Build Semantic Retrieval

## Objective

Answer the question:

> "Given a user question, which pieces of my documentation are relevant?"

### Pipeline

```text
User Question
      │
      ▼
Embedding Model
      │
      ▼
Query Vector
      │
      ▼
Chroma Similarity Search
      │
      ▼
Top-K Document Chunks
```

### Tasks

* [ ] Convert question into embedding
* [ ] Query Chroma
* [ ] Retrieve top-k chunks
* [ ] Display retrieved chunks
* [ ] Display source metadata
* [ ] Experiment with `k`
* [ ] Experiment with similarity thresholds
* [ ] Evaluate retrieval quality manually

### Initial target

Before involving the LLM, the system should be able to do:

```text
Question:
"How do I configure DNS?"

Retrieved:

1. docs/networking/dns.md
2. docs/networking/resolv.conf.md
3. docs/networking/networkmanager.md
```

This is an important milestone.

---

# 10. Phase 7 — Add Qwen3-8B

## Objective

Give the local LLM the relevant documentation retrieved from Chroma.

### Pipeline

```text
                    ┌───────────────┐
                    │ User Question │
                    └───────┬───────┘
                            │
                            ▼
                    Embedding Model
                            │
                            ▼
                       ChromaDB
                            │
                            ▼
                    Relevant Chunks
                            │
                            ▼
                 ┌────────────────────┐
                 │ Prompt Construction│
                 └─────────┬──────────┘
                           │
                           ▼
                       Qwen3-8B
                           │
                           ▼
                         Answer
```

### Prompt concept

The LLM should receive:

```text
SYSTEM:
Answer questions using the supplied documentation.
If the answer cannot be found in the documentation,
say that you do not have enough information.

CONTEXT:
[retrieved documentation]

QUESTION:
[user question]
```

### Tasks

* [ ] Construct RAG prompt
* [ ] Pass retrieved context to Qwen
* [ ] Generate response
* [ ] Test questions with known answers
* [ ] Test questions not covered by documentation
* [ ] Prevent unsupported answers where possible

---

# 11. Phase 8 — Introduce LangChain

## Objective

Once the underlying components work independently, use LangChain to simplify orchestration.

### LangChain responsibilities

Potentially use LangChain for:

* Document loaders
* Text splitters
* Embedding interfaces
* Chroma integration
* Prompt templates
* Retriever interfaces
* LLM interfaces
* RAG chains

### Learning objective

Understand the difference between:

```text
What LangChain is doing
```

and:

```text
What is actually happening underneath
```

The system should remain understandable without LangChain.

---

# 12. Phase 9 — Evaluation

## Objective

Determine whether the RAG system is actually retrieving useful information.

Create a small test set.

### Example

```text
Question:
"What command starts the SSH service?"

Expected source:
docs/linux/ssh.md

Expected answer:
systemctl start sshd
```

Create approximately 20–50 questions covering:

* Easy questions
* Questions requiring multiple chunks
* Questions with similar terminology
* Questions not contained in the documentation
* Questions where irrelevant documents contain similar words

### Evaluate

* Retrieval accuracy
* Source relevance
* Answer accuracy
* Hallucination rate
* Response latency
* Token generation speed

---

# 13. Phase 10 — Experimentation

Once the basic RAG system works, experiment with individual components.

## Embedding models

Compare:

* BGE-small-en-v1.5
* BGE-base-en-v1.5
* Nomic Embed Text

## LLMs

Compare:

* Qwen3-8B
* Llama 3.1 8B
* Other small local models

## Chunking

Experiment with:

```text
256 tokens
512 tokens
1024 tokens
```

and different overlap values.

## Retrieval

Experiment with:

```text
top_k = 2
top_k = 4
top_k = 6
top_k = 10
```

## Prompting

Compare:

* Basic context injection
* Explicit source citations
* Instructions against hallucination
* Structured answers

---

# 14. Future Enhancements

These should **not** be part of the initial implementation.

Potential future features:

* [ ] PDF ingestion
* [ ] HTML documentation ingestion
* [ ] Automatic document updates
* [ ] Source citations in responses
* [ ] Hybrid keyword + vector search
* [ ] Reranking
* [ ] Query rewriting
* [ ] Conversation history
* [ ] Streaming responses
* [ ] Web UI
* [ ] CLI interface
* [ ] Document management interface
* [ ] RAG evaluation framework
* [ ] Agent/tool integration
* [ ] Multiple vector collections
* [ ] Authentication
* [ ] Containerization

---

# 15. Initial Technology Stack

| Component        | Initial Choice     |
| ---------------- | ------------------ |
| OS               | Omarchy Linux      |
| Language         | Python             |
| LLM              | Qwen3-8B           |
| LLM quantization | 4-bit GGUF         |
| LLM runtime      | llama.cpp          |
| Embeddings       | BGE-small-en-v1.5  |
| Vector database  | ChromaDB           |
| RAG framework    | LangChain          |
| Source documents | Local filesystem   |
| Interface        | CLI initially      |
| GPU acceleration | Intel Arc / Vulkan |
| Cloud APIs       | None               |

---

# 16. Definition of Done — Version 1

Version 1 will be considered complete when the following works:

```text
$ python rag.py

Question: How do I configure DNS?

Answer:
[Answer generated by local Qwen3-8B using
locally retrieved documentation.]

Sources:
- docs/networking/dns.md
- docs/networking/networkmanager.md
```

The entire process should occur locally:

```text
                    NO CLOUD APIs
                         │
                         ▼
┌──────────────────────────────────────────┐
│                                          │
│ Local Documents                          │
│       ↓                                  │
│ BGE-small Embeddings                     │
│       ↓                                  │
│ ChromaDB                                 │
│       ↓                                  │
│ Retrieval                                │
│       ↓                                  │
│ Qwen3-8B                                 │
│       ↓                                  │
│ Answer                                   │
│                                          │
└──────────────────────────────────────────┘
```

## Primary learning objectives

By the end of Version 1, I should understand:

1. What embeddings are.
2. How semantic similarity works.
3. How documents are chunked.
4. How vectors are stored in Chroma.
5. How retrieval works.
6. How retrieved context gets passed to an LLM.
7. Why RAG systems sometimes retrieve the wrong information.
8. How LangChain abstracts these operations.
9. How to replace individual components.
10. How to evaluate and improve a RAG system.
