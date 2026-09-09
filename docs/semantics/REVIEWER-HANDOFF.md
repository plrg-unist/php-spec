# Independent review continuation

Read PLAN.md, PROGRESS.md, applicable AGENTS.md and the php/php-spec/p4-spectec
skills first. Continue complete core semantics; root orchestrates, runtime_next
implements runtime/storage, compiler_next owns compiler/frontend, and the reviewer
owns independent evidence, discrepancy history, inventory, PROGRESS and README.
Never push. Stage owned files and coordinate Git index, build starts and freezes.
No PHP semantic family closes from the bounded checkpoints below.

## Current accepted checkpoint

Comparison implementation `0e065cc6` and author reports `c94459fd`
pass **1,142 exact source observations +25 outcome negatives** on `ba6075cd569573bc5f19ec661e4da74a07079a0f9b87873b8544994d3f1f07f2`.
[Comparison review](../../coverage/semantics/comparison-review.json) adds 38 public
source alternatives, 34 compiler alternatives plus 24 access checks, and six
programs across 163 budgets each (4,974 assertions), including thrown recursion
errors. A separate 83-pair/166-assertion string-order helper gate has exact loaded
specification bytes matching production; it is not 83 source-runtime comparisons.
Author comparison 232/3,388, comparison compiler 48/8/24, broad compiler 1,184/15,
origins 25/333, runtime compiler 15/148 and ownership 617+96/5,434 pass the final
closure. Both retained overflow mismatches now agree through public source; all
four originals and 48 phase originals remain byte-identical and source-integrated.

The earlier candidate passed semantic gates but failed evidence.py because both
isolated fixture roots omitted newly mandatory comparison archives. The final
fixture repair seeds them and rejects changed/missing inputs. Preflight passes
15 identity, three path and 17 closure negatives; nine build-log changes are
ignored. Actual one-byte mutation/restoration of each consumed archive changes
shared and both helper fingerprints. Earlier successful runs are historical.

Truth `e7dac829`/review `682bcba0`, control `d87f3f9f`, scalar/array/string lvalues,
ordered compiler/pool bridging and namespace constants remain covered. Frontend
unpack preservation `d4706937`/review `d4231d20` and array syntax kind
`09f33419`/review `b0f11653` precede comparisons. Detailed contracts and latest
drafts are in [runtime continuation](RUNTIME-SUCCESSOR-HANDOFF.md) and
[compiler continuation](COMPILER-HANDOFF.md).

## Immediate open admitted defect: false reference FETCH

[Originals and independent repeats](../../coverage/semantics/false-reference-fetch-review.json)
retain **three admitted mismatches and four matching controls**. After
`$a=false;$r=&$a`, nested `$a[0][0]=1` and `$x=&$a[0]` omit the pinned conversion
deprecation but the current model emits it. The difference survives `unset($r)`.
Final `$a[0]=1` assignment still warns in both implementations. This is an
existing source defect, not a comparison regression; the runtime is not globally
clean. Repair it before admitting inc/dec or compound mutations.

Runtime scratch `30/33/37/40-reference-wrappers.watsup` proposes REFCELLS history
on stable cell IDs, separate from owner counts/roots. It is **not independently
approved**. Audit acquisition/binding, ordinary writes, singleton unset, root and
element rebinding, fresh ordinary bindings, ALIAS/DIRECT COW transitions, cycles,
cleanup and resumption. Markers must not become GC roots or leak compiler reference
state into permanent pools. Preserve wrapper identity on the original while a
COW copy may unwrap a singleton. Generic FETCH versus final ASSIGN_DIM must remain
distinct. Recheck all seven raw originals, expanded state graphs and full source;
add resolution evidence separately without overwriting originals.

A further author-only four-source capture in
`.tools/false-reference-unset-disagreement.json` reports two nested UNSET fetch
mismatches and two controls. Preserve and independently repeat it next; generic
UNSET fetch in module38 also needs wrapper-history review. Final UNSET_DIM must
retain its own warning behavior. These four cases are now independently archived/repeated in
coverage/semantics/false-reference-unset-{originals,review}.json; they are distinct
from the seven earlier originals.

## Compiler/frontend prerequisites and next interfaces

- First-hole metadata draft `.tools/ParserAbstract-first-hole.php` retains an
  actual first comma token line before Error placeholders become null. Empty
  list() has a placeholder at ')', which is not a leading omission. Two retained
  sources have identical old checked ASTs but native errors on lines 1 and 2.
  Gate this separately with source encodings, malformed/edited context and bounded
  syntax. Original 28 loss witnesses and partial resolutions remain in the ledger.
- Genuine-list target conversion is a separate phase repair. Sixteen retained
  originals include native-valid skipped logical/prepass arms. Preserve earlier
  outer-style, spread, RHS read and RHS referenceability errors before long-array
  rejection. Keep original array kind, unpack and omitted entries. The previously archived single phase-gap witness is independently reviewed;
  all 22 expanded captures are now independently repeated with exact native lint
  and frontend outcomes.
- Ordinary array omissions have a broader six-source gap: native-valid skipped
  `[,$x]` branches are rejected by the frontend. A metadata-bearing ArrayHole item
  is only a proposal. Independently assess minimal faithful omission/token-line
  representation, typed adapter/printer contracts and inventory effects; avoiding
  generated type renumbering is not a sufficient reason to choose it. This work
  is distinct from genuine-list conversion and first-hole metadata.
- After wrapper repair, pair four inc/dec forms with compiler PPRW access, then
  twelve compound forms and remaining numeric/string dispatch. Preserve key reads,
  append legality, evaluation/error lines, captured locations and copied pre/post
  results. Coalescing assignment needs its own memoized quiet-read/write path.
  Compiler retains 48 update originals; 47 parse, one is a matching parser rejection.
  Runtime53 and compiler46 update drafts are unpublished.
- Array unpack/destructuring must pair compile traversal and construction with
  runtime copying/references, keys and errors. Compiler18 unpack originals remain
  scratch. Foreach needs persistent bucket/cursor identity through deletion,
  reinsertion and ownership changes. Calls/frames, declarations/defaults, classes,
  dynamic sources, callbacks, collection and resumable lifetime remain open.

Expanded frontend originals are retained in
[phase archive review](../../coverage/semantics/frontend-phase-originals-review.json):
16 genuine-list and six ordinary-array-hole captures, now independently repeated.
First-hole metadata `87341500` is accepted in destructuring-first-hole-review.json;
its compiler consumption remains pending.

## Review discipline and commands

Use only `.tools/php/bin/php` (PHP8.5.10 CLI NTS64) and the pinned profile from
`tests/semantics/static_types.py`; source pin is
`34308a6666b2d489c509541ea9befea9e2b42348`. Semantics stay pure `.watsup`.
Original source bytes/streams/status, edited checked ASTs and helper values are
separate evidence classes. Unsupported, budget exhaustion, crashes and timeouts
never count as agreement.

Run evidence/inventory **before long source campaigns whenever catalog, archive
inputs or harnesses change**. Serialize Dune build starts, finish author smoke and
save all watched bytes before the authoritative freeze. Then run one full source
campaign plus independent alternatives and applicable state/ownership gates.
Do not mutate consumed archives while gates run; test copies first and coordinate
any actual mutation/restoration. Never rewrite report fingerprints to hide drift.

- `python3 tests/semantics/evidence.py`; `python3 scripts/check-semantic-inventory.py`.
- `python3 tests/semantics/validate.py`: exact source stdout/stderr/status and
  negative outcomes. Independently audit raw ordered source IDs/bytes/hashes,
  accepted outcome categories, archive bindings and current fingerprints.
- `comparison.py`, `comparison_compiler.py`, `source_compiler.py`,
  `source_origins.py`, `runtime_compiler.py`, `ownership.py` under tests/semantics;
  add other applicable helpers when changed contracts justify them.
- `make test`, `make inventory`, parser regeneration/distribution patch
  reconstruction for frontend changes. The 30,980-record full syntax audit is
  historical; final full corpus validation and fresh offline rebuild remain required.

Current inventory is 169 constructors/306 obligations; only validation.oracle-pin
closes. No constructor closes. CORE's environment/intrinsic boundary remains
fixed. Preserve the sole intentional namespace-relative static divergence; its
source activation proof is pending. All other irregularities currently follow the
pin. Commit coherent implementation, author evidence, then reviewed status; keep
hand-off prose concise and current.
