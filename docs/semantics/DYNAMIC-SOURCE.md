# Dynamic source foundation

Target: pinned PHP 8.5.10 CLI NTS64. The checked foreign parser service
accepts raw eval bytes and returns a versioned AST or a separate parser
rejection. Its stateless adapter check establishes shape and request identity;
the runtime must still issue and consume a trusted request from a paused state.

`$compile_source_append` registers a fresh nonzero unit and requires one
matching `SOURCEFILE`, including agreement with the compiler's unit and file
fields. It uses the existing ordered compiler and constant-pool installation
without replacing earlier units, pools or code. It restores the caller's task
continuation and leaves its live variable table, request and owned state in
place. The caller of this helper must later install the new unit's work inside
an eval continuation; the helper alone does not execute it.

Compiler warnings in new units and runtime warnings under a new source origin
carry the unit ID to the observer. Direct static failures and early-declaration
fatals retain that source identity as their terminal origin. Unit 0 keeps its
existing event and terminal representation. The focused registry fixture uses
checked file-mode ASTs for successful and direct-static units. Its namespace
branch composes two separately checked AST nodes only to exercise an internal
compiler failure path; the parser rejects those combined original bytes.
The [foundation ledger](../../coverage/semantics/dynamic-source-foundation.json)
binds the checked-unit fixture, unchanged main-source traces and pinned native
duplicate-declaration probes.

The separate [reached eval increment](DYNAMIC-EVAL.md) builds on this
compiler/registry foundation. Include/require and once identity still require
separate source-provider increments; this foundation alone does not execute a
dynamic source.

Selected nonowning positional `defined`/`constant` queries for the exact
`__COMPILER_HALT_OFFSET__` name use the API call site's compiled filename.
The first completed root-terminal HALT unit with no compilation reentry supplies
its offset; later units with that filename cannot replace it. Direct constant
reads still fold the current AST's offset, so repeated eval can return different
runtime and direct values. A fixed builtin `defined` with one raw string literal
and no namespace fallback follows Zend's ordinary-table quick check and returns
false, even in a HALT file.

The existing authenticated declaration journal supplies chronology. Accepted
HALT occurrences outside the canonical root shape, or earlier incomplete/failed
or reentrant HALT compilations, yield `Unsupported`; completion is sufficient
evidence here, not a claim that registration always waits for compilation to end.
Genuine parser rejection contributes no registration. Captured query strings and
selected-call receipts retain the existing structural variable-input policy.
An authenticated absent registration for the call site's filename raises the
ordinary `Error` for a nonowning positional call through a selected `constant`
callable with `'__COMPILER_HALT_OFFSET__'` as its argument. The Error has its
`constant` frame and original argument. An included
file's registration does not supply the caller's lookup; a main-file
registration does not supply an eval unit's lookup. The
[absent-lookup ledger](../../coverage/semantics/halt-absent-review.json) records
four native/model source agreements and three reached-state checks. Incomplete
or ambiguous registration remains `Unsupported`.
A fixed call with compiled global name `constant`, no namespace fallback and one
raw `'__COMPILER_HALT_OFFSET__'` string argument now uses the same filename-local
offset or absent-registration `Error`. The
[fixed-call ledger](../../coverage/semantics/halt-fixed-review.json) records four
new exact source agreements and reached main/include/eval call fronts. Other
fixed arguments, owning/named/unpacked calls and broader
compiler-failure/reentry behavior remain open. A bare `constant` call in an
ordinary namespace also uses that path when its compiled primary name has no
user-function target and its compiled fallback is global `constant`. The
namespaced user function takes priority when present. The
[namespace-call ledger](../../coverage/semantics/halt-namespace-review.json)
records main/child filename isolation, the absent Error and its trace, and
three reached fallback fronts. Variable arguments, repeated call-site cache
history and ambiguous HALT registration remain partial. The
[lookup ledger](../../coverage/semantics/halt-lookup-review.json) binds two original
sources and their reached state checks, keeping counterfactual history/source
projections separate from execution.
