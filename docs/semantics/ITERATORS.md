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

Declaration admission currently requires compatible explicit return types.
Internal abstract obligations and inherited virtual prototypes use Iterator's
stub order. Omitted or incompatible tentative return types remain explicit
Unsupported until the immediate declaration-warning follow-on; their native
deprecations must not become signature fatals. Concrete Traversable-only classes
also await the native core-fatal location (`Unknown`, line0).

`IteratorAggregate`, `ArrayAccess`, Traversable argument/array unpacking and wider
ordinary object/reference traversal remain required. Broader object destruction
and cyclic garbage collection remain unfinished. This milestone does not establish
complete traversal or complete PHP core semantics.

`python3 tests/semantics/user_iterator.py --mode native` checks the authored native
expectations. `python3 tests/semantics/user_iterator_protocol.py --select cursor-claims,cursor-alias`
reaches real callback/body states and rejects duplicate or aliased cursor claims.
Raw native/model commands, outputs, revisions and runtime profiles stay in ignored
`.tools` directories; the harness records each selected run separately.
