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

Ordinary named functions with by-value returns and scalar control stacks can
also jump into or back within a supported declare body. The new container arm
uses its existing `[PCFIELD 1]` statement origins and the unchanged continuation;
it does not rerun directives or skipped statements. A backward jump inside a
loop reuses that exact loop marker, without repeating its condition. Current
and saved callers must have genuine ordinary function-call source links. Scalar
CV contents are checked through STORE while their cells retain ordinary owners.
Registered tick callbacks, protected source/target/caller regions, owning or reference
buffers, resumable and cleanup contexts gain no new route. Two `ticks=0` originals
and focused source/budget checks are recorded in the
[plain-declare goto review](../../coverage/semantics/plain-goto-declare-review.json).

The rules live in `128-goto-compiler.watsup` and `129-goto-runtime.watsup`.
[The review](../../coverage/semantics/goto-review.json) records source, static,
descriptor and paused-state checks. `try`/`finally` jumps and the broader
exception protocol remain unfinished.
