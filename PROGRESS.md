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
  read [ARRAY-HANDOFF](docs/semantics/ARRAY-HANDOFF.md). Next audit internal HELD
  roots before enabling pruning, conditional COW and source embedded references.
- Signatures agent owns class linking/variance after reviewed local class headers.
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
- Source machine `41e8fa2b`: independently repeated **371 exact source comparisons
  +25 negatives**; ordinary array writes/unset and profile-name fixes included.
  `_SESSION` is ordinary here; HTTP compiler diagnostics remain pending.
- Ownership `41e8fa2b`: **617 graph +15 machine/boundary helper cases**, 5,075
  assertions, independently repeated; 150 extra reviewer graph probes passed.
  Explicit allocated graphs preserve uncollected cycles; task captures move and
  clear scratch fields. Driver pruning, internal HELD roots, COW and source
  reference/GC integration remain pending.
- Numeric, integer, parsing, formatting, coercion and string helpers independently
  reviewed/repeated; see NUMERICS and their reports. Power `4e9256ba` passed
  **3,660 bit-exact cases**; exact source/FMA contractions and 657 ELF data words
  audited against glibc 2.39-0ubuntu8.8. See POWER-PROVENANCE.
- Local type helpers `531a8b40`/`9da9b012`: **694 retained comparisons**, expanded
  reviewer matrix **743**, 9 descriptors and 7 negatives. Separately classified:
  24 intended relative-static interpretations, 34 parser rejects and one known
  frontend compile restriction. This is helper evidence; declaration activation
  and reconciliation of direct-void frontend rejection remain pending.
- Local signatures `ac5bc703`: **357 checked helper/lint comparisons**, 28
  descriptors, 174 return-reference checks, 4 edited minimum-int descriptors and
  14 Unsupported checks; 2 frontend restrictions and 2 edited compiler checks
  remain separate. Expanded independent matrix: 458 comparisons. Review fixed
  global namespace-relative special defaults and checked deferred-default lines.
  No declaration activation, default materialization or call binding is claimed.
- Class headers `187b01f2`: **195 checked helper/lint comparisons**, 9 descriptors,
  10 Unsupported, plus 57 exact frontend restrictions and 57 separate edited
  compiler checks. Expanded independent matrix: 235 comparisons/13 descriptors.
  Bodies are retained syntax; source activation and class linking remain pending.
- **68 independent oracle targets**, 15 integrated into the reviewed source
  harness. `conformance-oracle.json` alone never establishes semantic coverage.
- Known admitted mismatch under immediate repair: `($x=&$a)+($a=2)` with `$a=1`
  gives PHP 4 versus spec 3. Reference-assignment results need owning reference
  operands. The 371-case selection does not cover this failing source.
- Delayed names, self-assignment capture, cyclic arrays and NaN sharing identity
  have retained discriminators. Operator compile lines differ from AST/LHS lines.
  Reference wrappers/temporary ownership must preserve these observations.
  New oracle witnesses establish literal-occurrence identity and uncollected-cycle
  reference ownership: explicit GC changes ordinary copied-array mutation (99
  before collection versus 19 after). Reachability-only owner counting is insufficient.
- Fixed environment and intrinsic scope remain in CORE. Weak/GC, closures,
  introspection, output buffers, ticks and assertions stay core; no unfinished
  family may be reclassified as an ordinary library.
- Intentional interpretation: namespace-relative `static` uses late-static
  semantics, avoiding the pinned compiler crash/accidental parent substitution.
  Exact observations and rationale are in DISCREPANCIES. Crash reproduction is
  not conformance; source activation requires its own intended-behavior witnesses.

## Next gates

Review the references runner’s scoped HELD/driver integration, then fix the
admitted reference-assignment-result mismatch before COW/embedded references.
Class linking/variance must follow pinned source predicates and phase ordering.
Phase1 remains partial: source power, remainder/shifts/bitwise/incdec/casts,
mixed comparisons, handlers and configurable precision need integration.
Control/calls/objects/dynamic sources/resumable execution/lifetime remain pending.

`python3 scripts/check-semantic-inventory.py --complete` rejects unfinished
entries; source/helper evidence and independent review remain separate.
Before the first family closes, strengthen this gate to check obligation-specific
case IDs/current report fingerprints and intentional-divergence source evidence.
Nine isolated evidence negatives reject source/binary/path drift and missing,
escaping or unproved evidence; `make test-semantics` includes them.
