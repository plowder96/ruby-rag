# RAG Evaluation

## 1. Purpose

This document defines the initial evaluation approach for the Ruby RAG system.

The evaluation process is intended to determine whether changes to document extraction, chunking, embeddings, metadata, retrieval, and generation improve the system or introduce regressions.

The initial evaluation approach is deliberately lightweight. More formal metrics and larger test sets can be introduced later as the system develops.

---

## 2. Golden Questions

These six questions define the initial **golden question set** used to evaluate the documentation extraction and retrieval pipeline:

1. **What is the difference between `Array#map` and `Array#each`?**
2. **How does `Hash#fetch` behave when the key doesn't exist?**
3. **How do I read a file line-by-line in Ruby?**
4. **What does `Enumerable#select` return?**
5. **How does Ruby handle blocks passed to methods?**
6. **What is the difference between `require` and `require_relative`?**

These questions exercise several retrieval situations:

* API documentation
* method signatures
* examples
* return values
* missing-key behavior
* language-level concepts
* relationships between related APIs

The golden questions should remain stable during initial development so that changes to extraction, chunking, embeddings, metadata, or retrieval parameters can be evaluated against the same known questions.

---

## 3. Evaluation Stages

Evaluation should distinguish between **retrieval quality** and **answer quality**.

### Retrieval Evaluation

First determine whether the system retrieved documentation that is relevant to the question.

```text
Question
   ↓
Retrieve document chunks
   ↓
Inspect retrieved content and metadata
   ↓
Assess relevance
```

The purpose is to determine whether the corpus and retrieval pipeline are supplying the information needed to answer the question.

### Answer Evaluation

Once retrieval is established, determine whether the generated answer correctly uses the retrieved documentation.

```text
Question
   ↓
Retrieved documentation
   ↓
Generate answer
   ↓
Compare answer with source documentation
```

This distinction is important when diagnosing problems. A poor answer may result from poor retrieval, poor generation, or both.

---

## 4. Initial Evaluation Procedure

For each golden question:

1. Submit the question to the retrieval system.
2. Inspect the retrieved chunks and their source metadata.
3. Determine whether the retrieved information is relevant to the question.
4. Generate an answer using the retrieved context.
5. Compare the answer with the retrieved documentation.
6. Record notable successes, failures, or unexpected behavior.

During early development, evaluation may be performed manually rather than through an automated scoring system.

---

## 5. Evaluation Principle

The evaluation set should remain stable while individual components of the system are changed.

When experimenting with:

* document extraction
* semantic-document structure
* classification or metadata
* chunking
* embedding models
* retrieval parameters
* prompting
* generation models

the same golden questions should be used to determine whether the change affects system behavior.

The goal is to distinguish actual improvements from regressions rather than relying on individual examples or subjective impressions.

---

## 6. Future Evaluation Expansion

The initial six-question set is intentionally small.

As the basic RAG pipeline becomes functional, the evaluation set may be expanded to include additional question types, such as:

* questions requiring multiple document chunks
* questions involving similar terminology
* questions whose answers are not present in the corpus
* questions where irrelevant documentation contains similar terms

More formal evaluation metrics and automated evaluation can be introduced later when they become useful.
