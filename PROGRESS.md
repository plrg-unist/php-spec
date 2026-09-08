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
| 3b | Calls, closures, binding and independent static checks | In progress — local type helpers reviewed; signatures active, calls/activation pending |
| 4a | Class linking, inheritance, traits, visibility and clone | Pending |
| 4b | Properties, modern declarations and internal protocols | Pending |
| 5a | Checked dynamic sources, autoload and explicit services | Pending |
| 5b | Generators/Fibers, lifetime, collection and callbacks | Pending |
| 6 | Full inventory/review closure, differential campaign and offline audit | Pending |

Commit each reviewed increment. Constructor and runtime-obligation statuses remain
separate; helper checks cannot establish source semantics. Unsupported, crashes,
timeouts and interrupted campaigns never count as validation passes.

## Assignments and interfaces

- Reviewer owns progress/inventory/contracts, independent witnesses and review gates.
- Runner owns source execution and storage/control. Next: exact ownership roots,
  temporary lifetimes and conditional COW, then embedded array references.
- Fresh signatures agent owns pending `17-signatures.watsup`/`signatures.py`,
  then class linking. Type helpers use explicit namespace/import/class/position/
  source contexts and ordered diagnostics; unresolved names remain explicit.
  Activation, autoload and call binding are separate machine obligations.
- Numeric helpers are pure; runner owns PHP values/effects. See NUMERICS.
  Storage uses cells, captured versus delayed operands and internal array IDs.
  Nested dimension descriptors preserve fetch timing; shallow graph copies are
  reviewed only for currently admitted reference-free entries. See DESIGN.
- Shared working tree: stage owned files only, never push. Baseline `082a3a2b`;
  the workspace gitlink was already modified. Commit each reviewed increment.

## Current evidence and decisions

- Inventory: 169 constructors and 304 runtime obligations, all pending/partial
  at full-core scope. `coverage/semantics/` retains bounded reports; git history
  records earlier milestone counts. Historical acceptance fingerprints are
  explicit; later implementation changes require fresh applicable evidence.
- Source machine through ordinary array unset `83c228cc`: independently repeated
  **363 exact source comparisons +23 negatives**, plus separate reviewer probes.
  Profile-name correction `94eb6cb3`: **8 selected comparisons +25 negatives**;
  `source-selected.json` preserves the preceding full `source.json` report.
  `_SESSION` is ordinary under this build; HTTP literal-read compiler diagnostics
  remain pending under `static.special-variable-diagnostics`.
- Numeric, integer, parsing, formatting, coercion and string helpers independently
  reviewed/repeated; see NUMERICS and their reports. Power `4e9256ba` passed
  **3,660 bit-exact cases**; exact source/FMA contractions and 657 ELF data words
  audited against glibc 2.39-0ubuntu8.8. See POWER-PROVENANCE.
- Local type helpers `531a8b40`/`9da9b012`: **694 retained comparisons**, expanded
  reviewer matrix **743**, 9 descriptors and 7 negatives. Separately classified:
  24 intended relative-static interpretations, 34 parser rejects and one known
  frontend compile restriction. This is helper evidence; declaration activation
  and reconciliation of direct-void frontend rejection remain pending.
- **62 independent oracle targets**, 15 integrated into the reviewed source
  harness. `conformance-oracle.json` alone never establishes semantic coverage.
- Delayed names, self-assignment capture, cyclic arrays and NaN sharing identity
  have retained discriminators. Operator compile lines differ from AST/LHS lines.
  Reference wrappers/temporary ownership must preserve these observations.
- Fixed environment and intrinsic scope remain in CORE. Weak/GC, closures,
  introspection, output buffers, ticks and assertions stay core; no unfinished
  family may be reclassified as an ordinary library.
- Intentional interpretation: namespace-relative `static` uses late-static
  semantics, avoiding the pinned compiler crash/accidental parent substitution.
  Exact observations and rationale are in DISCREPANCIES. Crash reproduction is
  not conformance; source activation requires its own intended-behavior witnesses.

## Next gates

Review exact array ownership/ref topology and local signature descriptors.
Phase1 remains partial: source power, remainder/shifts/bitwise/incdec/casts,
mixed comparisons, handlers and configurable precision need integration.
Control/calls/objects/dynamic sources/resumable execution/lifetime remain pending.

`python3 scripts/check-semantic-inventory.py --complete` rejects unfinished
entries; source/helper evidence and independent review remain separate.
Before the first family closes, strengthen this gate to check obligation-specific
case IDs/current report fingerprints and intentional-divergence source evidence.
Nine isolated evidence negatives reject source/binary/path drift and missing,
escaping or unproved evidence; `make test-semantics` includes them.
