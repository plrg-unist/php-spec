# Iterator foreach

Module224 adds source `Iterator` objects to ordinary by-value `foreach`. The
callback order is `rewind`, `valid`, `current`, optional `key`, body, then `next`
and `valid`. Keys retain their returned PHP values. Direct by-reference traversal
throws before calling any Iterator method.

Implicit calls select the effective public method, retain its declaring and called
class, and pass zero arguments. Saved foreach continuations authenticate the
selected receiver, source statement, callback stage and diagnostic line. Cursor
continuations require one matching metadata entry below `NEXTITER`; their IDs
must differ across the current task list and saved callers, including same-site
recursive traversal.
The iterator and its actual current result remain owned during `key()` and the body;
a reference result is read after `key()` and its original cell survives rebinding.
Break, return, goto and abrupt frame teardown release the cursor and its owners.

Module230 admits omitted or incompatible tentative returns as deprecations.
Checks follow the actual parent and ordered interface prototypes: source methods
can replace tentative obligations, direct Iterator bindings restore them, and
repeated bindings preserve duplicate notices. The no-argument built-in
`#[ReturnTypeWillChange]` suppressor uses ordinary namespace/import resolution.
Hard signature or constant failures default-report their warning prefix.

Runtime notices run after complete class publication. Early `compile_file`
notices wait for all unit publications and retain their order among existing
compiler warnings. Handler arguments identify the physical method declaration;
callback scope and trace retain the real class opcode or include ingress.
Throwing handlers leave published classes available; remaining diagnostics use
the live handler mask and reporting settings. Nested includes own separate
queues. Source/compiler chronology authenticates batches, and one continuation
owns each runtime publication or file unit across current tasks and saved frames.

Genuine early `eval` diagnostic callbacks remain temporary Unsupported. Their
per-class delivery, later publication after handler throws and pending-exception
fatal priority are the immediate required follow-on. Runtime class declarations
inside completed eval units are admitted. Concrete Traversable-only classes also
await the native core-fatal location (`Unknown`, line0).

`IteratorAggregate`, `ArrayAccess`, Traversable argument/array unpacking and wider
ordinary object/reference traversal remain required. Broader object destruction
and cyclic garbage collection remain unfinished. This milestone does not establish
complete traversal or complete PHP core semantics.

`python3 tests/semantics/user_iterator.py --mode native` checks the authored native
expectations. `python3 tests/semantics/user_iterator_protocol.py --select cursor-claims,cursor-alias`
reaches real callback/body states and rejects duplicate or aliased cursor claims.
`python3 tests/semantics/iterator_declaration_notices.py` checks notice order,
prototype replacement, suppressors, publication and fatal-prefix behavior;
early-eval controls assert only the temporary Unsupported boundary.
Raw native/model commands, outputs, revisions and runtime profiles stay in ignored
`.tools` directories; the harness records each selected run separately.
