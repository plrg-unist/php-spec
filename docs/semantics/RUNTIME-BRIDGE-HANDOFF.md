# Runtime compiler bridge handoff

Read PLAN.md, PROGRESS.md, AGENTS.md and the php/php-spec/p4-spectec skills, then
ARRAY-HANDOFF.md, DESIGN.md, SOURCE-COMPILER.md, CONSTANT-CONTEXT.md and DIMENSIONS.md.
The complete PHP core goal remains unfinished. This is a clean author turnover,
not completion of compiler activation, string dimensions, or control flow.

## Accepted checkpoint

Runtime commits: `cb02399c` task origins; `0df3d175` permanent pool installation;
`0270197e` actual filename transport and twelve string-line source regressions.
Compiler commits: `72d3a65d` ordered compiler and effective constant rewrite lines;
`4297dadf` heredoc/nowdoc token-line correction; `00e27843` access descriptors.
There are no uncommitted runtime implementation changes at this handoff.

The final regular source suite passed **526 exact source comparisons + 25 outcome
negatives**, independently repeated. Filename transport passed 16 canonical and 24
independent cases; origins 25/333; pools 24 boundary +100 graphs/1623 assertions,
independent 24 +250/4825; ownership 617 +96/5434. Ordered compiler 561 lint +15 ending
line cases and 8 sources/24 access roles passed independently, with additional
5 sources/17 roles. See the corresponding current/historical reports rather than
assuming a report's fingerprint survives subsequent edits.

## Ownership and current entry points

The runtime author owns 30–43, modules.json, adapter execution integration,
bin/php-semantics, runtime/source tests, DESIGN and ARRAY-HANDOFF. The narrow 20
string-line handoff has returned from the compiler author. Coordinate changes to
compiler-owned 11, 16, 21, 45-constant-context and 46-source-compiler; do not duplicate
those traversals. The reviewer owns PROGRESS/inventory/CORE/README and independent
conformance evidence. Never push; stage only owned files after independent review.

`adapter/main.ml::execute` now requires canonical base64 `filename`, checks the
program, and calls `$php_run(program, budget, filename_text)`. The CLI passes the
actual `os.fsencode` path. 40 decodes bytes and retains `SOURCEFILE unit bytes` in
`S.FILES`; empty/NUL filenames are invalid context. Non-UTF8 bytes are preserved.
Currently this field is set after the old source drive. The bridge must supply
that same actual filename **before** compilation and execution, without a dummy
file or host character conversion. File-sensitive PHP expressions remain pending.

`$php_run` still calls 40 `$run_source`, whose `$check_statements` path uses 20's old
availability/constant-read checks. It then creates scoped statement tasks and
runs `$drive`. 36's recursive constant classifier is also still in use. The new
compiler and pure 44/45 dimension helpers are **not registered in modules.json**;
source execution does not install pools or consume compiler facts. Replace the
old source compilation path carefully, retaining explicit Unsupported outcomes
for unresolved syntax/context; avoid keeping two competing source prepasses.
Bare helper-state execution may remain a clearly identified internal test path.

## Reviewed interfaces

- 11: `$pcsource(id, program)` retains checked AST and canonical occurrences.
  Identity is compiled instance ID plus structural `pcpath`, never tree equality
  or metadata. 31 propagates `AT origin task` / `ORIGIN_RETURN` across nested work.
  `$origin_accepts` selects the explicit path, then checks its node. Internal saved
  continuation states still rely on machine invariants.
- 30/32: `PCONSTANT path value`, `ppool={UNIT,CONSTANTS}`, permanent `S.POOLS`.
  `$install_pool(S, unit, array_backing, allocations, constants)` validates the
  structural boundary and shifts every array ID by `|S.ARRAYS|`, including gaps.
  It preserves existing state, rejects repeated installation, and does not prove
  arbitrary supplied constants correct. `$pool_value(pools, origin)` looks up
  already installed values. 39 projects pool roots separately from `HELD`.
  Source-unit teardown is pending; temporary cleanup must never drop these roots.
- 45 constant context: `PFFACT path value effective_line`; `$pfprepare` performs
  the exact bounded constant traversal. Arrays visit each item's value before its
  key, even when dynamic/by-reference entries prevent whole-array folding. VAR/ASSIGN stop
  this prepass, but ordinary compilation still visits their child arrays.
  Scalar leaves preserve their token line; rewritten operations use the ambient
  prepass line. Do not recover that line from the original AST after folding.
- 46: `$ppstart(id, program, actual_file_bytes)` returns `ppstate` with `FOLD`,
  `WORK`, `EXPRESSIONS`, `ACCESS`, completion and ordered diagnostics.
  `FOLD.SOURCE` is the canonical unit; `FOLD.MEMORY` is isolated compiler storage.
  `PPCWORK path statement env endline` identifies successfully compiled work.
  A block's children are compiled recursively without extra WORK entries; execute
  each recorded item once at its original path, only after whole-source success.
  `PPCEXPR path endline value?` records ordinary compilation, including no-value
  expressions. `$ppaccess(P,path)` returns `PPR`, `PPW`, or `PPUNSET` only after
  successful compilation. Keys/computed names are reads; DIM bases inherit mode.
  By-reference acquisition uses the same Zend write-fetch mode as other writes;
  runtime task kinds distinguish the actual reference protocol.
- `$ppconstants(P)` merges partial facts and ordinary constant operand results,
  coalescing exact matching path/value pairs and rejecting conflicting values,
  array IDs, invalid lines or incomplete compilation. Ordinary codegen can yield
  constants without an AST rewrite. Retain both sources of values. Partial facts
  beneath wholly folded parents deliberately have no ordinary access descriptor.

Do not embed `ppstate` in `pstate`: `FOLD.MEMORY` is itself a runtime state. Convert
only unit/path/value/access/ending-line data into a runtime descriptor. Reject
compiler cells/bindings before extracting array storage. Do not transplant
compiler `HELD` into runtime `HELD`; permanent pool roots own all retained values,
including unused partial arrays. Keep executable metadata separate from ownership.

## First source bridge

Use reviewed compiler work and descriptors on the current global source subset.
Namespace/import value resolution stays explicitly pending; never interpret its
names using an unconditional global lookup. Byte compiler diagnostics also need
an explicit completion/encoder when that context is activated.
An ordinary compiler error suppresses execution of all earlier `WORK`; retain
its ordered compiler diagnostics instead of starting the partially compiled tasks.

A possible small dispatch boundary is scoped `AT EVAL` and `AT DIM_PREP`. Consume
an installed constant only for a checked **PPR** occurrence with an actual compiled
constant operand. Merged partial facts alone cannot authorize a read. In
particular, DIM_PREP is shared with writing/unset/reference acquisition; preserve
those designation effects. Interception must preserve surrounding origin scopes,
borrowing/capture rules, permanent roots and budget resumability. Do not duplicate
or allocate a constant literal each time its task executes.

Replace runtime consumers of `$compiled_line` with the ending line recorded for
their exact expression occurrence. 31 echo tasks and 40–42 continuation creation
contain those calls. Respect explicit assignment line resets and the distinction
between a CV operand's origin line and its consumer's line. The old helper may
serve bare internal states; it cannot substitute for compiled metadata when a
source descriptor exists.

This is a behavior-changing compiler/pool bridge. It can admit constant string
DIM reads folded inside arrays before generic 44 runtime reads are connected.
Include those newly admitted prepass witnesses in this first source gate. Likewise,
if a previously Unsupported compile error becomes modeled (for example a constant
array key), preserve its exact positive source regression and update the negative
classification explicitly. Never omit a mismatch or call it a passing Unsupported
case. Keep all 526 existing source cases, including twelve heredoc/quoted controls.
Any newly admitted namespace/import-only source also needs its own exact witness;
do not describe an expanded source entry as preserving an unchanged support set.

Tests must cover same occurrence reuse after temporary cleanup, distinct equal
NaN array occurrences/units, dynamic allocation disjointness, first mutation COW,
partial facts without executable access, read versus writable DIM contexts,
actual filenames, effective lines, and encoded checked-program retention. Existing
SOURCE-ORIGINS tests intentionally trace bare source tasks; update entry-point
assumptions explicitly if the compiled entry changes their expected state.

## Following gates and commands

Immediately next: generic scalar/string reads through 44 and all sixteen retained
read/prepass conformance fixtures (`string-read-*`, `scalar-read-*`; listed in
DIMENSIONS.md/conformance catalog). Then 45 string writes/reference/nested errors
and eight retained source ordering witnesses. Key conversion, negative bounds and
append may stop before a delayed RHS is resolved; do not uniformly evaluate it
first. Array unpack/destructuring and foreach/general control follow. Call frames,
objects/properties, callbacks, source GC and lifecycle remain further core work.

Useful commands, serialized around any required build and stable source freeze:

```
python3 tests/semantics/execute_context.py
python3 tests/semantics/source_origins.py
python3 tests/semantics/compiled_pools.py
python3 tests/semantics/ownership.py
python3 tests/semantics/string_lines.py
python3 tests/semantics/constant_context.py
python3 tests/semantics/source_compiler.py
python3 tests/semantics/validate.py
```

Coordinate short freezes with the compiler author and reviewer. Final source runs
currently take about three minutes. Independent review and an exact fresh source
repeat are required before committing each bounded implementation milestone.
