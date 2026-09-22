# Ruby Source Q/A RAG Classification Approach

## 1. Purpose

This document defines the current approach for classifying and tagging information extracted from the Ruby source code and RDoc comments for use in a basic question-answering (Q/A) RAG system centered on the Ruby programming language.

The goal is **retrieval usefulness**, not exhaustive documentation of every possible semantic distinction. Classification should help the retrieval system distinguish *what role a piece of information plays*, while topics and other metadata capture *what Ruby concept the information concerns*.

---

## 2. Overall Conceptual RAG Pipeline

The intended pipeline is:

```text
                 Ruby source / RDoc
                        │
                        ▼
              ┌───────────────────┐
              │ Extract / chunk    │
              │ source information │
              └─────────┬─────────┘
                        │
                        ▼
              ┌───────────────────┐
              │ Classify           │
              │ information role   │
              └─────────┬─────────┘
                        │
                        ▼
              ┌───────────────────┐
              │ Extract metadata   │
              │ topics / methods / │
              │ classes / concepts │
              └─────────┬─────────┘
                        │
                        ▼
              ┌───────────────────┐
              │ Store chunk +      │
              │ metadata + vector │
              │ / keyword index   │
              └─────────┬─────────┘
                        │
                 User question
                        │
                        ▼
              ┌───────────────────┐
              │ Retrieve relevant  │
              │ chunks             │
              │ (semantic +        │
              │ metadata/keyword)  │
              └─────────┬─────────┘
                        │
                        ▼
              ┌───────────────────┐
              │ Generate answer    │
              │ grounded in Ruby   │
              │ source material    │
              └───────────────────┘
```

The important design principle is that **classification and topic tagging serve different purposes**.

---

## 3. Classification vs. Topic

### Classification

**Classification answers:**

> What role does this piece of information play?

Classification should use a relatively small, stable taxonomy that generalizes across the Ruby codebase.

Examples:

- API documentation
- Implementation details
- Algorithm descriptions
- Memory / GC behavior
- Optimization rationale
- Runtime safety constraints

Classification should not attempt to describe every Ruby feature mentioned in a chunk.

### Topic

**Topic answers:**

> What Ruby concept is this information about?

Topics should be more specific and can grow as the corpus grows.

Examples:

- array indexing
- ranges
- arithmetic sequences
- permutations
- shared arrays
- copy-on-write
- GC compaction
- write barriers
- defensive copying
- method dispatch
- blocks
- enumerators

A single chunk can have one classification and multiple topics.

For example:

```json
{
  "classification": "IMPLEMENTATION",
  "topics": [
    "array indexing",
    "ranges",
    "arithmetic sequences"
  ]
}
```

This is preferable to creating a separate primary classification such as `INDEXING_RANGES`.

---

## 4. Current Classification Taxonomy

The recommended initial taxonomy contains six primary classifications.

### 4.1 `API_DOCUMENTATION`

Information describing Ruby's public-facing API or user-visible behavior.

Use for:

- classes and methods
- arguments
- return values
- documented behavior
- enumerator behavior
- user-facing semantics

Example:

```json
{
  "classification": "API_DOCUMENTATION",
  "topics": [
    "Array#[]",
    "array indexing",
    "slicing",
    "ranges"
  ]
}
```

---

### 4.2 `IMPLEMENTATION`

General information about how Ruby/MRI implements a feature when the information does not fit a more specific implementation category.

Use for:

- internal data structures
- C-level implementation mechanics
- internal helper behavior
- object representation
- implementation-specific details

This is intentionally broad, but should not become a catch-all when a more specific classification is appropriate.

---

### 4.3 `ALGORITHM`

Information explaining an algorithm or computational procedure used by Ruby.

Use for:

- permutation generation
- combinations
- Cartesian products
- sorting algorithms
- numerical algorithms
- iteration algorithms
- other explicit computational procedures

Example:

```json
{
  "classification": "ALGORITHM",
  "topics": [
    "permutations",
    "enumeration",
    "defensive copying"
  ]
}
```

---

### 4.4 `MEMORY_GC`

Information concerning memory representation, ownership, allocation, garbage collection, object sharing, or related runtime memory behavior.

Use for:

- embedded vs. heap objects
- shared arrays
- copy-on-write
- GC marking
- GC compaction
- write barriers
- pointer ownership
- object lifetime
- allocation behavior
- defensive copies when the important aspect is memory/object ownership

Example:

```json
{
  "classification": "MEMORY_GC",
  "topics": [
    "shared arrays",
    "copy-on-write",
    "GC compaction",
    "write barriers"
  ]
}
```

---

### 4.5 `OPTIMIZATION`

Information explaining performance-oriented implementation choices.

Use for:

- fast paths
- special cases
- avoiding unnecessary work
- cache-related considerations
- optimized comparisons
- allocation avoidance
- performance-driven implementation choices

Example:

```json
{
  "classification": "OPTIMIZATION",
  "topics": [
    "fast path",
    "optimized comparison",
    "cache locality"
  ]
}
```

---

### 4.6 `RUNTIME_SAFETY`

Information describing constraints required to keep execution correct in the presence of Ruby's runtime behavior.

Use for:

- reentrancy
- mutation during callbacks
- frozen objects
- pointer invalidation
- Ruby method calls that can trigger GC
- object movement/evacuation
- subtle interactions between C code and Ruby code

Example:

```json
{
  "classification": "RUNTIME_SAFETY",
  "topics": [
    "reentrancy",
    "array mutation",
    "GC compaction",
    "pointer invalidation"
  ]
}
```

---

## 5. Why `INDEXING_RANGES` Is Not a Primary Classification

`INDEXING_RANGES` was considered during analysis of `array.c`, because many `OTHER` comments concern:

- negative indexes
- ranges
- slicing
- `ArithmeticSequence`
- bounds checking

However, it should **not** be a primary classification.

The reason is that indexing and ranges are **topics/domains**, rather than a general information role.

Similar concepts appear throughout Ruby:

- `Array` — positional indexes and slicing
- `String` — character/byte offsets and slicing
- `Range` — range endpoints and iteration
- `Enumerator` — sequence/iteration behavior
- `Regexp` — match positions and offsets
- `Hash` — key lookup rather than positional indexing

Making `INDEXING_RANGES` a classification would therefore mix together information that may have very different roles.

Instead:

```json
{
  "classification": "IMPLEMENTATION",
  "topics": [
    "array indexing",
    "ranges",
    "arithmetic sequences"
  ]
}
```

or, for user-facing documentation:

```json
{
  "classification": "API_DOCUMENTATION",
  "topics": [
    "array indexing",
    "ranges",
    "slicing"
  ]
}
```

---

## 6. Additional Metadata / Tags

Classification should remain relatively small. More detailed information should be represented through additional metadata.

Potential metadata fields include:

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

Not every field needs to exist for every chunk.

### Example: API-oriented chunk

```json
{
  "classification": "API_DOCUMENTATION",
  "topics": [
    "array indexing",
    "slicing",
    "ranges"
  ],
  "classes": [
    "Array"
  ],
  "methods": [
    "Array#[]"
  ],
  "source_file": "array.c",
  "ruby_version": "3.4"
}
```

### Example: Memory/GC chunk

```json
{
  "classification": "MEMORY_GC",
  "topics": [
    "shared arrays",
    "copy-on-write",
    "GC compaction",
    "embedded arrays"
  ],
  "classes": [
    "Array"
  ],
  "source_file": "array.c",
  "ruby_version": "3.4"
}
```

### Example: Algorithm chunk

```json
{
  "classification": "ALGORITHM",
  "topics": [
    "permutations",
    "enumeration",
    "falling factorial"
  ],
  "classes": [
    "Array"
  ],
  "methods": [
    "Array#permutation"
  ],
  "source_file": "array.c",
  "ruby_version": "3.4"
}
```

### Example: Runtime-safety chunk

```json
{
  "classification": "RUNTIME_SAFETY",
  "topics": [
    "reentrancy",
    "Ruby callbacks",
    "array mutation",
    "pointer invalidation"
  ],
  "source_file": "array.c",
  "ruby_version": "3.4"
}
```

---

## 7. Classification Principles

### Keep the primary taxonomy small

The primary classification should contain categories that remain useful as additional Ruby source files are added.

Prefer:

```text
ALGORITHM
```

over:

```text
PERMUTATION
COMBINATION
CARTESIAN_PRODUCT
```

Prefer:

```text
MEMORY_GC
```

over:

```text
SHARED_ARRAY
COPY_ON_WRITE
GC_COMPACTION
WRITE_BARRIER
```

The more specific concepts belong in `topics`.

### Avoid a generic `MISCELLANEOUS` category

A `MISCELLANEOUS` category provides little retrieval value and tends to become a dumping ground.

If a chunk genuinely does not fit the current taxonomy, that should be treated as a signal to evaluate whether the taxonomy needs to expand.

### Do not overfit the taxonomy to one source file

The initial taxonomy was developed while examining `array.c`. It should therefore be tested against additional Ruby source files before being considered final.

A useful classification should generalize across files such as:

```text
array.c
string.c
hash.c
object.c
enumerator.c
range.c
numeric.c
```

The taxonomy should describe the **role of the information**, while topics describe the **Ruby feature involved**.

---

## 8. Recommended Initial Schema

A simple initial representation could be:

```json
{
  "content": "...",
  "classification": "MEMORY_GC",
  "topics": [
    "shared arrays",
    "copy-on-write"
  ],
  "methods": [
    "Array#..."
  ],
  "classes": [
    "Array"
  ],
  "source_file": "array.c",
  "ruby_version": "3.4"
}
```

The embedding/vector should primarily represent `content`, while metadata can be used to improve retrieval through filtering, boosting, or hybrid search.

---

## 9. Design Objective

The classification system should ultimately help answer questions such as:

> What does this Ruby method do?

→ `API_DOCUMENTATION`

> How does MRI implement this behavior?

→ `IMPLEMENTATION`

> What algorithm does Ruby use here?

→ `ALGORITHM`

> Why does Ruby manage these objects this way?

→ `MEMORY_GC`

> Why is this implementation structured this way for performance?

→ `OPTIMIZATION`

> What runtime hazard is this code protecting against?

→ `RUNTIME_SAFETY`

The system should then use **topics and other metadata** to narrow the retrieval space to the relevant Ruby concept.

The central design principle is:

> **Classification describes the role of the information; topics describe the subject of the information.**

This separation should allow the taxonomy to remain stable while the vocabulary of Ruby-specific topics grows with the corpus.
