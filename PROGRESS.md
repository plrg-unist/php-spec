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
| 2b | Arrays, strings, lvalues and sequencing | Partial — reads/writes/unset and variable/element reference sources and targets reviewed; string offsets/foreach pending |
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
- References agent owns source execution/storage after reviewed ownership `41e8fa2b`;
  read [ARRAY-HANDOFF](docs/semantics/ARRAY-HANDOFF.md). Scoped HELD and driver
  pruning, owning reference results, COW/union and variable-source literal refs
  `4b954dfa` and CV timing/classification repair `eea66b2d` are reviewed.
  Element-reference targets `f56e12bc` are reviewed; scalar/string dimensions next.
- Static worker: structural source-unit occurrences `898f0152` and bounded
  namespace/import contexts `891c2c95` reviewed; next checked compiler-location
  metadata and valid import-alias frontend repair, then further declarations.
  [LINKING-HANDOFF](docs/semantics/LINKING-HANDOFF.md) records reviewed helper
  interfaces and pending applicability, internal metadata, linking and activation.
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
- Source machine `f56e12bc`: independently repeated **507 exact source comparisons
  +25 negatives**; variable/element references, literal entries, COW/union and
  owning results included. **617 graph +96 boundary cases**, 5,434 assertions,
  plus 57 independent target topology/timing probes passed. Element assignment
  replaces the entry's alias; target designation precedes CV initialization,
  while captured non-CV sources retain an owner across target COW.
  String dimensions, nonarray reads and source GC remain pending.
  See [handoff](docs/semantics/ARRAY-HANDOFF.md).
- CV timing/classification defects are resolved in `eea66b2d`: delayed reference
  target names now warn before direct source initialization; literal-float names
  use delayed reads (PHP/spec 4). All nine witnesses are mandatory. The five
  original disagreements, four controls and accepted resolution remain
  [retained](coverage/semantics/reference-timing-disagreement.json).
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
- Namespace/import compiler helper `891c2c95`: **211 original checked prefix
  comparisons** plus 64 independent alternates passed; 24 explicit seen-symbol
  inputs, 6 work barriers, 3 environments, 13 resumption/missing-brace cases and
  4 negatives. The multiline import-line defect is resolved and
  [raw history retained](coverage/semantics/compiler-context-line-disagreement.json).
  Anonymous brace locations and 12 valid function/constant alias frontend gaps
  remain pending. Edited helper cases do not close source gaps; body compilation
  and source runtime activation remain pending.
- **131 independent oracle targets**, 55 integrated into the reviewed source
  harness. `conformance-oracle.json` alone never establishes semantic coverage.
- Reference-result defect resolved in `751fbcff`: `($x=&$a)+($a=2)` with `$a=1`
  now gives PHP/spec 4. Owning reference operands retain the captured cell and read
  its current value at consumption. [Raw discrepancy](coverage/semantics/reference-result-disagreement.json)
  preserves the prior spec 3 and binds the accepted mandatory regression.
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

Review pure scalar/string dimension helpers before source integration; preserve
constant-array prepass folding and assignment barriers as well as key conversion,
diagnostic and temporary-owner timing. All 16 new read/prepass oracle targets are
mandatory in the next source gate; writable/reference string contexts follow. Element-target
and array-prepass witnesses remain mandatory. The reviewed compiler helper uses name-derived import/namespace lines. Next
repair missing anonymous-brace metadata and import-alias frontend acceptance,
then independently validate the complete syntax corpus in an immutable snapshot.
The next static source-context traversal and class linking must preserve pinned
phase ordering and stable literal-occurrence identity.
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
