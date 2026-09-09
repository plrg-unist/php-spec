# Compiler continuation

Read PLAN, PROGRESS and the php/php-spec/p4-spectec skills. Never push. The target
is pinned PHP 8.5.10 CLI NTS64; use only `.tools/php/bin/php` and `vendor/php-src`
as the oracle. Meaning belongs in pure SpecTec. Unsupported, tool failures and
budget exhaustion never count as agreements. Full core remains unfinished: 169
constructors, 70 field domains and 306 obligations; only oracle identity closes.
Final full syntax, fresh offline build and complete core/source closure remain due.

## Current checkpoint and ownership

Quiet/header/name code `a42fddfe`, compiler evidence `cd0f3d3f`, runtime evidence
`608a8752` and review `f3235689` are accepted. There are 295 selected source
agreements +18 outcome negatives, eight state programs/3,760 assertions and
independent source/ownership replay. The compiler group passes 5,336 native lints,
240 focused traces/12 state-access controls, 90 foreach traces/20 controls and
111 destructuring traces/32 controls. The remaining foreach compiler boundary is
object-dependent nullsafe access; calls and object access remain explicit work.

The full container campaign `96cbf051` passed 4,997 sources +24 negatives before
the quiet changes. It remains historical, not refreshed full source closure for
quiet code. Earlier ordinary, unpack, list and foreach checkpoints are recorded in
PROGRESS and their contracts. `coverage/semantics/quiet-compiler-group.json` binds
823 installed inputs and seven private campaign helpers separately; the reports
retain their actual private execution scopes. The copied Zend compiler reference
is a read-only test dependency, not a runtime evaluation shortcut.

Compiler4 owns frontend/schema and compiler rules/tests. Runtime successors own
storage/evaluation integration; review7 independently gates changes and owns the
phase ledger, inventory and PROGRESS. Coordinate shared20/30/33, module catalogs,
watched freezes and the Git index. Preserve raw originals before repairs. Draft
outside watched inputs; preflight before campaigns; freeze complete inputs/tools.
Private tests must reuse canonical executables without Dune builds through copied
or symlinked roots. The raw source harness creates exclusive per-run artifacts.

## Interfaces to preserve

- Occurrence identity is compiled unit plus FIELD/INDEX path, never AST equality.
  Ordinary-array items are nullable and retain original indices through holes.
  Foreach fields remain iterable0/key1/byRef2/value3/body4/keyByRef5.
- Prepass FACTS, selected-child REDIRECTS, queued WARNINGS, ordinary operand facts
  and permanent POOLS are different. Only visited PPR operands export constant
  reads. Retain raw AST lines and parser literal designation; equality of a later
  constant value cannot recreate a CV name or parser-folded concat.
- Array prepass visits values then keys, including later entries after dynamic
  operands. Hole errors precede pass-two insertion/scalar-unpack failures. Initial
  holes retain compilation context; later holes use the preceding original value
  or unpack operand line. Explicit Zend barriers/traversals are not a catchall
  conversion of unknown expressions into nonconstant facts.
- Class constants and named `::class` that need missing lookup APIs remain
  Unsupported. Erasing a potentially known value changes branch/error priority;
  retained builtin Attribute originals demonstrate the actual former defect.
- `PPCEFFECT`/`CODEEFFECT` preserve ordered original side effects when ordinary
  compilation returns a known operand. List assignments can return constant
  operands after target effects; prepass still stops at the assignment. CAST and
  coalesce produce temporaries absent an earlier AST fold. AND/OR/NOT/comparison
  can fold while preserving effects. Never replay child conversions twice.
- List fetch lines and target store lines differ. Nonreference CV RHS is copied
  before targets and bypasses FETCH_THIS; reference RHS captures the wrapper.
  Keys precede source fetches, then targets. Holes retain running context;
  nonreference VAR targets carry their original AST line, reference/DIM targets
  retain pretarget fetch context, and nested patterns carry their completion line.
- Wrappers, copied array tables, embedded shared references and delayed operands
  are distinct. Foreach uses insertion occurrence IDs and per-iterator saved
  positions across COW descendants, not current item indices or shared lineage
  progress. Metadata creates no artificial owners. Preserve caller continuations
  during DIM setup and reset; the original lost-ORIGIN_RETURN defect is retained.
- Compound targets use PPRW before RHS, keys PPR. Direct `$this` compound/incdec is
  lint-valid and fails at runtime acquisition without object context. Keep captured
  DIM final-opcode lines and dynamic-name fetch timing.
- `concatExprLine`, `nullaryExprLine`, `cloneExprLine` and callable context have
  source-backed designation and edited-boundary checks. Bare null exit requires
  token spans; parenthesized exit uses endLine. Unqualified lowered exit/die/clone
  names use their keyword protocol; qualified/relative names use ordinary calls.
  Foreach reuses the existing statementBodyLine producer, including UTF-16 profiles.

## Accepted quiet/header/name behavior

`PPIS` preserves quiet variable/DIM traversal; nonvariable DIM bases and keys use
PPR. Property/static/nullsafe quiet execution is still an object dependency.
Runtime coalesce fetch differs from isset/empty terminal tests, especially for
string offsets and invalid keys. Do not implement one by silently reusing the
other's conversion or diagnostics.

`HEADERASSIGNED` is a compilation-unit flag. Direct CV BP_VAR_W marks it, including
a write compiled inside a dead branch. R, RW, UNSET and IS do not mark it. Direct
header reads warn only before the flag; computed constant names warn independently.
Future function/op-array compilation must start the correct fresh flag context.
List RHS and foreach CV target lowering retain their special compiler protocols.

Constant variable names convert during compilation, including array/NaN warnings.
Keep original child operand facts and pools. Runtime `captured_name` normalizes
only when `compiled_read` proves that exact name-child occurrence is constant;
KNOWN alone is insufficient. This covers read/acquire/unset, assignment/reference
preparation, DIM, list and foreach name capture. Delayed CV operands are not
resolved early. Twenty-five original duplicate-warning failures are preserved.

Two obsolete name Unsupported checks, the foreach header pending check and three
list/header/quiet exclusions were retired with exact source/native observations.
Three quiet object cases and the actual call boundaries remain explicit. No new
intentional engine divergence was introduced; namespace-relative static remains
the sole reviewed divergence with source activation still pending.

## Next private candidates — not source admissions

1. Guarded coalescing assignment is in the runtime successor handoff. Compiler
   `.tools/coalesce-assignment-compiler-checked/frozen-review-inputs.json` binds
   413 inputs: 266 compiler traces and eight malformed descriptor checks. Separate
   `.tools/coalesce-assignment-guards` has 16 further exact traces and nine grammar
   rejects; no speculative nonvariable-LHS source admission was added.
   `WRITES (pcpath,nat)*` is separate from quiet ACCESS/EXPRESSIONS and exports
   `CODEWRITE`. The second writable walk revisits VAR/DIM structure using original
   AST lines and cached child facts, without compiling their effects again. It
   repeats constant-name conversion diagnostics where Zend does. Descriptors must
   be positive, unique and attached to PPIS occurrences. Runtime distinguishes
   delayed CV rereads from captured temporaries; reference-valued temporaries retain
   wrapper identity. Missing/zero/duplicate code descriptors reject explicitly.
2. GLOBALS compiler-only revision is frozen at
   `.tools/globals-name-compiler-checked/frozen-review-inputs.json` (428 inputs),
   independently reviewed in `c2e3d1ea`. It passes 48 name-key and 16 phase/provenance
   originals plus retained compiler/metadata regressions. Literal/parser-concat
   GLOBALS DIM keys convert as global variable names, without the locally scoped
   header diagnostic. Computed TMP names equal to GLOBALS stay ordinary DIM paths.
   Direct global unset[] has its special unset-error message; nested GLOBALS[] still
   gives append rejection. The first wrong-message state is retained. Pair46/71
   with the guarded runtime candidate; do not overwrite its later ownership fixes.
3. Isset/empty compiler73 is a private, unreviewed draft at
   `.tools/isset-empty-compiler-first/73-isset-empty-compiler.watsup`. Its first gate
   passes 169 native compiler traces: 132 terminal-matrix sources and 37 phase
   controls. The original40 archive separately retains one grammar rejection and
   two call/object dependencies. Variable operands use PPIS; empty(nonvariable)
   compiles as NOT with retained effects; isset(nonvariable) rejects before child
   compilation. Direct GLOBALS produces the special boolean constant. Multiple
   isset arguments compile in order. Descriptor/phase expansion and actual source
   runtime pairing are still required; do not confuse these checks with execution.

Complete request environment, quiet assignment and isset/empty before broader
calls. Then activate named/class/magic lookup, declarations/defaults, frames/calls,
linked objects/properties, exceptions, dynamic source and resumable/lifetime/core
intrinsic protocols. These remain required work, not permanent exclusions.
