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
| 2b | Arrays, strings, lvalues and sequencing | Partial — ordinary literals/reads reviewed; writes/COW/references/foreach pending |
| 3a | Control, exceptions, diagnostics and unwinding | Pending |
| 3b | Calls, closures, binding and independent static checks | In progress — static local types under review; calls/activation pending |
| 4a | Class linking, inheritance, traits, visibility and clone | Pending |
| 4b | Properties, modern declarations and internal protocols | Pending |
| 5a | Checked dynamic sources, autoload and explicit services | Pending |
| 5b | Generators/Fibers, lifetime, collection and callbacks | Pending |
| 6 | Full inventory/review closure, differential campaign and offline audit | Pending |

Commit each reviewed increment. Constructor and runtime-obligation statuses remain
separate; helper checks cannot establish source semantics. Unsupported, crashes,
timeouts and interrupted campaigns never count as validation passes.

## Assignments and interfaces

- Reviewer owns this file, inventory, CORE, README/PLAN links and independent
  conformance witnesses; reviews each bounded implementation increment.
- Runner owns checked execution, storage/control/arrays and source testing.
- Pure numeric domain: `NINT int | NFLOAT nat` (binary64 bits); add/sub/mul
  return numbers, division returns `NUM number | DIVZERO`, power returns a
  number plus a pending notice. Runner owns the PHP value domain and effects.
- Static agent owns separate descriptor/context/result types: checked
  type AST plus namespace/import/class/position/source context to normalized
  types and ordered compile diagnostics. Keep unresolved names explicit; no
  autoload, declaration hoisting, pstate edits or bootstrap pcheck dependency.
  Start local type legality, then signature descriptors; see NUMERICS and CORE.
- Storage maps byte names to cells; operands distinguish captured values from
  delayed variable reads. Arrays retain ordered entries/history and internal IDs;
  recursive dimension descriptors defer fetches through key effects. Shared-ID
  identity shortcuts are observable with NaN, without PHP object identity.
  Writes/COW and embedded reference topology are next; see DESIGN.
- Shared working tree: stage owned files only, never push. Baseline `082a3a2b`;
  the workspace gitlink was already modified.

## Evidence and decisions

- Inventory: exact 169 constructors and 303 unique runtime obligations, all
  still pending/partial at full-core scope. Contracts began in `69868bac`.
- Independently reviewed/repeated helpers: numeric `4d343899` (1,976 differential
  +8 symbolic cases), integer `7d48a580` (1,025), numeric text `9cc4ecef` (350).
  Formatter `99ebf273` (8,826), context `33e503aa` (921) also independently
  repeated with stable fingerprints; string operators `81f151d7` (1,400).
  Reports in `coverage/semantics/`.
- Reviewed source machine: bootstrap `8b856a27` (8 comparisons +7 negatives),
  scalar storage `5a083605` (53 comparisons +12 negatives), numeric bridge
  `e3fbd6e8` (157 comparisons +16 negatives), ordinary array reads `eb48f793`
  (251 comparisons +22 negatives). Stable acceptance fingerprints;
  current report `coverage/semantics/source.json`, raw observations in
  `coverage/results-semantic-source.jsonl`. Phase0 report is historical.
- Storage regressions preserve delayed dynamic names, reference rebinding,
  dynamic-write initialization, eliminated discarded CV reads and warning lines.
  Operator diagnostics use post-child compile lines, distinct from AST/LHS lines.
- 57 independent source targets in `tests/semantics/conformance` match the oracle;
  only three are currently integrated into semantic tests. Oracle-only evidence is
  `coverage/semantics/conformance-oracle.json`; it never implies implementation.
- Fixed profile includes `E_ALL=30719`, original identity and byte-exact channels.
  Weak/GC, closure/call introspection, output buffers and ticks stay core. Ordinary
  libraries, foreign resources and Reflection-created lazy objects are outside
  the explicit environment. Compiler-special assertions remain in scope.
- Power provenance pins glibc 2.39-0ubuntu8.8 FMA/AVX2, including actual compiler
  contractions and unchanged local source/license evidence. General helper
  `4e9256ba` passed 3,660 independent bit-exact cases; prep `54e90ae2` (600+1),
  FMA `57ac6be7` (7 identities), data `ac315d39` (657 ELF words, `b73632b8`).
  See `docs/semantics/POWER-PROVENANCE.md`.
- Intentional interpretation: namespace-relative `static` declaration types use
  late-static semantics. The pinned engine crashes without a parent and wrongly
  substitutes the parent otherwise; exact observations and rationale are in
  `docs/semantics/DISCREPANCIES.md`. Crash reproduction is not conformance.

Gate: `python3 scripts/check-semantic-inventory.py`; `--complete` rejects unfinished
entries and requires independent review plus source/helper evidence separately.
Nine isolated evidence negatives reject source/binary/path drift and missing,
escaping or unproved evidence; `make test-semantics` includes them.
Next: review writable array locations/self-assignment, then COW/reference
topology; finish local type gate after the explicit relative-static correction. The initial
686-case helper repeat passed exact diagnostics and stable closure; source declaration
activation is still pending. Phase1 remains partial: source power,
remainder/shifts/bitwise/incdec/casts, mixed comparisons, handlers and configurable
precision still need integration and evidence. Frames/lifecycle remain pending.
