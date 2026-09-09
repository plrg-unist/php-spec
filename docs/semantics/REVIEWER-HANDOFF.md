# Independent review continuation

Read PLAN, PROGRESS, applicable AGENTS and the php/php-spec/p4-spectec skills first.
Root orchestrates; runtime owns execution/storage, compiler owns static/frontend
work, reviewer owns independent evidence, inventory, PROGRESS and concise docs.
Never push. Coordinate file ownership, Git index and Dune starts. Complete core
remains unfinished; no constructor or PHP semantic family closes here.

## Accepted inc/dec checkpoint

Code `7d5718fb`, reports `5b24a5f8` and
[review](../../coverage/semantics/incdec-review.json) pass **1,484 exact sources +25
negatives** on `d399263a1c9f33bb445c958d624392ffc83d49df1c247df72b0c23ce59855d35`.
Independent raw audit verifies ordered source IDs/bytes/hashes and exact native
stdout/stderr/status, plus all retained wrapper/prepass/call-line/root-line sources.
339 independent public observations (331 distinct byte strings), 71 context replays/
994 assertions and eight dense replays/4,152 assertions pass. Dense budgets are
0–100 inclusive. Replay reports preserve their original fingerprints; separate
bindings prove every loaded semantic byte is identical to saved production.

Canonical gates: 154 runtime programs/2,226 assertions; dedicated compiler 108 lints,
32 access paths, eight emission lines and 12 context boundaries; broad compiler
1,526 lints/15 emission lines. Origins 25/333, bridge 15/148, ownership 617+96/5,434,
writable-fetch 30/505 and prior wrappers 21/396 pass the same closure. Helper graph
collection assertions are not source GC calls. All new helpers embed source bytes,
adding no consumed archive dependency. Independent preflight passed 15 identity,
three path, 17 closure negatives and nine build-log invariances; inventory is
169 constructors/306 obligations, with only validation.oracle-pin closed.

Four pre/post updates acquire RW variable/dimension/append locations and return
copied values. Current six values include exact string/bool/null diagnostics and
array failures. Direct `$this` uses eager FETCH_THIS in global source execution;
literal-string spelling is direct, ternary-computed spelling stays computed.
Computed reads use ordinary lookup and updates reject rebinding dynamically.
Direct assignment/reference rebinding and final unset reject statically before
operand compilation. Dimension bases/reference RHS retain runtime acquisition.
Computed BASE_NAME diagnostics use the stored root line; direct CV dimension
fetches retain their containing opcode line. Forced keys keep their own ordering.

## Preserve corrective history

- Wrapper identity `3585707a`/review `5b0dc0f2` repaired five FETCH/UNSET differences,
  then ordinary WRITE_DYNAMIC was found incorrectly marking references.
  Correction `84d70299`, reports `fa691044`, review `24c681d7` separates initialized
  writable fetching from actual acquisition. All seven acquire_name call sites
  were inspected; WRITE_DYNAMIC alone is ordinary. All 28 retained originals
  (12 mismatches/16 controls) resolve, with 12 independent extra sources, 79 prior
  wrapper sources and 49 marker/state checks. Current full source gate refreshes
  all canonical originals. Preserve initialized self-target timing and copied
  reference-result assignment without creating a fresh wrapper.
- REFCELLS stores stable cell history independently of owners/roots. Writes and
  singleton unset preserve it; fresh ordinary bindings remain unmarked. COW/union
  may unwrap copied ALIAS entries independently. Markers retain no storage and
  cannot enter isolated compiler pools. Generic FETCH/intermediate UNSET warnings
  differ from final ASSIGN_DIM/UNSET_DIM. Cycles remain observable before collection.
- Incdec prepass originals retain two old Unsupported gaps and a control; all four
  update shapes now have explicit nontraversing PFSTOP barriers. Ordinary visits
  still compile operands. Nullsafe-call overlapping-rule failure is retained as
  an interpreter failure, never a PHP error or pass; direct call checks now precede
  disjoint fallback checks. Seven computed-line originals retain four draft
  mismatches/three controls, now source-integrated and resolved.
- Callable metadata `c6a7d67d`/review `1d32e9be` retains eight old-AST originals:
  an identical pair needs native lines 3/2. `callableExprLine` preserves dynamic
  invocation opening-token context; name calls retain their name line. Optional
  integer transport differs from semantic requiredness/range checking. Missing/
  nonpositive context remains Unsupported; positive edited lines are consumed.
- First-hole metadata `87341500`/review `79951ad4`, unpack `d4706937` and original
  array kind `09f33419` remain accepted. Genuine-list conversion `5c756e5e`/review
  `861020db` passes 20 skipped sources; 14 reached originals remain Unsupported.
  First-hole compiler consumption and full destructuring remain open.

## Next independent gates

Use the current [runtime](RUNTIME-SUCCESSOR-HANDOFF.md) and
[compiler](COMPILER-HANDOFF.md) handoffs, not obsolete private snapshots. The rebased
compound prototype passes 81 author programs/1,204 assertions plus extra timing
controls, but independent source and dedicated compiler PFSTOP/access/order gates
remain pending. Preserve dynamic target acquisition before delayed RHS CV reads,
while forced RHS expressions may run earlier. Review array `+=` identity/COW and
all remaining numeric/byte/power/cast source dispatch. `??=` needs a separate quiet
read/memoized write path. Keep old draft disagreements unchanged.

Computed plain-write/reference/unset environment names were already explicitly
Unsupported; they were not admitted mismatches. Literal-concat variable names also
remain an old compiler-line boundary (concat-cv-originals.json). Zend parser-ZVAL
folding and its no-error guard are not equivalent to arbitrary constant FACTS;
probe unary/folded contexts before deciding their exact source classification.

Ordinary omissions should use nullable Array_.items plus exact initial context,
not a new ArrayHole constructor. Preserve indices. The engine diagnoses a null
entry at the previous nonempty element's original AST line, or current compiler
line when first. Do not substitute keyed-item start or folded-child fact lines.
Sixteen fresh `.tools/array-hole-line-originals.json` observations need independent
repetition/archive before schema changes; include keyed/unpack/arithmetic/concat
and nested-first-hole controls. Generated domain merging/remapping must cover all
adapter/printer/semantic consumers and skipped versus reached compiler visits.

Comparison/truth/control corrections and all originals remain retained. Partial
FACTS, ordinary values, executable ACCESS, redirects and permanent POOLS stay
separate. Namespace-relative `static` is the sole intentional divergence, with
source activation pending. Calls/frames, objects/linking, dynamic sources,
callbacks/unwinding and lifetime/collection remain unfinished.

Before expensive campaigns, save watched bytes and run evidence/inventory preflight.
An earlier archive-fixture omission forced a complete comparison rerun; do not
repeat it. Never alter fingerprints to conceal drift or count Unsupported/tool
failure/budget as agreement. Final complete syntax and a fresh offline rebuild
remain required; copied binaries are not portability evidence.
