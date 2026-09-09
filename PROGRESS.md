# Core semantics progress

Target: PHP 8.5.10 CLI NTS 64-bit; [plan](PLAN.md),
[contract](docs/semantics/CORE.md), [inventory](coverage/semantics/features.json).
Complete core remains the goal. Syntax coverage is not semantic coverage.

## Milestones

| Milestone | Deliverable | Current status |
| --- | --- | --- |
| 0a | Contracts and inventory | Complete — contracts only |
| 0b | Checked AST runner and original-source harness | Complete — bounded bootstrap |
| 1a | Integers/bytes and result typing | Partial — helpers and scalar arithmetic source bridge reviewed |
| 1b | Binary64 and rounding | Partial — basic arithmetic helpers/source paths reviewed |
| 1c | Numeric text, conversions, formatting, power | Partial — helpers reviewed; source contexts partial |
| 2a | Slots, aliases, frames and access modes | Partial — scalar bindings/references reviewed; frames/global/property access pending |
| 2b | Arrays, strings, lvalues and sequencing | Partial — array reads/writes/unset/references reviewed; string source offsets/foreach pending |
| 3a | Control, exceptions, diagnostics and unwinding | Pending |
| 3b | Calls, closures and independent static checks | Partial — type/signature/compiler helpers reviewed; activation pending |
| 4a | Class linking, inheritance, traits, visibility and clone | Partial — local headers/relations reviewed; linking pending |
| 4b | Properties, modern declarations and internal protocols | Pending |
| 5a | Dynamic sources, autoload and explicit services | Pending |
| 5b | Generators/Fibers, lifetime, collection and callbacks | Pending |
| 6 | Full inventory/review closure, differential campaign and offline audit | Pending |

## Active ownership

- Reviewer: independent source/helper gates, discrepancy history, inventory and closure evidence.
- Runtime bridge: source dimensions next, then control/loops and unpack/destructuring/foreach.
- Compiler: namespace constant lookup, then declarations/defaults and calls.
- Shared tree: stage owned files, commit independently reviewed increments, never push.

## Accepted evidence

- **169 constructors, 306 runtime obligations; zero currently closed**. This is an
  obligation-specific assessment, not a requirement to wait for global completion.
  Strengthening closure evidence and assessing completed scopes is active work.
- Source compiler/pool bridge **`537d13de`** passed **546 exact source comparisons
  +28 outcome negatives**, independently repeated in 217 seconds. Full compilation
  precedes execution; real filename bytes are bound before compilation, failed
  compilation suppresses recorded work, and successful work executes once with
  lexical origins. Permanent per-unit pools remap array IDs and supply only compiled
  read operands; effective lines and byte diagnostics survive execution.
  [Independent evidence](coverage/semantics/runtime-compiler-review.json) retains
  16 alternate sources, 16 constructed states/138 assertions and four byte probes.
  Source admission includes folded string dimensions, not generic runtime offsets.
- Ordered compiler/access and constant helpers passed **582 native lint cases,
  15 emission-line observations, 10 Unsupported contexts**, 8 sources/24 access
  roles, metadata/export controls and independent alternates. Partial AST facts,
  ordinary code-generation values and executable access descriptors stay distinct.
  [SOURCE-COMPILER](docs/semantics/SOURCE-COMPILER.md) and
  [CONSTANT-CONTEXT](docs/semantics/CONSTANT-CONTEXT.md) describe the source consumer.
- Origin/pool/ownership gates passed 25 checked traces/333 assertions,
  24 pool boundaries +100 graphs/1,623 assertions, and 617 ownership graphs
  +96 boundaries/5,434 assertions. Expanded independent graphs, multiple units,
  equal-metadata paths, encoded sources and budget resumption also passed.
  [COMPILED-POOLS](docs/semantics/COMPILED-POOLS.md) records permanent roots and
  identity contracts. Source loops/functions and dynamic instances remain pending.
- Array element references `f56e12bc` preserve entry alias replacement,
  target-before-CV initialization, captured-source ownership across COW and cycles.
  [ARRAY-HANDOFF](docs/semantics/ARRAY-HANDOFF.md) retains reviewed contracts.
  Pure dimension reads `9ec050a1` and writes/errors `9990d23e` passed 583 and
  2,220 runtime comparisons plus compiler/boundary controls and independent
  matrices. Generic source dispatch remains next; see
  [DIMENSIONS](docs/semantics/DIMENSIONS.md).
- Compiler/frontend `9658958c` passed 233 checked prefixes plus 64 independent
  alternates, seen-symbol/barrier/resumption controls and four encoding profiles.
  Anonymous brace metadata and valid import aliases are corrected. Full declaration,
  default and body compilation remain incomplete. Name resolver `5a6de4ca` passed
  61 original sources +7 boundaries and 20 independent probes; runtime lookup is next.
- [Full syntax audit](coverage/frontend-syntax-repair.json): **30,980 ordered records**
  — 30,671 pass, 254 parser rejections, 41 individually classified compile-phase
  differences, 6 redirects and 8 non-source records. Targeted/generated/deep checks
  passed; 539 syntax inputs matched the immutable snapshot. Copied executables
  establish no new rebuild/portability claim. Syntax coverage is not semantics.
- Numeric suffix/NUL repair `9fc9628f`, compiler replacement lines `72d3a65d`,
  heredoc/nowdoc lines `4297dadf`, filename transport `0270197e` and lossless test
  diagnostics `49854949` are reviewed. Original failures remain unchanged in
  [DISCREPANCIES](docs/semantics/DISCREPANCIES.md); relevant regressions remain in
  current source/helper campaigns. Numeric/static detail is linked through
  [NUMERICS](docs/semantics/NUMERICS.md) and [STATIC](docs/semantics/STATIC.md).
- **146 independent oracle targets; 63 integrated**. Edited helper checks and
  oracle-only observations establish no source runtime coverage.

## Next gates and retained decisions

Runtime proceeds through generic scalar/string reads, string writes/reference
errors, control/loops, then unpack/destructuring/foreach. Compiler proceeds through
namespace constant lookup, declarations/defaults and calls. The
[qualified constant alias discrepancy](coverage/semantics/qualified-constant-alias-disagreement.json)
has temporary guard `ff941f17`: four original failures now return Unsupported,
while unmatched/unqualified controls agree. The guard is not a resolution; the
resolver consumer must reproduce the original native observations next.

All 16 read/prepass and eight write/error-order witnesses, array/reference
regressions and applicable compiler emission-line witnesses are mandatory when
those source branches activate. Ordinary compilation visits below assignment
prepass barriers; preserve key coercion, delayed reads and owner timing.

Uncollected cycles retain observable reference owners. Constant occurrences reuse
installed values; distinct NaN-array occurrences retain distinct identity.
Collection and original-source repeated loop/function execution remain pending.
Legacy bare source helpers and residual checker dependencies require retirement.

CORE's environment/intrinsic boundary remains fixed. Numeric source contexts,
control, calls, linking, objects, dynamic sources, callbacks and resumable lifetime
remain incomplete. Relative `static` has one intentional divergence in the ledger,
with source activation evidence pending. Other observed engine irregularities
follow the pin.

Unsupported, crashes, timeouts and interrupted runs never count as passes.
Closure requires full obligation scope, specific original-source cases, current
fingerprints, independent review and separate intentional-divergence evidence.
`python3 scripts/check-semantic-inventory.py --complete` must reject unfinished
entries; evidence-negative checks remain part of `make test-semantics`.
