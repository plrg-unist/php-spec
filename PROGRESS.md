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

- Reviewer: progress/inventory/contracts, independent witnesses and acceptance gates.
- References: runtime/storage, now permanent compiled-unit pool ownership and source
  consumers. Read [ARRAY-HANDOFF](docs/semantics/ARRAY-HANDOFF.md) and
  [SOURCE-ORIGINS](docs/semantics/SOURCE-ORIGINS.md).
- Compiler: ordered ordinary compilation, lexical context and retained constant
  facts. Read [CONSTANT-CONTEXT](docs/semantics/CONSTANT-CONTEXT.md),
  [SOURCE-CONTEXT](docs/semantics/SOURCE-CONTEXT.md) and
  [LINKING-HANDOFF](docs/semantics/LINKING-HANDOFF.md).
- Shared tree: stage owned files only, commit each independently reviewed increment,
  never push. Workspace gitlink was already modified; project baseline `082a3a2b`.

## Accepted evidence

- Inventory: **169 constructors, 306 runtime obligations; zero closed**. Every
  family remains pending/partial at full-core scope. Reports retain historical
  acceptance fingerprints; changed inputs require fresh applicable evidence.
- Current source machine `cb02399c`: independently repeated **514 exact source
  comparisons +25 negatives**, about 167 seconds. Origin propagation passed
  25 canonical traces/331 assertions, 41 expanded traces/491 assertions, explicit
  equal-metadata path sequences, multiple source IDs, UTF-16LE retention and
  budget resumption. Unit/path lookup validates the selected node; node equality
  never selects occurrence identity. Ownership: **617 graph +96 boundary cases**,
  5,434 assertions. Permanent pool consumption is not installed.
- Element-reference targets `f56e12bc` preserve entry alias replacement,
  target-before-CV initialization, owning captured sources across COW and cycles.
  Earlier CV/reference-result defects and their mandatory regressions are resolved;
  [DISCREPANCIES](docs/semantics/DISCREPANCIES.md) retains original raw disagreements.
- Pure dimension helpers: reads `9ec050a1` passed 583 runtime comparisons and
  compiler/boundary controls; writes/fetch errors `9990d23e` passed 2,220 runtime
  comparisons plus 12 boundaries. Expanded independent matrices passed. These
  remain outside source dispatch; [DIMENSIONS](docs/semantics/DIMENSIONS.md) records
  key coercion, byte bounds, diagnostic order and delayed RHS contracts.
- Constant helper `93eeb749`: 42 original observations plus 7 boundaries and 37
  independent alternates passed. Partial facts, same-path reuse, distinct NaN-array
  paths and isolated pool roots are reviewed. Ordinary compiler scheduling and
  runtime pool installation remain pending.
- Compiler/frontend `9658958c`: 233 checked prefix comparisons plus 64 independent
  alternates; seen-symbol, work-barrier, resumption and metadata controls passed.
  Anonymous brace locations and valid function/constant import aliases are fixed.
  Declaration/default/body compilation and runtime activation remain pending.
- [Full syntax repair audit](coverage/frontend-syntax-repair.json): **30,980 ordered
  records** — 30,671 pass, 254 parser rejections, 41 individually classified
  compile-phase differences, 6 redirect containers and 8 non-source records.
  Targeted/generated/deep and grammar/scanner checks passed; 539 final syntax inputs
  matched the immutable snapshot. Copied executables establish no fresh rebuild
  or portability claim. Earlier portability evidence remains historical.
- Pure numeric and static helper campaigns are linked in
  [NUMERICS](docs/semantics/NUMERICS.md) and [STATIC](docs/semantics/STATIC.md).
  Numeric boundary repair `9fc9628f` follows the pin's suffix/NUL and invalid
  signed-exponent behavior; all 104 retained source observations now agree.
- **146 independent oracle targets; 62 integrated**. Oracle-only observations and
  edited helper checks establish no source semantic coverage.

## Next gates and retained decisions

Review ordered compiler work, then install permanent compiled-unit pools before
source dimensions. The draft currently loses effective lines on constant AST
replacements: six raw disagreements and four controls are retained in
[DISCREPANCIES](docs/semantics/DISCREPANCIES.md); correction is required before
compiler acceptance. Pool roots must survive temporary cleanup; installation must
reserve disjoint allocation IDs. Runtime tasks consume facts by unit/path, while
ordinary compilation still visits children below constant-prepass assignment
barriers. Preserve compiler lines, key conversion, delayed reads and owner timing.
All 16 read/prepass and eight write/error-order witnesses, plus existing array and
reference regressions, are mandatory when their source branches activate.

Uncollected cycles retain observable reference owners; reachability-only counting
is insufficient. Repeated literal occurrences must reuse their compiled value,
while distinct NaN-array occurrences retain distinct identity. Collection and
loop/function literal execution remain pending.

The CORE environment/intrinsic boundary remains fixed. Numeric source contexts,
control, calls, linking, objects, dynamic sources, callbacks and resumable lifetime
remain incomplete. Relative `static` has one intentional divergence in the ledger;
source activation still needs its intended-divergence witnesses. Other recorded
variance/numeric irregularities follow the pinned engine.

Unsupported, crashes, timeouts and interrupted campaigns never count as passes.
`python3 scripts/check-semantic-inventory.py --complete` rejects unfinished entries;
source/helper evidence and independent review remain separate. Before any family
closes, require obligation-specific case IDs, current report fingerprints and
intentional-divergence source evidence. Existing evidence-negative checks remain
part of `make test-semantics`.
