# Labels and goto

The source compiler records labels and goto sites in each top-level unit,
function or closure. Names are case-sensitive and shared across namespace
blocks in that callable. Duplicate labels fail when encountered; unresolved
names and jumps into a loop or switch finalize in the callable's second pass.
Nested callables finish independently, preserving PHP's diagnostic order. The
compiled `CODEGOTO` entry records the exact source and target paths; resumed
source and code are checked against those paths.

A jump reconstructs the continuation from the target occurrence. Entering an
`if` or ordinary block skips guards and statements before the label. A target
inside the current loop, foreach or switch reuses its saved continuation;
jumping outward drops only exited owners. Saved foreach markers authenticate
their source, iterator and selected array or reference mode. Saved switch
markers retain or release the subject value with its heap owner.

The rules live in `128-goto-compiler.watsup` and `129-goto-runtime.watsup`.
[The review](../../coverage/semantics/goto-review.json) records source, static,
descriptor and paused-state checks. `try`/`finally` jumps and the broader
exception protocol remain unfinished.
