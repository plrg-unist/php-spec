# Core semantics progress

Target: PHP 8.5.10 CLI NTS 64-bit; [plan](PLAN.md),
[contract](docs/semantics/CORE.md), [inventory](coverage/semantics/features.json).
Complete core remains the goal. Syntax coverage is not semantic coverage.

## Milestones

| Milestone | Deliverable | Current status |
| --- | --- | --- |
| 0a | Core/environment/observation contracts and inventory | Complete — contracts only |
| 0b | Checked AST runner and original-source differential harness | Complete — bounded bootstrap reviewed (`8b856a27`) |
| 1a | Pure integers/bytes and result typing | Partial — integer/bitwise/float-cast helpers reviewed; source integration pending |
| 1b | Pure binary64 and rounding | Partial — add/sub/mul/div helpers reviewed; source integration pending |
| 1c | Numeric text, conversions, formatting, power | Partial — text/formatting/context helpers reviewed; power pending |
| 2a | Slots, aliases, frames and access modes | Partial — scalar bindings/refs reviewed (`5a083605`); frames/global/property access pending |
| 2b | Arrays, strings, lvalues and sequencing | In progress — scalar source bridge review, then arrays and foreach |
| 3a | Control, exceptions, diagnostics and unwinding | Pending |
| 3b | Calls, closures, binding and independent static checks | Pending |
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
- Numeric owns pure `.watsup` primitives and helper tests. The implemented numeric
  domain is `NINT int | NFLOAT nat` (binary64 bits); add/sub/mul return numbers,
  division returns `NUM number | DIVZERO`. Runner owns the PHP value domain.
- Storage maps byte names to cells; operands distinguish captured values from
  delayed variable reads. Arrays will distinguish copied entries from aliases
  and retain append history. See `docs/semantics/DESIGN.md`.
- Shared working tree: stage owned files only, never push. Baseline `082a3a2b`;
  the workspace gitlink was already modified.

## Evidence and decisions

- Inventory: exact 169 constructors and 302 unique runtime obligations, all
  still pending/partial at full-core scope. Contracts began in `69868bac`.
- Independently reviewed/repeated helpers: numeric `4d343899` (1,976 differential
  +8 symbolic cases), integer `7d48a580` (1,025), numeric text `9cc4ecef` (350).
  Formatter `99ebf273` (8,826), context `33e503aa` (921) also independently
  repeated with stable fingerprints. Reports in `coverage/semantics/`.
- Reviewed source machine: bootstrap `8b856a27` (8 comparisons +7 negatives),
  scalar storage `5a083605` (53 comparisons +12 negatives). Stable fingerprints;
  current report `coverage/semantics/source.json`, raw observations in
  `coverage/results-semantic-source.jsonl`. Phase0 report is historical.
- Storage regressions preserve delayed dynamic names, reference rebinding,
  dynamic-write initialization, eliminated discarded CV reads and warning lines.
- 31 independent source targets in `tests/semantics/conformance` match the oracle;
  only two are currently integrated into semantic tests. Oracle-only evidence is
  `coverage/semantics/conformance-oracle.json`; it never implies implementation.
- Fixed profile includes `E_ALL=30719`, original identity and byte-exact channels.
  Weak/GC, closure/call introspection, output buffers and ticks stay core. Ordinary
  libraries, foreign resources and Reflection-created lazy objects are outside
  the explicit environment. Compiler-special assertions remain in scope.
- Power provenance pins glibc 2.39-0ubuntu8.8 FMA/AVX2, including actual compiler
  contractions and unchanged local source/license evidence. General power remains
  pending; see `docs/semantics/POWER-PROVENANCE.md`.
- No intentional engine disagreement.

Gate: `python3 scripts/check-semantic-inventory.py`; `--complete` rejects unfinished
entries and requires independent review plus source/helper evidence separately.
Next: review the numeric source bridge and byte-string helpers, then arrays;
keep frame, callback and lifecycle obligations visible throughout.
