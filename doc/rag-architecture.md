# RAG Architecture

## 1. Purpose

This document defines the detailed architecture of the local RAG system.

The parent project specification defines the system at a high level. This document expands that architecture by describing the responsibilities and relationships of the major components.

Implementation details may evolve as the system is developed and tested, but the major component boundaries should remain understandable and independently testable.

---

## 2. System Architecture

The initial system follows this conceptual pipeline:

```text
Documentation
      ↓
Document Processing
      ↓
Text Chunking
      ↓
Embeddings
      ↓
Vector Store
      ↓
Similarity Retrieval
      ↓
Relevant Context
      ↓
Prompt Construction
      ↓
Local LLM
      ↓
Response
```

The system is intended to run entirely on the local machine.

---

## 3. Architectural Components

### 3.1 Documentation

Documentation is the authoritative source material from which the searchable corpus is created.

For the initial implementation, the source corpus is Ruby 3.4.10 documentation extracted from the selected Ruby source files and RDoc comments.

The original source material must remain separate from the processed and vectorized representations.

See `corpus.md` for corpus definition and source-processing details.

---

### 3.2 Document Processing

Document processing transforms raw source material into clean, semantic documentation units suitable for later processing.

Responsibilities include:

* extracting relevant documentation from source files
* cleaning and normalizing extracted content
* preserving source information
* assigning relevant metadata
* producing semantic documentation units
* validating the processed output

The extraction stage should be independently testable before embeddings, ChromaDB, or LangChain are introduced.

The detailed corpus-processing design is maintained in `corpus.md`.

---

### 3.3 Text Chunking

Chunking converts processed documentation units into units appropriate for embedding and retrieval.

Chunking is intentionally separate from document extraction.

A semantic documentation unit should first represent a coherent piece of information; chunking can then divide that material as necessary for retrieval.

Chunking strategy, chunk size, overlap, and related experiments should be treated as implementation decisions rather than fixed architectural assumptions.

---

### 3.4 Embeddings

The embedding component converts documentation chunks into vector representations and converts user questions into vectors suitable for similarity comparison.

The initial embedding model is:

```text
BGE-small-en-v1.5
```

The embedding component should expose a clear boundary so that alternative embedding models can be evaluated without redesigning the rest of the system.

---

### 3.5 Vector Store

The vector store maintains the searchable representation of the processed documentation.

The initial vector store is:

```text
ChromaDB
```

It should retain:

* document embeddings
* document/chunk content
* associated metadata
* enough source information to identify the origin of retrieved content

The original documentation remains separate from the vector store. The vector store is a derived representation that can be rebuilt from the source corpus. This separation is an explicit architectural principle of the project.

---

### 3.6 Retrieval

Retrieval determines which documentation is relevant to a user question.

The initial retrieval flow is:

```text id="s3gqjc"
User Question
      ↓
Question Embedding
      ↓
Query Vector
      ↓
Similarity Search
      ↓
Top-K Document Chunks
```

Retrieval should be independently testable before the generation stage is introduced.

The retrieval component should expose the retrieved content and associated metadata so that retrieval quality can be inspected directly.

Initial retrieval experiments may include parameters such as `k` and similarity thresholds.

---

### 3.7 Context Construction

The retrieved chunks are assembled into the context supplied to the LLM.

The context-construction stage is distinct from retrieval:

```text
Retrieval
    ↓
Relevant chunks
    ↓
Context construction
    ↓
LLM prompt
```

This separation allows retrieval quality and prompt/context construction to be evaluated independently.

The initial system should prefer straightforward context construction that remains easy to inspect.

---

### 3.8 Generation

The generation component uses the user's question and retrieved documentation to produce the final response.

The initial local LLM is:

```text
Qwen3-8B
```

with local inference provided by:

```text
llama.cpp
```

The generation stage should receive explicitly defined inputs rather than reaching directly into the vector store or source corpus.

At a conceptual level:

```text"
Question
   +
Retrieved Context
   ↓
Prompt
   ↓
Qwen3-8B
   ↓
Answer
```

The LLM should be treated as the generation component, not as the retrieval mechanism.

---

## 4. Component Boundaries

The major components should maintain clear boundaries:

```text id="pnkv44"
Corpus
  ↓
Document Processing
  ↓
Semantic Documents
  ↓
Chunking
  ↓
Embeddings
  ↓
Vector Store
  ↓
Retrieval
  ↓
Context Construction
  ↓
Generation
```

Each stage should consume defined inputs and produce defined outputs.

This allows an individual stage to be inspected or replaced without requiring the entire system to be rewritten.

---

## 5. Retrieval and Generation Independence

Retrieval and generation should remain separate concerns.

A useful milestone is to be able to run:

```text
Question
   ↓
Retrieval
   ↓
Relevant Chunks
```

without invoking the LLM.

This makes it possible to determine whether a poor final answer resulted from:

* incorrect or incomplete retrieval
* inadequate context construction
* generation behavior
* some combination of these

The evaluation methodology in `evaluation.md` reflects this separation.

---

## 6. Source Data and Derived Data

The architecture distinguishes between authoritative source data and derived representations.

```text id="2e7vjj"
Authoritative Source
       ↓
Processed Documentation
       ↓
Chunks + Metadata
       ↓
Embeddings
       ↓
Vector Store
```

The vector store and embeddings should be considered reproducible outputs of the processing pipeline rather than the authoritative source of documentation.

Changes to extraction, normalization, chunking, metadata, or embedding configuration may therefore require rebuilding downstream representations.

---

## 7. LangChain Boundary

LangChain is an orchestration framework in the initial technology stack, but it should not define the underlying architecture.

The project should first establish an understanding of the underlying operations:

```text
document processing
chunking
embedding
vector storage
retrieval
prompt construction
generation
```

LangChain may then be introduced where it provides useful orchestration or interfaces.

The system should remain conceptually understandable without LangChain.

This follows the project methodology of understanding underlying operations before relying on higher-level abstractions.

---

## 8. Replaceability

Major technology choices should remain replaceable where practical.

Potential replacement points include:

* embedding model
* vector database
* retrieval implementation
* local LLM
* inference runtime
* orchestration framework

Replacement should occur at component boundaries rather than requiring changes throughout the system.

This supports later experimentation while preserving the basic architecture.

---

## 9. Architectural Invariants

The following principles should remain true as the implementation evolves:

1. **Source documentation remains separate from derived vector representations.**
2. **Document processing is independent of retrieval and generation.**
3. **Retrieval can be tested independently of generation.**
4. **Major components have clear boundaries and replaceable interfaces where practical.**
5. **The system remains understandable without relying on LangChain abstractions.**
6. **Derived representations can be rebuilt from the underlying source material.**
7. **The initial implementation favors inspectability and simplicity over unnecessary sophistication.**

---
