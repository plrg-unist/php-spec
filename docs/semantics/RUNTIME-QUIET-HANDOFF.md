# Runtime successor after quiet access

Canonical quiet code is `a42fddfe`, author source/state bindings `608a8752`,
compiler evidence `cd0f3d3f`, and native/first-failure originals `ab38e02c`.
Independent final acceptance is `f3235689`; GLOBALS compiler-only review is
`c2e3d1ea`. Current quiet code fingerprint is
`9c46ba66f0ba43b6167cdf4477df087c9dec0e6feb2b83643ac7974417aaf3de`. The last full
container campaign passed 4,997 exact sources and 24 outcome negatives on
`a0e3709a6f574493db32398813d340343c00223a72ce0c0f44d885bd88375b67`:
author `d71d4107`, independent `96cbf051`, stable
`coverage/semantics/container-source.json`. This is historical after quiet
code installation. Only oracle identity closes; complete core remains unfinished.

## Accepted quiet work and exact evidence

Quiet variable/DIM `??` is FETCH_DIM_IS, distinct from terminal isset/empty.
Module70 preserves delayed CV name/key operands, already-evaluated temporaries,
key expression effects and diagnostics. Missing/null return null without making
an ENV binding. Direct global `$this` throws; a computed name equal `this` quietly
falls back. Array keys retain conversion warnings/type errors. String offsets
use the quiet VM protocol: leading-integer text warns, noninteger text is null,
float/NAN cast is silent, array keys throw. Do not reuse this terminal protocol
for isset/empty: string array keys there return false/true rather than throwing,
float/NAN conversions emit diagnostics, and array invalid-key error text differs.

The compiler now owns http_response_header assignment/read state and deprecations,
including direct CV versus constant-computed name distinctions. Runtime33 maps
compiler deprecated diagnostics. Constant variable-name conversion uses original
pool facts, but its warning is emitted by the compiler. `$captured_name` checks
`compiled_read` at the exact name-child occurrence, then normalizes captured
KNOWN values to PSTRING (array→Array), leaving delayed CV and REFERENCE operands
untouched. Consumers cover NAME_READ/ACQUIRE/UNSET, PREP_ASSIGN/PREP_REF, DIM_NAME,
LIST_STORE_NAME and FOREACH_NAME; assignment/foreach name paths have two FIELD0
components. Do not replace this test with mere known-value equality.

Quiet source catalogue295 = reviewed286 plus6 retired outcome negatives,
2 exact quiet VAR/DIM boundary sources and1 preserved list/header boundary.
Six retired negatives are four array/NaN constant names and two header forms;
18 outcome negatives remain. Author8 state fixtures check3,760 assertions at
all budgets0–64, full resumed state, heap/array/cursor/origin validity, POOLS/CODE
preservation and final TODO/ORIGIN/HELD/ITERATORS empty. Independent original
quiet826:286 sources plus6 state fixtures/2,277 assertions, budgets0–48,64,96,128.
Fresh reviewer verified nine additions and exact final catalogue membership.

Private historical roots are immutable:
* `.tools/runtime4-name-pair/quiet-inputs.json`:826 reviewed inputs;
  94 matrix,120 header,30 name,26 extra author source outcomes.
* `.tools/runtime4-quiet-publication/candidate-inputs.json`:829, final295
  source literals; public295+18 and durable8dense3,760 pass. Reports in its
  coverage/semantics/source-selected.json and quiet-access.json.
* `.tools/runtime4-quiet-final/candidate-inputs.json`:829, only four compiler
  test consumers differ from prior829. publication-bridge.json binds retained
  source/state evidence honestly; runtime, CASES and PREFIX providers unchanged.
  compiler-reference-inputs.json adds exact read-only Zend/zend_compile.c (830).

Originals are durable in `ab38e02c`:198 quiet-dimension native observations
(66 coalesce and132 isset/empty),84 delayed observations,36 compiler name
originals and25 duplicated runtime conversion warnings plus5 controls.
`variable-name-first-runtime-failures.json` reconstructs exact7 changed/60
unchanged spec files over1f0e8810. Reviewer6 reproduced all25 failures unchanged.
A malformed hand-authored list-reference source was a parser reject, preserved
in runtime4-name-pair/additional-cases-first.py and its native-originals run;
corrected valid source has a distinct ID. Never count parser/tool failures pass.

## Next ready runtime: memoized coalescing assignment

DO NOT overwrite frozen `.tools/runtime4-coalesce-assign` (832 inputs) or
`.tools/runtime4-coalesce-guarded` (834 inputs). Guarded manifest is
candidate-inputs.json. It is still private, not admitted in canonical source.

Modules46/71 from compiler4's checked compiler prototype add ppstate WRITES
(pcpath,nat)*. Existing EXPRESSIONS/ACCESS records retain first quiet access;
second compiler walk reuses memoized child facts, resets original AST lines,
reconverts constant names for second compile warning, records unique positive
write lines, and never reruns child compilation. Compiler33 exports CODEWRITE
alongside CODEEXPR/CODEEFFECT; expression/effect walkers skip the new marker.
Existing ordinary descriptors stay unchanged. Source/runtime72 relies on this
explicit read/write distinction: e.g. multiline float temporary key warns at
read line3, write line2; simple CV key is reread at its own line after RHS.

Runtime72 prepares the original pbase, performs quiet read, frees saved inputs on
non-null result, otherwise owns the pbase through RHS in COALESCE_ASSIGN_WRITE.
`memoized_write_base` changes only occurrence lines. Original REFERENCE temp
operands remain reference wrappers: RHS mutation sees the changed cell value,
RHS rebinding retains the old wrapper; ternary value copies dereference earlier.
RHS assignment-to-self uses existing early resolve protocol. DIM writes reuse
assign_array; variable writes preserve result copying and dynamic-this error.
Only COALESCE_ASSIGN_WRITE needs a new explicit task_nodes owner (base_nodes).

First832 valid source gates passed105 originals (37 of38 retained +68 matrix),
with1 named-GLOBALS case Unsupported. Author8dense3,760 passed. Internal edited
CODEWRITE missing/zero/duplicate produced line0 or ambiguous execution; this is
code integrity, not a native source disagreement. Exact old full states and
fixtures are codewrite-first-63grjenw; old832 stays immutable.

Guarded834 adds only module72 recursive descriptor readiness before read/RHS:
exactly one positive CODEWRITE for every VAR/DIM occurrence. Invalid internal
code returns explicit Unsupported and releases continuations. Three author
edited-state controls pass; reviewer added nested-only controls (9/74 assertions).
Guarded source137 = old105 plus16 reviewer nested originals plus16 accepted
compiler-target guard originals. One GLOBALS remains excluded; nine genuine
parser controls stay separate. Author8dense3,760 and independent7dense3,024
(budgets0–48,64,96,128) pass, including reference rebind/mutation, throw, nonnull
temporary cleanup, nested memo tables, COW results and origins.

Evidence locations:
* guarded coverage/semantics/coalesce-assignment.json; exact author fixtures
  `.tools/coalesce-assignment-state-yfcqnl9i` beneath guarded root.
* guarded source-run-wk4fey5h (37/38 +GLOBALS), source-run-w55gf8nu (68),
  source-run-0bpvsc11 (32), codewrite-controls-results.json.
* `.tools/review6-guarded-source/review.json`,
  `.tools/review6-guarded-state-results.json`, plus paths in
  docs/semantics/QUIET-REVIEWER-HANDOFF.md.
* durable native originals: coalesce-assignment-lines (20), reference (12),
  nested (16) under coverage/semantics, commits8f3e9e4d/9ca5a4dc/d99702a1.

Before ??= publication rebase onto accepted quiet compiler test/cataloque baseline,
add actual 137 literals (and future supported GLOBALS original), durable compiler
and state gates, update all CODEWRITE consumers and retired boundaries, run early
preflight, independent final binding, small coherent code and separate evidence
commits. No duplicate full source run is needed solely for this rebase; full
current closure is required at planned quiet/CV checkpoint or a shared risk.

## Following work and invariants

Compiler4 has immutable `.tools/globals-name-compiler-checked`428 inputs,46/71
for direct parser-designated GLOBALS key conversion and direct unset[] error.
330 exact compiler traces+8 malformed controls; first wrong unset[] diagnostic
preserved separately. Copy into a distinct requestenv root only. Runtime global
DIM names use compiler name conversion at FIELD1; dynamic TMP equalGLOBALS must
keep generic array-key compilation. Reading whole GLOBALS duplicates symbol table
values with explicit reference wrappers retained; never alias ENV as an ordinary
array. Ordinary seven request-environment originals remain pending, plus broad
CLI/request initialization and environment API. Reviewer7 captures native copy,
undefined CV omission, numeric key and order controls; do not guess the request
state from a few argc fixtures.

Compiler4 has `.tools/isset-empty-compiler-first/73-isset-empty-compiler.watsup`:169 exact compiler traces (132 terminal matrix plus37 phase/provenance
sources) pass in results.json. The40 original controls under
`.tools/isset-empty-originals/originals.json` separately retain one grammar
reject and two call/object pending cases. Module73 depends on GLOBALS42846/71;
additional descriptor controls are queued, with no runtime/source admission. empty(nonvariable) lowers ordinary NOT; isset(nonvariable) rejects
before child compilation. Variable operands PPIS; direct GLOBALS constant
true/false; multiple isset arguments short-circuit ordered AND. Runtime74 must
preserve distinction from module70 and explicit object/property boundaries.

Then calls/frames/return, declarations/classes/properties, exceptions, dynamic
sources, resumable services, lifetime and core intrinsics remain. Top-level
return foreach original is still Unsupported; future return completion must
release iterator classes but keep final variable aliases. Final syntax closure,
fresh offline rebuild and complete core validation are mandatory.

Use sole PHP8.5.10 NTS64 .tools/php/bin/php and canonical frozen executables.
Never Dune-build private roots: use .tools/run-private-semantics.py for harness
build calls, or call canonical numeric_runner/adapter directly. Preserve exact
mismatches and loaded bytes before fixes; no Unsupported/tool failures/timeouts
as source pass. Coordinate shared index and freezes. No push.

## Rotation boundary

At this handoff no runtime-owned process is running and the shared index is
released. Compiler4 retains continuity for final compiler prototypes and
reviewer7 owns independent next-family reviews. No canonical source edits are
pending. Build fingerprints and frozen candidates must remain intact. Root
requested rotation after this accepted quiet checkpoint; continue with real
??= source admission, then request environment and terminal isset/empty work.
