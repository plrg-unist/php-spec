# Runtime compiler bridge handoff

Read PLAN.md, PROGRESS.md, AGENTS.md and the php/php-spec/p4-spectec skills, then
ARRAY-HANDOFF.md, DESIGN.md, SOURCE-COMPILER.md, CONSTANT-CONTEXT.md and DIMENSIONS.md.
The complete PHP core goal remains unfinished. This handoff records the runtime
bridge, subsequent source activations, and the remaining control and lifetime work.

## Historical pre-bridge checkpoint

Runtime commits: `cb02399c` task origins; `0df3d175` permanent pool installation;
`0270197e` actual filename transport and twelve string-line source regressions.
Compiler commits: `72d3a65d` ordered compiler and effective constant rewrite lines;
`4297dadf` heredoc/nowdoc token-line correction; `00e27843` access descriptors.
These checkpoints predate the source bridge described below.

The final regular source suite passed **526 exact source comparisons + 25 outcome
negatives**, independently repeated. Filename transport passed 16 canonical and 24
independent cases; origins 25/333; pools 24 boundary +100 graphs/1623 assertions,
independent 24 +250/4825; ownership 617 +96/5434. Ordered compiler 561 lint +15 ending
line cases and 8 sources/24 access roles passed independently, with additional
5 sources/17 roles. See the corresponding current/historical reports rather than
assuming a report's fingerprint survives subsequent edits.

## Current bridge implementation

`33-runtime-compiler.watsup` now connects public `$php_run` to `$ppstart` before
execution. The caller's actual filename bytes initialize `S.FILES` and the lexical
compiler context first. The compiler must complete successfully before any `WORK`
executes. Compiler warnings remain ordered before later failures; lexical fatal
messages use the byte-valued `STATICBYTES` completion and the source renderer.
Ordinary `STATICERROR`, Unsupported, budget and runner failures remain distinct.

Successful compilation installs merged facts/constant operands in the permanent
pool, rejects compiler variable storage, and retains compact `CODEEXPR` descriptors
with occurrence, ending line and constant-read eligibility. It does not embed
`ppstate` or compiler memory in runtime state. Scoped `AT EVAL`/`AT DIM_PREP` reads
consume the already shifted pool value only for a successful ordinary `PPR` operand.
`PPW` and `PPUNSET` contexts retain designation work. Partial facts below wholly
folded parents own values but provide no executable access permission.

Namespace constant reads additionally export tagged `CODENAME` descriptors with
occurrence, resolved name bytes and optional global fallback bytes. After a pooled
read misses, `AT EVAL ConstFetch` performs lookup at the recorded ending line.
Lookup failure names the primary resolved spelling, even when fallback was tried;
preceding runtime output is preserved. `DIM_PREP` reaches this same path through
its existing same-origin `AT EVAL`. Folded values retain the pool route. Compiler
lexical context remains separate from runtime variable storage.

31 and 40–42 source consumers use recorded occurrence ending lines; a compiled
unit never recovers a missing descriptor from AST equality or source metadata.
The obsolete source traversal, recursive scalar/array classifier and production
`$run_source`/`$run_statements` helpers are removed. Origin tests define their own
explicitly unchecked fixture wrapper with direct source locations. The compiler
uses its own narrow direct-CV check. Module44 is registered and `$base_read` now delegates ordinary array/string/scalar
reads to `$dimension_read`. Module45 write helpers now update captured source locations and model reference/nested errors.

The reviewed bridge passed 546 exact source comparisons and 28 explicit negative
outcomes after the imported-class-prefix guard `ff941f17`. Independent review
repeated the full source suite, 582 compiler and 233 context campaigns, and all runtime
helper gates. Additional independent evidence covers 16 source probes, 16 constructed
cases/138 assertions, four byte-diagnostic probes and seven alias controls.
`runtime_compiler.py` passed 11 cases/105 assertions; 12 admitted original sources
from the compiler emission-line matrix also matched through public execution.
The earlier accepted counts above remain historical. Runtime owns20/30–43, the module catalog, renderer and runtime tests;
compiler owns11/16/21/22/45constant/46; reviewer owns progress/inventory/CORE/README.

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
  `WORK`, `EXPRESSIONS`, `ACCESS`, `NAMES`, completion and ordered diagnostics.
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

## Scope and remaining integration

Namespace/import scalar-only work now executes at its original lexical paths;
namespace constant value resolution remains explicitly Unsupported until the shared
resolver is connected and independently reviewed. In particular, compound constant
names whose first component matches an imported class alias are temporarily
Unsupported: the old global evaluator would otherwise report the wrong resolved
name. Four retained negatives cover matching/case-folded aliases, prior output and
partial arrays; unmatched-prefix and unqualified controls remain admitted. No
unconditional global fallback or host lookup is introduced. Compiler diagnostic rendering currently has the
single-source-unit contract of `$php_run`; dynamic/multiple-source execution and
per-unit teardown remain pending.

The bridge newly admits constant string DIM reads folded inside constant and dynamic
arrays, compile-time illegal array keys, and lexical compiler diagnostics. Exact
source witnesses retain those support changes. Read activation retains all 16 read/prepass fixtures. Some fixtures combine a
folded operand with an ordinary string read, preserving both prepass suppression
and runtime diagnostics as source regressions.

Constructed bridge tests check repeated occurrence reuse after temporary cleanup,
distinct NaN-array occurrences and units, dynamic allocation disjointness, read versus
write/unset permission, partial facts without ordinary descriptors, compiler variable
storage rejection and budget resumability. Existing source/origin/filename/ownership
regressions remain mandatory, including the encoded checked-program retention test.
These constructed re-entry states do not claim PHP loop or function execution.

The subsequent generic read activation passed 576 exact source comparisons and
28 explicit negative outcomes. Independent review repeated 64 additional original
sources, the 583-case read matrix, runtime compiler/origin/ownership controls, and
612 ordered compiler lint cases with emission-line and access-role controls.

Namespace constant activation subsequently passed 621 exact source comparisons
and 24 explicit negative outcomes. Independent review repeated 43 alternate
sources, including all seven original alias observations, and 19 constructed
lookup/multiunit/DIM resumption cases with 187 assertions. Canonical namespace
40 source/15 descriptor checks, constant 42/5, compiler 663 lint/emission/access
checks, runtime bridge 15/148 and origin/ownership campaigns also passed. The four
temporary alias guards are removed; their exact original sources now agree.

String write/reference activation and exact bare-break terminator lines passed
664 source comparisons and 23 explicit outcome negatives. Independent review
repeated 103 additional write sources plus one retained temporary-lvalue compiler
boundary, all 14 original break failures/controls and eight alternate sources/five
metadata controls. The 2,220 write cases/12 boundaries, ownership 617/96, origins
25/333, runtime bridge 15/148, namespace 40/15, constant 42/5, compiler 706 and
metadata/occurrence transport campaigns also passed. These are bounded source and
helper results, not closure of a PHP semantic family.

Legacy traversal/classifier retirement and known temporary-target compile errors
passed 686 exact source comparisons plus 24 outcome negatives. Independent review
verified the full raw source report, repeated 38 additional temporary-target sources
and two explicit call/property boundaries, and repeated origin 25/333 and runtime
bridge 15/148 checks. Ownership 617/96 and compiler 728/emission/metadata checks
passed the same closure. Production source execution has one compiler path; the
unchecked origin runner is defined only in its test fixture.

## Following gates and commands

Ordinary scalar/string reads through 44 are connected, with all 16 retained
read/prepass conformance fixtures and 15 compiler emission-line source cases.
String writes/reference/nested errors through 45 are connected, with all eight retained
source ordering witnesses. Key conversion, negative bounds and append may stop before a delayed RHS
is resolved; do not uniformly evaluate it first. Array unpack/destructuring and foreach/general control follow. Call frames,
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

## Next source milestones

1. Activate ordinary scalar/string reads through 44 and all 16 retained read/prepass
   fixtures, then string writes/reference/nested errors with all eight ordering
   fixtures. Keep delayed RHS reads and captured writable locations explicit.
2. Add source `if`, `while`, `do` and `for`, pure truthiness and loop-scoped
   `break`/`continue`. Test actual repeated literal execution using the already
   installed pool and interruption/resumption across iterations.
3. Add array unpack/destructuring and foreach value/reference execution. Foreach
   requires persistent cursor behavior under deletion/reinsertion and mutation,
   not an index into the current entry list. Extend the ownership protocol first.

The compiler worker can independently prepare namespace constant resolution and
function declarations while these runtime steps proceed. Runtime namespace reads
need compact resolved-name/fallback descriptors; basic named calls subsequently
need frames, argument/reference binding and declaration activation. General callbacks,
objects and lifecycle remain further core work. The full-core objective is unchanged.

## Accepted control source activation

Prerequisites: accepted string writes and reviewed legacy checker/classifier
retirement. The unchecked trace wrapper stays in the test fixture only. Compiler owns
if/while/do/for traversal and static break/continue legality; runtime owns 30 task
domains and new 50 rules, including the extension to task-root projection.
The registered source path joins compiler 47 with runtime 50.

Compiler order is observable even for runtime-unselected code: while/do compile
body before condition; for compiles init, body, step, condition. If clauses compile
condition/body in clause order. Preserve each child's structural occurrence path.
Do not infer break/continue legal depth by arbitrary scalar folding. Statement
terminator lines need exact checked token context, especially close tags consuming
newlines. Accepted prerequisite 3a137a36 transports exact token-derived statementBodyLine
for synthetic statement-list diagnostic context.

Runtime conditional tasks can store true/false continuation lists and a consumer
line. Evaluate condition at its own AT origin, resolve its delayed operand, apply
PHP truthiness (null/false/zero signed integers/both float zeros/empty or "0"
string/empty array false; NaN and nonempty arrays true). NaN conversion must emit
the runtime warning from number_bool; native lint does not emit it for if(NAN).
Clear the condition result,
then install the selected continuation. Any nested task lists must participate in
39's root traversal even though ordinary generated branches contain ASTs only.

Loop continuation markers must retain the loop's source origin and AST. While tests
before body; do tests after body; for runs init once, tests the last condition (true
for an empty condition sequence), then body and step. All earlier condition/step
expressions execute and discard normally. Re-enter each compiled occurrence through
AT tasks; do not recompile or allocate replacement literal pools.

Break/continue scan loop markers with a validated depth. Discard nested continuation
work, restore the selected loop's saved origin, and either discard its marker
(break) or execute its next condition/step phase (continue). Existing ORIGIN_RETURN
frames outside the loop remain intact. Clear consumed scratch values and preserve
permanent pool roots. Try/finally, switch-specific continue warnings, generators and
callbacks need their own later control/lifetime rules; do not silently unwind them.

Required source witnesses: true/false/elseif/else selection; false conditions still
fully compiled; warning/error ordering and skipped runtime branches; while/do/for
iteration order; init/body/step/condition compile diagnostic precedence; literal
break/continue depth; nested loop origin restoration; runtime budgets at every
phase; repeated compiled array literal occurrences (including NaN identity), same
occurrence reused versus distinct occurrences; namespaced late NAN array reads
remaining runtime allocation; temporary cleanup and COW through loop assignments.

Foreach follows unpack/destructuring prerequisites and requires persistent bucket
identity/cursors under deletion/reinsertion, plus value/reference iteration owner
semantics. A list-index cursor is insufficient. Function bodies and defaults need
compiler/declaration activation and call frames separately; this control slice is
not a complete-core claim.

The accepted implementation uses CHOOSE/LOOP_TEST/LOOP_NEXT tasks and the public
compiled source entry. `tests/semantics/control_flow.py` retains 40 normal sources,
21 additional finite compiler-order/error sources, exact state resumption at seven
small budgets, unchanged pools/CODE, heap validity and nested branch operand roots.
The final gate passed 747 exact source observations and 25 outcome negatives,
including an infinite-loop budget boundary. Infinite native loops are never run
as positives. Independent review repeated 67 alternate original sources and
three programs across 163 budgets each (2,493 state assertions), plus canonical
control 40/41/1,231, ownership 617+96/5,434, origins 25/333, and bridge 15/148.
Compiler validation passed 789 lint sources and 46 dedicated control sources,
16 edited metadata contexts and two structural compilation-order checks.

The earlier alternate checked frontend/compiler/runtime smoke passed 40 original
sources/668 assertions before publication and remains historical evidence. Foreach
and broader expression dispatch remain next work.

Next source activation sequence, agreed with the parent after this control slice:

1. Truth consumers (`!`, short-circuit boolean/logical operators, ternary) and
   comparisons. Reuse runtime truth conversion, preserving warning timing and
   delayed operands. General array/nonnumeric comparisons need their own rules;
   the existing `num_compare` helper alone does not define PHP comparison.
2. Increment/decrement and compound assignment on captured lvalues, followed by
   modulo, shifts, bitwise operators and casts. Existing numeric helpers cover
   machine arithmetic but do not establish source operand conversion, diagnostic
   order, nonnumeric string behavior or assignment result ownership.
3. Array unpack/destructure compilation and execution can advance independently
   with an explicit compiler/runtime descriptor contract. Foreach then needs
   stable bucket identity and cursor/owner semantics under mutation. Declaration
   and call-frame interfaces remain parallel compiler work.

Current source arithmetic admission is only `+`, `-`, `*`, `/`, `===`, `!==`
and unary `+`/`-`; never infer broader source support from registered numeric
helpers. Preserve the full-core objective while publishing bounded reviewed changes.
