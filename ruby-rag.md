# Local RAG System — Project Plan

## 1. Project Purpose

Build a basic **Retrieval-Augmented Generation (RAG)** system in Python that can answer questions using a locally stored collection of documentation.

The entire system should run locally without sending documents, embeddings, prompts, or other project data to cloud APIs.

The project is also intended as a hands-on learning exercise. The goal is to develop an understanding of the major components of a RAG system and how they interact, while building a working system incrementally and keeping each major component understandable and testable.

---

## 2. Scope

### Version 1

Version 1 will include:

* A Python-based local RAG system.
* **Ruby 3.4.10** as the initial documentation corpus.
* A deliberately limited initial corpus that is small enough to inspect and understand manually.
* Local document processing, embedding, vector storage, retrieval, and LLM generation.
* A command-line interface for submitting questions and receiving answers.
* A stable initial set of questions for evaluating changes to the retrieval pipeline.

### Constraints

* The system will run locally.
* No cloud APIs will be used for document processing, embeddings, retrieval, or LLM generation.
* The system will be developed incrementally, with major components remaining independently understandable and testable.

### Outside the Initial Scope

The initial implementation will not include:

* Broad support for additional document formats or automated document ingestion.
* Advanced retrieval techniques such as hybrid search or reranking.
* Conversational history and related multi-turn features.
* Web-based interfaces or interfaces beyond the initial CLI.
* Agent or tool integration.
* Authentication, containerization, or other production-oriented deployment features not necessary for understanding and validating the basic RAG pipeline.

The initial corpus, including the specific Ruby source files selected and the process used to extract and normalize their documentation, will be documented separately.

---

## 3. Development Methodology

The project will prioritize **understanding how RAG works** over building the most sophisticated system possible.

Development will be **human-directed and LLM-guided**. ChatGPT will serve as a technical guide, teacher, and pair programmer by explaining concepts, proposing approaches, and providing code. The user will run the code locally, inspect the results, make implementation decisions, and direct the next step. The project will not use an autonomous coding agent.

Development will follow these principles:

* Build incrementally, validating each major stage before moving to the next.
* Keep components understandable and independently testable.
* Avoid unnecessary abstractions during the initial implementation.
* Understand underlying operations before relying on higher-level abstractions such as LangChain.
* Keep major components replaceable so individual models or technologies can be changed and evaluated later.
* Prefer a simple implementation that can be understood end-to-end over a more sophisticated implementation whose behavior is difficult to explain or inspect.
* Use stable evaluation questions to validate changes to the system and distinguish improvements from regressions.

The project should evolve through experimentation and observation. Implementation decisions should be informed by what the system actually does, rather than assuming that higher-level abstractions will behave as expected.

---

## 4. Architecture

The system will be organized as a sequence of distinct stages:

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
Local LLM
      ↓
Response
```

The major architectural components are:

* **Documentation:** The authoritative source material used by the system.
* **Document Processing:** Converts source material into clean, usable documentation units.
* **Text Chunking:** Divides documentation into units suitable for embedding and retrieval.
* **Embeddings:** Converts chunks and queries into vector representations for semantic similarity.
* **Vector Store:** Stores embeddings, document chunks, and associated metadata.
* **Retrieval:** Uses semantic similarity to identify relevant documentation for a question.
* **Generation:** Passes the question and retrieved context to the local LLM to produce a response.

The original documentation will remain separate from the vector store so that source material can be inspected, reprocessed, or replaced independently of the retrieval database.

Each major stage should remain independently testable and replaceable. Detailed implementation decisions for document processing, chunking, embeddings, vector storage, retrieval, and generation will be maintained in relevant child specifications rather than in this parent document.

---

## 5. Tech Stack

The following technologies and environment represent the initial implementation baseline:

| Component            | Initial Choice     |
| -------------------- | ------------------ |
| Operating system     | Omarchy Linux      |
| Programming language | Python             |
| LLM                  | Qwen3-8B           |
| LLM format           | Quantized GGUF     |
| LLM quantization     | 4-bit              |
| LLM runtime          | llama.cpp          |
| Embedding model      | BGE-small-en-v1.5  |
| Vector database      | ChromaDB           |
| RAG framework        | LangChain          |
| Source documents     | Local filesystem   |
| Interface            | CLI initially      |
| GPU acceleration     | Intel Arc / Vulkan |
| Cloud APIs           | None               |

The initial hardware environment is an **Acer Aspire A14** with an **Intel Core Ultra 9 288V**, **Intel Arc integrated graphics**, and **32 GB RAM**.

These are initial technology choices rather than permanent architectural commitments. Components should remain replaceable where practical so that alternatives can be evaluated later.

---

## 6. Roadmap

The project will be developed incrementally through the following major stages:

1. **Environment** — Establish the Python development environment, repository structure, dependencies, and local tooling.
2. **Local LLM** — Get Qwen3-8B running independently and understand the basic local inference workflow.
3. **Embeddings** — Generate and inspect embeddings and develop an understanding of semantic similarity.
4. **Documentation Processing** — Extract, clean, normalize, and validate the initial Ruby documentation corpus.
5. **Vector Storage** — Chunk the processed documentation, generate embeddings, and store the searchable representation in ChromaDB.
6. **Semantic Retrieval** — Build and independently evaluate retrieval of relevant documentation from user questions.
7. **RAG Generation** — Pass retrieved context to Qwen3-8B and produce answers grounded in that context.
8. **LangChain Integration** — Introduce LangChain after the underlying components are understood and working independently.
9. **Evaluation** — Use the stable question set to evaluate retrieval and answer quality and identify weaknesses.
10. **Experimentation** — Experiment with individual components such as models, chunking, retrieval parameters, and prompting.

Each stage should produce a usable and testable milestone before the project proceeds to the next stage. Detailed tasks, implementation decisions, experiments, and current progress will be maintained outside the parent specification.
