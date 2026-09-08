# Core semantics progress

Target: PHP 8.5.10 CLI NTS 64-bit; [plan](PLAN.md),
[contract](docs/semantics/CORE.md), [feature inventory](coverage/semantics/features.json).
Complete core remains the goal. Existing syntax validation is not semantic evidence.

## Milestones

| Milestone | Deliverable | Status / owner |
| --- | --- | --- |
| 0a | Core/environment/observation contracts; all constructors/runtime obligations | Complete — reviewer (contracts only) |
| 0b | Checked AST runner, explicit outcomes, original-source differential harness | In progress — runner |
| 1a | Pure integers/bytes and result typing | In progress — numeric |
| 1b | Pure binary64 codec, rounding, operations and special cases | In progress — numeric |
| 1c | Numeric text, conversions, formatting, power | Pending |
| 2a | Slots, aliases, frames and access modes | Pending |
| 2b | Arrays, strings, lvalues and expression sequencing | Pending |
| 3a | Control, exceptions, diagnostics and unwinding | Pending |
| 3b | Calls, closures, binding and independent static checks | Pending |
| 4a | Class linking, inheritance, traits, visibility and clone | Pending |
| 4b | Properties, modern declarations and internal protocols | Pending |
| 5a | Checked dynamic sources, autoload and explicit services | Pending |
| 5b | Generators/Fibers, lifetime, collection and callbacks | Pending |
| 6 | Full inventory/review closure, differential campaign and offline audit | Pending |

Each milestone may have several small commits; reviewers require fixes before
recording acceptance. Runtime obligations and constructor status are independent.
Helper tests do not establish source-level semantics. Unsupported/timeouts/crashes
are never successful validation, and incomplete families stay visible.

## Active assignments and interfaces

- Reviewer owns this file, `features.json`, `CORE.md`, README/PLAN status links;
  independent review follows each runner/numeric increment.
- Runner owns checked execution integration and semantic source testing.
- Numeric owns pure `.watsup` primitives. Proposed shared numeric domain is
  `NINT int | NFLOAT nat` (binary64 bits); add/sub/mul return numbers and
  division returns `NUM number | DIVZERO`. Runner owns the PHP value domain.
- Agents share a working tree; stage only owned changes, never push. Baseline
  project commit is `082a3a2b`; workspace gitlink was already modified.

## Evidence and decisions

- Contracts/inventory commit: `69868bac`. Plan and all three skills read;
  required syntax/dependency docs reviewed.
- Initial inventory enumerates all 169 constructors and 297 runtime obligations;
  all remain pending until implementations and evidence exist.
- Baseline profile fixes precision, diagnostics, optimizer/JIT, locale/timezone;
  original source identity is observable. Contracts require byte-exact comparison.
- Weak/GC, closure binding, call introspection, output-buffer and tick controls
  remain core obligations. Reflection-created lazy objects and foreign resources
  are explicitly inadmissible environment values; ordinary libraries are excluded.
- Inventory check: exact schema membership for 169 constructors; 297 unique
  runtime obligation IDs with valid constructor references. Local oracle probe
  confirms 8.5.10 CLI, 8-byte integers, NTS and `E_ALL=30719`.
- No semantic validation has completed. No intentional engine disagreement.

Inventory gate: `python3 scripts/check-semantic-inventory.py`; `--complete` also
rejects every unfinished entry and requires source/helper evidence separately.
The initial completion gate correctly rejects all 466 pending entries.

Next: review executable runner and numeric slices,
then update statuses from actual source/helper evidence without narrowing scope.
