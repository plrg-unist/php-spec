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
