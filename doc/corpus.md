# Corpus and Document Extraction

## 1. Purpose

This document defines the initial document corpus and the process used to transform Ruby source material into clean, semantic documentation units for the RAG system.

It describes:

* where the source documentation comes from
* why the initial corpus is intentionally limited
* how raw source files are transformed into processed documentation
* what information should be preserved during extraction
* how classification and topic tagging fit into document processing

The detailed classification taxonomy is maintained separately in `document-classification.md`.

---

## 2. Initial Corpus

The initial documentation target is **Ruby 3.4.10**.

Before building the ingestion pipeline, the Ruby 3.4.10 source repository was inspected to determine where the documentation relevant to the initial test questions actually resides.

The investigation found that much of Ruby's Core API documentation is embedded directly in the Ruby source files as **RDoc comments**, rather than existing entirely as standalone documentation files under `doc/`.

The relevant Ruby source files are therefore treated as the authoritative raw documentation sources for the initial corpus.

### Documentation Sources

| Source                    | Relevant documentation                                                                     |
| ------------------------- | ------------------------------------------------------------------------------------------ |
| `array.c`                 | `Array#map` and `Array#map!`, including signatures and examples                            |
| `enum.c`                  | `Enumerable#map` and `Enumerable#select`, including signatures, descriptions, and examples |
| `hash.c`                  | `Hash#fetch`, including missing-key behavior, default values, block form, and examples     |
| `io.c`                    | `IO#each_line`, including signatures and examples for reading lines                        |
| `load.c`                  | `require` and `require_relative`                                                           |
| `doc/syntax/methods.rdoc` | Ruby method/block documentation, including block arguments and passing blocks to methods   |

The initial investigation also identified relationships useful for retrieval testing. For example, `Array#map` is defined on `Array` while `Enumerable` also defines `map`, and `IO#each` and `IO#each_line` use the same implementation.

---

## 3. Corpus Boundaries

The initial corpus deliberately does **not** include the entire Ruby source repository.

The six selected files provide the documentation needed for the initial test questions while keeping the corpus small enough to inspect and understand manually.

The initial corpus may expand later, but additions should be deliberate and should preserve the project's ability to inspect and evaluate the processed documentation.

### Raw Source Set

The initial raw dataset is:

```text
data/raw/ruby/3.4/
├── array.c
├── enum.c
├── hash.c
├── io.c
├── load.c
└── doc/syntax/methods.rdoc
```

The relative source path of `doc/syntax/methods.rdoc` should be preserved when the file is copied into the raw dataset.

---

## 4. Raw Sources vs. Processed Documents

The selected Ruby source files are **raw source material**, not the final documents used for retrieval.

The C source files contain useful RDoc mixed with implementation details that are irrelevant to many of the initial questions. The ingestion process should therefore extract the relevant documentation rather than treating entire source files as individual RAG documents.

The processed corpus should consist of clean, semantic documentation units suitable for later chunking and embedding.

For example, an extracted `Array#map` unit should contain the relevant method signature, description, examples, and associated source information rather than an entire `array.c` file.

---

## 5. Document Extraction Pipeline

The initial corpus-processing pipeline is:

```text
Ruby source / RDoc
        ↓
Extract relevant documentation
        ↓
Clean / normalize
        ↓
Classify / tag
        ↓
Create semantic documentation units
        ↓
Inspect / validate
        ↓
Text chunking
        ↓
Embeddings
```

The extraction and normalization stages should be developed and tested independently before introducing embeddings, ChromaDB, or higher-level orchestration.

The processed documents should be inspected before they are used for retrieval so that extraction problems can be identified separately from later retrieval problems.

---

## 6. Semantic Documentation Units

The extraction process should produce units organized around meaningful pieces of documentation rather than arbitrary source-file boundaries.

A semantic unit may represent information such as:

* a class or module
* a method
* a group of related methods
* a language-level concept
* an implementation concept
* another coherent piece of information useful for retrieval

The appropriate granularity should be determined through inspection and experimentation rather than fixed in advance.

These semantic units become the source material for later chunking.

---

## 7. Classification and Topic Metadata

Extracted information may be assigned metadata that helps describe its role and subject.

Two concepts should remain distinct:

**Classification** answers:

> What role does this information play?

**Topic** answers:

> What Ruby concept is this information about?

Classification should remain relatively small and stable, while topics may become more specific as the corpus grows.

A single semantic unit may therefore have one primary classification and multiple topics.

For example:

```json
{
  "classification": "API_DOCUMENTATION",
  "topics": [
    "array indexing",
    "slicing",
    "ranges"
  ]
}
```

The detailed taxonomy, classification rules, and examples are maintained in:

```text
docs/document-classification.md
```

---

## 8. Source and Context Metadata

Processed documentation should preserve enough information to identify its origin and describe its context.

Potential metadata includes:

```text
classification
topics
methods
classes
modules
source_file
source_language
ruby_version
source_location
visibility
implementation_layer
```

Not every field needs to exist for every documentation unit.

The embedding should primarily represent the textual content of the documentation unit, while metadata should remain available for inspection and for later retrieval strategies such as filtering or metadata-aware retrieval.

---

## 9. Validation

Processed documentation should be inspected and validated before embeddings and vector storage are introduced.

Validation should confirm that:

* relevant documentation was extracted
* irrelevant implementation material was not unintentionally included
* semantic units are coherent
* source information was preserved
* metadata is accurate where present
* documentation is understandable independently of the original source-file context

The goal of this stage is to establish a trustworthy processed corpus before introducing later stages of the RAG pipeline.
