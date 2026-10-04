# Iterator foreach

Module224 adds source `Iterator` objects to ordinary by-value `foreach`. The
callback order is `rewind`, `valid`, `current`, optional `key`, body, then `next`
and `valid`. Keys retain their returned PHP values. Direct by-reference traversal
throws before calling any Iterator method.

Implicit calls select the effective public method, retain its declaring and called
class, and pass zero arguments. Saved foreach continuations authenticate the
selected receiver, source statement, callback stage and diagnostic line. The
iterator and its actual current result remain owned during `key()` and the body;
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
