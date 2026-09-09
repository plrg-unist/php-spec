# Core semantics progress

Target: PHP 8.5.10 CLI NTS 64-bit; [plan](PLAN.md),
[contract](docs/semantics/CORE.md), [inventory](coverage/semantics/features.json).
Complete core remains the goal. Syntax coverage is not semantic coverage.

## Milestones

| Milestone | Deliverable | Current status |
| --- | --- | --- |
| 0a | Core/environment/observation contracts and inventory | Complete — contracts only |
| 0b | Checked AST runner and original-source differential harness | Complete — bounded bootstrap reviewed (`8b856a27`) |
| 1a | Pure integers/bytes and result typing | Partial — helpers reviewed; scalar arithmetic source bridge reviewed |
| 1b | Pure binary64 and rounding | Partial — add/sub/mul/div reviewed through helper and scalar source paths |
| 1c | Numeric text, conversions, formatting, power | Partial — text/formatting/context/power helpers reviewed; source contexts partial |
| 2a | Slots, aliases, frames and access modes | Partial — scalar bindings/refs reviewed (`5a083605`); frames/global/property access pending |
| 2b | Arrays, strings, lvalues and sequencing | Partial — reads/writes/unset and variable/element reference sources and targets reviewed; pure string reads reviewed; source offsets/foreach pending |
| 3a | Control, exceptions, diagnostics and unwinding | Pending |
| 3b | Calls, closures, binding and independent static checks | Partial — local types/signatures reviewed; calls/activation pending |
| 4a | Class linking, inheritance, traits, visibility and clone | Partial — local class headers reviewed; linking/activation pending |
| 4b | Properties, modern declarations and internal protocols | Pending |
| 5a | Checked dynamic sources, autoload and explicit services | Pending |
| 5b | Generators/Fibers, lifetime, collection and callbacks | Pending |
| 6 | Full inventory/review closure, differential campaign and offline audit | Pending |

Commit each reviewed increment. Constructor and runtime-obligation statuses remain
separate; helper checks cannot establish source semantics. Unsupported, crashes,
timeouts and interrupted campaigns never count as validation passes.

## Assignments and interfaces

- Reviewer owns progress/inventory/contracts, independent witnesses and review gates.
- References agent owns source execution/storage; read
  [ARRAY-HANDOFF](docs/semantics/ARRAY-HANDOFF.md). Element-reference targets
  `f56e12bc`, numeric-boundary repair `9fc9628f` and pure dimension reads
  `9ec050a1` are reviewed; pure string writes `9990d23e` are reviewed; source dimensions are next.
- Static worker owns checked compiler context and source facts. Structural
  occurrences `898f0152`, bounded namespace/import contexts `891c2c95` and
  frontend location/import-alias repair `9658958c` are reviewed. Shared constant
  facts `93eeb749` are reviewed; ordered compiler work and runtime origins are next. [LINKING-HANDOFF](docs/semantics/LINKING-HANDOFF.md)
  records pending applicability, internal metadata, linking and activation.
  Coordinate source-unit/task integration with the references owner.
- Numeric helpers are pure; runner owns PHP values/effects. See NUMERICS.
  Storage uses cells, captured versus delayed operands and internal array IDs.
  Nested dimension descriptors preserve fetch timing; graph copies account for
  admitted literal reference entries and uncollected cycles. See DESIGN.
- Shared working tree: stage owned files only, never push. Baseline `082a3a2b`;
  the workspace gitlink was already modified. Commit each reviewed increment.

## Current evidence and decisions

- Inventory: 169 constructors and 306 runtime obligations, all pending/partial
  at full-core scope. `coverage/semantics/` retains bounded reports; git history
  records earlier milestone counts. Historical acceptance fingerprints are
  explicit; later implementation changes require fresh applicable evidence.
- Source machine: latest independently repeated **514 exact source comparisons
  +25 negatives** at `9fc9628f`. Element-reference targets `f56e12bc` additionally
  passed 617 graph +96 boundary cases and 57 independent topology/timing probes.
  Entry alias replacement, target-before-CV initialization and captured-source
  ownership across COW are reviewed. Earlier CV and reference-result defects and
  mandatory witnesses remain linked in [DISCREPANCIES](docs/semantics/DISCREPANCIES.md).
  String source dimensions, nonarray reads and source GC remain pending.
- Pure dimension-read helper `9ec050a1`: **583 runtime comparisons +10 compiler
  leaves +5 boundaries**, 2,318 assertions; 1,456 independent expanded runtime
  pairs passed. This helper is unregistered in the source machine; constant leaf
  folding alone does not establish compiler prepass traversal. See
  [DIMENSIONS](docs/semantics/DIMENSIONS.md).
- Numeric-boundary correction `9fc9628f` follows the pin’s suffix/NUL and invalid
  signed-exponent behavior, including wrapped integers. Source and expanded
  numeric gates passed; [104 raw observations](coverage/semantics/numeric-boundary-disagreement.json)
  preserve 28 former disagreements, all resolved. Seven witnesses are mandatory.
- Pure string-write/fetch helper `9990d23e`: **2,220 runtime +12 boundary cases**,
  12,040 assertions; 2,056 independent expanded cases passed. Key conversion,
  negative bounds before delayed RHS reads, byte writes and reference/nested errors
  are reviewed. Source location commits and callback ownership remain pending.
- Constant-expression helper `93eeb749`: **42 original source observations +7
  boundaries**, plus 37 independent expanded observations passed. Exact occurrence
  facts retain partial folds, persistent array roots, same-path reuse and distinct
  NaN-array paths. Nested compile-error priority/lines and assignment barriers are
  reviewed. [CONSTANT-CONTEXT](docs/semantics/CONSTANT-CONTEXT.md) defines the
  explicit invocation contract; ordinary compiler scheduling and runtime pool
  installation remain pending.
- Pure numeric helpers are independently reviewed; [NUMERICS](docs/semantics/NUMERICS.md)
  and [power provenance](docs/semantics/POWER-PROVENANCE.md) retain exact campaigns.
  Reviewed type/signature/class-header/covariance/method helpers and their expanded
  independent matrices are recorded in [STATIC](docs/semantics/STATIC.md).
  Edited checks do not repair frontend gaps; source declaration/default/body
  compilation, linking and call activation remain pending.
- Structural source units `898f0152` retain exact checked ASTs and stable unit/path
  identities across all 169 constructors. [SOURCE-CONTEXT](docs/semantics/SOURCE-CONTEXT.md)
  records 1,497 structural assertions and expanded source checks. These are
  representation checks, with no source compilation/evaluation claim.
- Namespace/import compiler and frontend repair `9658958c`: **233 original
  checked prefix comparisons** plus 64 independent alternates passed; 24 explicit
  seen-symbol inputs, 6 work barriers, 3 environments, 13 resumptions and 4
  negatives. Checked anonymous-brace locations and valid function/constant import
  aliases now cross the source frontend. Four encoding profiles/40 metadata checks
  retain exact transport and reject malformed fields. Ordinary body/default
  compilation and runtime activation remain pending; 27 grammar rejections remain
  separately classified. [Raw line history](coverage/semantics/compiler-context-line-disagreement.json)
  preserves the resolved defect.
- Full syntax repair audit: **30,980 ordered corpus records**, 30,671 pass,
  254 parser rejections, 41 individually classified compile-phase differences,
  6 redirect containers and 8 non-source records. Targeted/generated/deep checks
  and complete grammar/scanner inventory passed; 539 final syntax inputs match
  the immutable snapshot. [Audit and commands](coverage/frontend-syntax-repair.json)
  retain exact corpus membership and fingerprints. Copied executables establish
  neither a fresh rebuild nor portability; syntax results establish no semantics.
- **146 independent oracle targets**, 62 integrated into the reviewed source
  harness. `conformance-oracle.json` alone never establishes semantic coverage.
- Preserve delayed reads, self-assignment capture, cyclic arrays, NaN identity
  and exact compiler lines. [CORE](docs/semantics/CORE.md) records pending literal
  occurrence identity and uncollected-cycle ownership witnesses: GC changes copied
  array mutation from 99 to 19. Reachability-only owner counting is insufficient.
- CORE fixes the environment/intrinsic boundary; unfinished families remain core.
  [DISCREPANCIES](docs/semantics/DISCREPANCIES.md) records the intentional relative
  `static` interpretation (avoiding the compiler crash/parent substitution) and
  separate static-return variance irregularities that must follow the pin.
  Source activation still needs intended-divergence witnesses.

## Next gates

Thread source origins through the unchanged source machine, then integrate ordered
compiler work and the reviewed constant pool before source dimensions. Preserve folding,
assignment barriers, key conversion, diagnostic and temporary-owner timing.
All 16 read/prepass and eight write/error-order oracle targets, plus existing element-target/prepass witnesses
are mandatory in the next source gate. Source-context traversal and class linking
must preserve pinned phase ordering and stable literal-occurrence identity.
Covariance remains a helper over supplied visible class graphs, with no source
activation, autoload schedule or production declaration diagnostics.
Phase1 remains partial: source power, remainder/shifts/bitwise/incdec/casts,
mixed comparisons, handlers and configurable precision need integration.
Control/calls/objects/dynamic sources/resumable execution/lifetime remain pending.

`python3 scripts/check-semantic-inventory.py --complete` rejects unfinished
entries; source/helper evidence and independent review remain separate.
Before the first family closes, strengthen this gate to check obligation-specific
case IDs/current report fingerprints and intentional-divergence source evidence.
Fourteen isolated evidence negatives reject source/config/data/binary/path drift
and missing, escaping or unproved evidence. Nine generated build-log changes
preserve identity; executed adapter/helper binaries remain hashed.
`make test-semantics` includes these checks.
