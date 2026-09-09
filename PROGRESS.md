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
| 2b | Arrays, strings, lvalues and sequencing | Partial — array and string reads/writes/references reviewed; foreach and broader contexts pending |
| 3a | Control, exceptions, diagnostics and unwinding | Partial — conditionals/loops/jumps reviewed; exceptions and unwinding pending |
| 3b | Calls, closures and independent static checks | Partial — type/signature/compiler helpers reviewed; activation pending |
| 4a | Class linking, inheritance, traits, visibility and clone | Partial — local headers/relations reviewed; linking pending |
| 4b | Properties, modern declarations and internal protocols | Pending |
| 5a | Dynamic sources, autoload and explicit services | Pending |
| 5b | Generators/Fibers, lifetime, collection and callbacks | Pending |
| 6 | Full inventory/review closure, differential campaign and offline audit | Pending |

## Active ownership

- Reviewer: independent source/helper gates, discrepancy history, inventory and closure evidence.
- Runtime bridge: truth/short-circuit/ternary and comparisons, then compound/numeric operations and arrays/foreach.
- Compiler successor: coordinate truth folding, then unpack/destructuring descriptors and declarations/defaults/frames.
- Shared tree: stage owned files, commit independently reviewed increments, never push.

## Accepted evidence

- **169 constructors, 306 runtime obligations; one obligation closed**:
  [oracle selection/identity](coverage/semantics/oracle-pin-review.json), independently
  reviewed at `6b5981cc`. No constructor or PHP semantic family closes. Governance
  `ffdc131d` binds closure to source cases/raw bytes and independent review;
  `--complete` additionally rejects stale fingerprints and unfinished obligations.
- Source machine passed **747 exact source comparisons +25 outcome negatives**
  after reviewed control activation `d87f3f9f`. Legacy traversal retirement `846dc3d2` and
  temporary-lvalue errors `32d4163a` remain covered.
  [Independent review](coverage/semantics/traversal-temporary-review.json) records
  38 alternate exact sources plus two Unsupported boundaries at `57bff379`. Compiler/pool bridge `537d13de` makes full compilation
  precede execution; real filename bytes are bound before compilation, failed
  compilation suppresses recorded work, and successful work executes once with
  lexical origins. Permanent pools supply compiled read operands with effective lines and byte diagnostics.
  [Independent evidence](coverage/semantics/runtime-compiler-review.json) retains source, state and byte probes.
  Generic scalar/string reads are now active, with 64 additional exact source
  probes in [read evidence](coverage/semantics/dimension-read-review.json).
  String writes/reference errors passed 103 alternate exact sources. Temporary
  scalar/array/expression targets now reject during compilation with correct ordering. [Write evidence](coverage/semantics/dimension-write-review.json)
  retains ordering, captured locations/COW and the final helper gates.
- Ordered compiler/access and constant helpers passed **789 native lint cases,
  15 emission-line observations, 4 Unsupported contexts**, 8 sources/24 access
  roles, metadata/export controls and independent alternates. Partial AST facts,
  ordinary code-generation values and executable access descriptors stay distinct.
  [SOURCE-COMPILER](docs/semantics/SOURCE-COMPILER.md) and
  [CONSTANT-CONTEXT](docs/semantics/CONSTANT-CONTEXT.md) describe the source consumer.
- Origin/pool/ownership gates passed 25 checked traces/333 assertions,
  24 pool boundaries +100 graphs/1,623 assertions, and 617 ownership graphs
  +96 boundaries/5,434 assertions. Expanded independent graphs, multiple units,
  equal-metadata paths, encoded sources and budget resumption also passed.
  [COMPILED-POOLS](docs/semantics/COMPILED-POOLS.md) records permanent roots and
  identity contracts. Source loops preserve them; functions and dynamic instances remain pending.
- Array element references `f56e12bc` preserve entry alias replacement,
  target-before-CV initialization, captured-source ownership across COW and cycles.
  [ARRAY-HANDOFF](docs/semantics/ARRAY-HANDOFF.md) retains reviewed contracts.
  Pure dimension reads `9ec050a1` and writes/errors `9990d23e` passed 583 and
  2,220 runtime comparisons plus boundary controls. Source dispatch is active; see
  [DIMENSIONS](docs/semantics/DIMENSIONS.md).
- Compiler/frontend `9658958c` passed 233 checked prefixes plus 64 independent
  alternates, seen-symbol/barrier/resumption controls and four encoding profiles.
  Anonymous brace metadata and valid import aliases are corrected. Terminator
  metadata `64e320b0` corrects all 14 bare-break line witnesses; 20 metadata
  profiles/200 checks, eight alternate sources/five mutations, schema parity,
  bounded syntax tests and inventory passed. Declaration/default and function-body compilation remain incomplete. Control body metadata `3a137a36` also
  passes 43 profiles/430 checks, 12 independent profiles/96 checks, deterministic
  schema regeneration and bounded syntax tests;
  [review evidence](coverage/semantics/control-metadata-review.json) distinguishes
  single statements from synthetic brace/colon bodies. Name resolver `5a6de4ca` now feeds constant source lookup `d5d28dc6`: 40 sources
  +15 descriptor checks,43 independent sources and19 runtime states passed.
  [Namespace evidence](coverage/semantics/namespace-constants-review.json) retains
  qualification, fallback timing, cache contexts and resumed origins.
- [Historical full syntax audit](coverage/frontend-syntax-repair.json): **30,980 ordered records**
  — 30,671 pass, 254 parser rejections, 41 individually classified compile-phase
  differences, 6 redirects and 8 non-source records. Targeted/generated/deep checks
  passed; 539 inputs matched the snapshot. Copied executables
  establish no new rebuild/portability claim. This audit is historical after the
  terminator metadata change; final full syntax/offline validation remains required.
- Numeric suffix/NUL repair `9fc9628f`, compiler replacement lines `72d3a65d`,
  heredoc/nowdoc lines `4297dadf`, filename transport `0270197e` and lossless test
  diagnostics `49854949` are reviewed. Original failures remain unchanged in
  [DISCREPANCIES](docs/semantics/DISCREPANCIES.md); relevant regressions remain in
  current campaigns. See [NUMERICS](docs/semantics/NUMERICS.md) and [STATIC](docs/semantics/STATIC.md).
- Control if/elseif/else, while/do/for and literal-depth jumps pass 67 independent
  exact sources, 20 alternate compiler cases, 16 metadata and two path-order checks.
  Canonical 40 source/41 state cases pass 1,231 assertions; dense replay adds
  2,493 assertions over 163 budgets for each of three nested/COW programs.
  [Control review](coverage/semantics/control-review.json) retains exact evidence.
- **146 independent oracle targets; 86 integrated**. Edited helper checks and
  oracle-only observations establish no source runtime coverage.

## Next gates and retained decisions

Runtime next connects truth/short-circuit/ternary and comparisons, then compound
lvalues and remaining numeric operations/casts. The compiler successor coordinates
truth-fold ordering before unpack/destructuring and declaration/default/frame work.
Array unpack/destructuring precedes foreach's persistent cursor/ownership rules. The
[qualified constant alias discrepancy](coverage/semantics/qualified-constant-alias-disagreement.json)
is resolved by `d5d28dc6`: all seven originals agree, including preceding output
before missing-name errors. Original failures and temporary guard `ff941f17`
remain in the ledger.

All 16 read/prepass and eight write/error-order witnesses, array/reference
regressions and applicable compiler emission-line witnesses are mandatory when
those source branches activate. Ordinary compilation visits below assignment
prepass barriers; preserve key coercion, delayed reads and owner timing.

Uncollected cycles retain observable reference owners. Constant occurrences reuse
installed values; distinct NaN-array occurrences retain distinct identity.
Collection and repeated function execution remain pending; repeated loop
occurrences now reuse their installed pools.
Production bare source helpers and recursive classifiers are retired; unchecked
origin tracing exists only in the test fixture.
The reviewed [reviewer handoff](docs/semantics/REVIEWER-HANDOFF.md) records exact
commands, ownership and high-risk next witnesses.

CORE's environment/intrinsic boundary remains fixed. Numeric source contexts,
remaining control, calls, linking, objects, dynamic sources, callbacks and resumable lifetime
remain incomplete. Relative `static` has one intentional divergence in the ledger,
with source activation evidence pending. Other observed engine irregularities
follow the pin.

Unsupported, crashes, timeouts and interrupted runs never count as passes.
Closure requires full obligation scope, specific original-source cases, current
fingerprints, independent review and separate intentional-divergence evidence.
`python3 scripts/check-semantic-inventory.py --complete` must reject unfinished
entries; evidence-negative checks remain part of `make test-semantics`.
