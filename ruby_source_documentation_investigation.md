# Ruby Source Documentation Investigation

## Documentation searched

The Ruby 3.4.10 source repository was inspected to identify authoritative source documentation for six initial RAG test questions:

1. `Array#map` vs. `Array#each`
2. `Hash#fetch` behavior when a key does not exist
3. Reading a file line-by-line in Ruby
4. `Enumerable#select` return value
5. Blocks passed to methods
6. `require` vs. `require_relative`

Initial inspection of `doc/` showed several categories, including historical changelogs, release notes, contributor documentation, examples, focused API documentation, and language syntax documentation.

The investigation established that much of Ruby's Core API documentation is embedded as RDoc comments directly in the Ruby source files rather than existing entirely under `doc/`.

## What we found

### `array.c`

Contains RDoc for `Array#map` and `Array#map!`, including method signatures and examples.

It also showed that `Array#map` is registered as:

```text
rb_define_method(rb_cArray, "map", rb_ary_collect, 0);
```

### `enum.c`

Contains RDoc for `Enumerable#select`, including:

```text
select {|element| ... } -> array
select -> enumerator
```

and the description that it returns an array containing elements selected by the block.

It also defines `Enumerable#map`.

### `hash.c`

Contains RDoc for `Hash#fetch`, including three forms:

```text
hash.fetch(key) -> object
hash.fetch(key, default_value) -> object
hash.fetch(key) {|key| ... } -> object
```

The documentation includes examples for default values and block handling.

### `io.c`

Contains RDoc for `IO#each_line`, including multiple signatures and examples:

```text
each_line(sep = $/, chomp: false) {|line| ... } -> self
each_line(limit, chomp: false) {|line| ... } -> self
each_line(sep, limit, chomp: false) {|line| ... } -> self
each_line -> enumerator
```

It also shows that `IO#each` and `IO#each_line` use the same implementation.

### `doc/syntax/methods.rdoc`

Contains language-level documentation for block arguments. The relevant section is:

```text
=== Block Argument
```

It explains the `&` block argument, passing blocks to other methods, and related block handling.

### `load.c`

Contains the documentation and implementation for `require_relative`, including:

```text
require_relative(string) -> true or false
```

The file also registers both loading functions as global functions:

```text
rb_define_global_function("require", rb_f_require, 1);
rb_define_global_function("require_relative", rb_f_require_relative, 1);
```

## Initial raw source file set

The source files selected for the initial raw documentation dataset are:

```text
array.c
enum.c
hash.c
io.c
load.c
doc/syntax/methods.rdoc
```

These files should be treated as source material, not as the final documents placed into the vector database.

## Next step

Write a small Python extraction script that reads the selected Ruby source files and extracts the relevant RDoc documentation from them.

The intended pipeline is:

```text
Ruby source files
       ↓
extract RDoc comments
       ↓
clean / normalize documentation
       ↓
save processed documentation
       ↓
inspect resulting documents
```

The important design choice is to inspect and validate the extracted documentation before adding embeddings, LangChain, or ChromaDB.

The extraction step should produce clean, semantic documentation units (for example, an `Array#map` document containing its signature, description, and examples) rather than embedding entire C source files containing implementation details that are irrelevant to the initial questions.
