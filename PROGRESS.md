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
| 2b | Arrays, strings, lvalues and sequencing | Partial — ordinary reads/writes/unset reviewed; embedded refs/foreach pending |
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
  pruning `46772123` and owning reference results `751fbcff` are reviewed; next
  conditional COW/singleton wrapper copying, then source embedded references.
- Signatures agent owns method compatibility after reviewed covariance `8a6c5708`.
  Local types/signatures are reviewed helpers. They use explicit namespace,
  import, class, position and source contexts and ordered diagnostics; unresolved names remain explicit.
  Activation, autoload and call binding are separate machine obligations.
- Numeric helpers are pure; runner owns PHP values/effects. See NUMERICS.
  Storage uses cells, captured versus delayed operands and internal array IDs.
  Nested dimension descriptors preserve fetch timing; shallow graph copies are
  reviewed only for currently admitted reference-free entries. See DESIGN.
- Shared working tree: stage owned files only, never push. Baseline `082a3a2b`;
  the workspace gitlink was already modified. Commit each reviewed increment.

## Current evidence and decisions

- Inventory: 169 constructors and 306 runtime obligations, all pending/partial
  at full-core scope. `coverage/semantics/` retains bounded reports; git history
  records earlier milestone counts. Historical acceptance fingerprints are
  explicit; later implementation changes require fresh applicable evidence.
- Source machine `751fbcff`: independently repeated **388 exact source comparisons
  +25 negatives**; owning reference-result correction included, with 26 expanded
  reviewer source probes. Ordinary array writes/unset and profile-name fixes remain.
  `_SESSION` is ordinary here; HTTP compiler diagnostics remain pending.
- Ownership through `751fbcff`: **617 graph +34 boundary cases**, 5,146 assertions,
  independently repeated. Allocation graphs retain uncollected cycles; scoped
  HELD roots, driver cleanup and owning result cells are reviewed. COW, source
  embedded references and GC remain pending; see [handoff](docs/semantics/ARRAY-HANDOFF.md).
- Pure numeric helpers are independently reviewed; [NUMERICS](docs/semantics/NUMERICS.md)
  and [power provenance](docs/semantics/POWER-PROVENANCE.md) retain exact campaigns.
  Local types `531a8b40`/`9da9b012`, signatures `ac5bc703`, and class headers
  `187b01f2` are reviewed helpers. Covariance `8a6c5708` passed **1,028**
  checked return-type/oracle comparisons, 9 descriptors and 4 Unsupported checks;
  expanded reviewer matrix: 1,928. [STATIC](docs/semantics/STATIC.md) retains
  counts, source restrictions and expanded reviewer matrices. Edited compiler
  checks do not repair frontend phase gaps. No source activation, default
  materialization, body compilation, linking or call binding is claimed.
- **77 independent oracle targets**, 16 integrated into the reviewed source
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

Review conditional location COW and singleton wrapper copying before enabling
source embedded references; preserve retained ownership/identity discriminators.
Method compatibility and class linking must preserve pinned phase ordering.
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
