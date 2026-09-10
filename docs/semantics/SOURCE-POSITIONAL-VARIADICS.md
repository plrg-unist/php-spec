# Positional variadic receives

The paired compiler102/runtime103 supports a final variadic parameter on currently
executable named functions, positional value/reference sends, supported scalar and
container types, caller strictness and fixed-prefix defaults. Named binding,
argument unpacking and caught exceptions remain required separate core work.
The separately accepted parser prerequisite brings defaulted-variadic syntax to
existing checked signature diagnostics; native parsing is distinct from lint.

Function frames retain the sent tail operand slots in EXTRA alongside the packed
variadic array. Fixed receives finish first, then each tail verifies and appends
in order. Coercion updates its value slot or shared reference cell before the next
tail; a later failure can expose earlier coercions, including changes to an
already-received fixed parameter sharing that cell. Empty tails perform no element
verification and preserve independent observable reference/COW behavior. Native
uses an immutable empty array; internal abstract allocation IDs are not PHP
identity. Frame cleanup releases extras before the caller's later array copies.

Variadic errors use the actual argument number without a parameter-name suffix.
Missing-prefix wording counts only fixed parameters. Error traces read the fixed
prefix and tail argument slots, including shared cells, rather than exposing
the collected array as an additional argument. Parameter and call instruction
lines retain their separate checked source projections. Reporting masks and
silence scopes follow the accepted suppression protocol through abrupt cleanup.

Finite stage guards bind the actual source function, fixed-slot readiness,
unreceived BEGIN destination, and RECEIVE index/packed container progression.
They preserve arbitrary consistent owning values/cells and do not reconstruct
past coerced values or require fixed parameters to retain earlier verified types.
The original structural-pass failure, trace/arity mismatches and forbidden-stage
counterexamples remain separately bound to their pre-repair inputs.

[Runtime evidence](../../coverage/semantics/variadic-runtime.json) binds28 source
agreements,20 protocol controls/372 assertions,2 dense ownership states/829
assertions,8 selected nonvariadic regressions and8 canonical CLI observations.
The [compiler contract](VARIADIC-COMPILER.md) records23 native phases/194
projections and two explicit catch dependencies. Counts overlap. Independent
acceptance is recorded in [variadic-review.json](../../coverage/semantics/variadic-review.json).

Source and protocol gates retain959/cee5. Final959/4854 changes an older compiler
test's stale variadic expectation and then the dense runner allowance300→900;
each step preserves958 other files and all modes. Both dense fixtures are exactly
the original prepared bytes, with no native rerun or assertion changes. They
passed in459 and369 seconds; the original300-second timeout remains archived.
The [history archive](../../coverage/semantics/variadic-runtime-originals.json)
retains eleven complete input snapshots, raw worker/process envelopes and pinned
engine/binary evidence. It distinguishes setup, structural and interpreter
failures from native disagreement and completed validation.

Named binding next requires destination holes and ordered extra names, with
hole-default preflight before ordinary receives and distinct source/effective
argument counts. Array unpacking and the remaining callable/core obligations
follow; this positional milestone closes no family.
