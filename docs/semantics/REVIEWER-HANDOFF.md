# Independent review continuation

Read PLAN, PROGRESS, applicable AGENTS and the php/php-spec/p4-spectec skills first.
Root orchestrates; runtime_next owns runtime/storage, compiler_next owns compiler
and frontend, reviewer owns independent evidence, inventory and concise docs.
Never push. Stage owned files and coordinate index, build starts and watched freezes.
No PHP semantic family or constructor closes from these bounded checkpoints.

## Latest corrective checkpoint

`84d70299`/reports `fa691044` repairs ordinary WRITE_DYNAMIC incorrectly marking
reference history. All seven acquire_name call sites were audited; only that
ordinary writable fetch changes. `fetch_write_name` initializes absent/undefined
slots without adding markers; true acquisition marks afterward. Existing shared
or singleton wrappers retain history. [Review](../../coverage/semantics/wrapper-dynamic-write-review.json)
resolves all28 originals (12 mismatches/16 controls) and adds12 exact controls;
prior79 wrapper sources,49 state assertions and ownership617+96/5434 pass.
Selected30 sources/25 negatives and canonical30/505 pass `055e533c`. Helper embeds
all original bytes; independent evidence/inventory preflight passes. Full source
refresh shares the immediately following inc/dec gate, not this bounded correction.

## Accepted wrapper correction

Code `3585707a`, reports `eebf79e9` and
[review](../../coverage/semantics/reference-wrapper-review.json) pass **1,163 exact
sources +25 negatives** on `1f71f10d643374f0d0ff046d2139315e8d9692f5c0ec1a07a6e4849ccf0776ec`.
All eleven unchanged FETCH/final-write/UNSET originals are integrated; five prior
mismatches now agree. Independent evidence adds 79 exact public sources, 72 replay
programs/1,288 assertions and 45 constructed transition/owner checks. The raw audit
checks every ordered catalog ID, original byte string/hash and native/model outcome.

`REFCELLS` records stable backing-cell wrapper identity independently of owner
counts and roots. Acquisition/rebinding marks cells; writes and singleton unset
preserve history. Fresh ordinary bindings are unmarked. Array COW and union may
unwrap a singleton copied ALIAS into DIRECT while the original wrapper remains.
Markers create no edges and cannot retain dead storage. Generic nested/reference
FETCH and intermediate UNSET suppress false conversion warnings through wrappers;
final ASSIGN_DIM/UNSET_DIM retain warnings. Direct CV source acquisition follows
target FETCH, while computed-name capture can precede it. Compiler reference
markers cannot enter permanent pools; valid installation preserves runtime markers.

Canonical wrappers 21 sources/396 assertions, compiler 1,205 lints/15 ending-line
observations, origins 25/333, bridge 15/148 and ownership 617+96/5,434 pass the same
closure. Collection assertions concern pure graph helpers, not source GC calls.
No intentional divergence was selected. Original mismatch archives remain unchanged.

## Next bounded gates

- Runtime private inc/dec uses `.tools/{20-incdec-compiler,30-incdec,45-incdec-compiler,46-incdec-checked,53-incdec-source}.watsup`.
  Current this-inclusive paths30-incdec-this/40-incdec-this/41-incdec-this/53-incdec-this
  plus20-incdec-compiler/45-incdec-compiler/46-incdec-this pass140 author programs/2030
  assertions. Rebase independent dense/public gates onto these after this checkpoint. Independent earlier
  177 programs/2,478 assertions passed but exposed two array-prepass Unsupported
  gaps, retained unchanged in incdec-prepass-originals.json. Review explicit PFSTOP
  depth, static fallback priority and new callable metadata consumption before
  publication. Canonical compiler draft has108 native lints,32 access paths,8 emission lines and12
  source-context boundaries. Computed write/ref/unset remain previously explicit
  environment boundaries. Literal concat names are a pending parser-folding context
  (concat-cv-originals.json); ternary names stay computed. Pair copied pre/post results, exact error lines,
  missing targets, append rules and held locations. Compound updates follow.
- Callable invocation metadata `c6a7d67d` is independently accepted in
  callable-line-review.json: eight exact old-AST originals (identical pair reports
  native lines 3/2), 35 canonical profiles/477 checks, 24 independent profiles/168
  checks and 24 native error-line comparisons. Exact parser regeneration passes;
  the one parser semantic action preserves opening argument-token context. Optional
  integer transport is distinct from compiler requiredness/range checks. No source
  call or update admission follows from this prerequisite alone.
- First-hole token metadata `87341500`/review `79951ad4` is accepted: 31 author
  profiles/409 checks, 20 independent profiles/140 checks and all 12 original line
  witnesses. Empty list closing tokens are not commas. Integer metadata is checked
  transport; missing/range requirements remain compiler consumer obligations.
- Genuine-list conversion `5c756e5e`/review `861020db` is accepted: recursive nested
  Array_ target conversion precedes ordinary omission checking and preserves all
  original flags/context. Twenty exact skipped sources/25 negatives, 32 checked
  profiles and independent comments/archive checks pass. Fourteen reached originals
  remain Unsupported. Full source refresh shares incdec activation.
- Ordinary array omissions should use nullable Array_.items and first-omission
  context; no new ArrayHole node is justified. `zend_try_ct_eval_array` uses NULL
  entries and diagnoses at the preceding nonempty element's original AST line;
  a leading hole retains current compiler context. Preserve prepass order, skipped
  branches and hole indices. Approximately 21 consumer files need deterministic
  generated-type remapping. Sixteen new exact line originals are retained at
  `.tools/array-hole-line-originals.json` for later independent review. Review metadata, generator/adapter/printer and semantic
  consumers together. Compiler is retaining multiline/keyed/folded/nested evidence.

[Frontend phase archives](../../coverage/semantics/frontend-phase-originals-review.json)
contain all 16 genuine-list and six ordinary-array-hole originals, independently
repeated before repair. Earlier 28 metadata losses remain retained. Never overwrite
originals with repaired observations. Unpack/destructuring, foreach, calls/frames,
objects/linking, dynamic sources and callbacks/lifecycle remain open; continue the
[runtime](RUNTIME-SUCCESSOR-HANDOFF.md) and [compiler](COMPILER-HANDOFF.md) interfaces.

## Retained constraints and validation

Use only project-local PHP 8.5.10 CLI NTS64, `.tools/php/bin/php`, source pin
`34308a6666b2d489c509541ea9befea9e2b42348`. Rules stay pure `.watsup`; checked source
execution, edited ASTs and helper values are separate evidence classes. Unsupported,
crashes, timeouts and budgets never count as semantic agreement.

Comparison `0e065cc6` retains all four overflow and 48 phase originals. Truth,
control, scalar/array/string lvalues, origins and compiler pools remain reviewed.
Partial FACTS, ordinary values, executable ACCESS and redirects stay distinct;
ordinary ternary copies values while raw prepass redirects can preserve delayed
operands. Uncollected cycles remain observable owners. Namespace-relative `static`
is the sole intentional divergence, with source activation proof pending.

Run `tests/semantics/evidence.py` and `scripts/check-semantic-inventory.py` **before**
long campaigns when catalogs, archives or harnesses change. Preflight currently
passes 15 identity, three path, 17 closure negatives and nine ignored-log changes.
The wrapper helper embeds source bytes, adding no consumed archive dependency.
The earlier comparison campaign required a repeat after isolated fixtures omitted
mandatory comparison archives; do not repeat that ordering mistake.

Serialize Dune starts, save all watched inputs, then run one complete source gate
and applicable independent/helpers. Validate exact raw membership and stable
fingerprints; never edit fingerprints to conceal drift. `make test`, inventory and
patch reconstruction gate frontend changes. The 30,980-record syntax audit is
historical; final full syntax and fresh offline rebuild remain required.
Inventory: 169 constructors/306 obligations; only validation.oracle-pin closes.
