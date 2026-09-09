# Runtime source occurrences

The machine retains canonical checked `pcunit` values in `SOURCES`. An optional
`ORIGIN` carries the compiled instance ID and structural occurrence path of the
current task scope. `$php_run` creates unit zero for its initial source;
`$run_source` accepts an explicit canonical unit, and rejects a forged occurrence
catalog. The original `PROGRAM` or `ENCODEDPROGRAM` value remains in that unit.
This stage does not install compiler facts or constant-array pools.

The `execute` transport now requires the actual source filename as canonical
base64 bytes alongside the checked AST and transition budget. `$php_run` decodes
it in the specification and retains `SOURCEFILE unit bytes` in `S.FILES`, including
budget and abrupt results. Empty and NUL-containing filenames are invalid context;
other bytes are preserved, including non-UTF8 filesystem names. Syntax-only
`check` and `elaborate` requests remain independent of this execution context.
File-sensitive PHP constructs are still pending. The compiler bridge must pass
this context into compilation before running tasks; this transport milestone
currently records it around the existing source entry point.

`AT origin task` enters a scope and appends `ORIGIN_RETURN` after its work. Child
expression, acquisition and dimension-preparation tasks carry explicit schema
field/index paths. Continuations execute in their parent's scope. Array literal
iteration uses the current item path and advances its sibling index, without
adding a scope for every item. Empty arrays keep the array expression's scope.
The generated structural traversal defines paths; runtime order remains in the
machine's PHP rules.

Before entering an `AT` scope, the machine finds its unit and path. For a task
that retains a checked node, the selected occurrence must contain that node.
This equality validates a path-selected node; it never chooses an occurrence.
Identical nodes, including equal edited metadata, may occur at distinct paths.
Saved return scopes are internal machine state, not a checked external input API.

Origin wrappers introduce no PHP owners: their root projection is exactly that
of the wrapped task. Source units contain checked syntax, not runtime array or
reference owners. Terminal temporary cleanup clears the active origin but retains
source units. A budget interruption retains both active and saved scopes; resuming
that state must produce the same result as uninterrupted execution. Each scope
transition consumes a driver budget unit, so a numeric execution budget is an
observation bound rather than a count of PHP operations.

Run `python3 tests/semantics/source_origins.py`. Its reusable trace helper records
visited task kind, unit and path, and compares each visited checked node against
an independent schema traversal of the checked AST. The canonical matrix covers
25 original sources, including an original UTF-16LE source whose encoded program
is retained. Explicit path sequences distinguish equal-metadata operand and array
item siblings. Fifteen interruption/resumption checks, invalid unit/path/node
checks and transparent reference-root checks supplement the trace comparisons.
The full source and ownership gates still validate behavior and lifetimes.

The internal [pool installer](COMPILED-POOLS.md) now supplies permanent roots
separate from `HELD` and reserves disjoint allocation IDs. Source execution still
needs to invoke it and consume compiled facts by unit/path. Those roots survive
temporary cleanup; compiled-unit teardown remains pending. The checked compiler traversal
must still visit child arrays normally below an assignment/variable barrier that
stops an enclosing constant-evaluation traversal. Repeated literal execution,
foreach and general control remain pending until these integrations are tested.
