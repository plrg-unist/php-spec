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

- Runtime successor: false-reference FETCH repair, then updates/compound operations and arrays/foreach.
- Compiler: remaining frontend provenance/phase repairs and update descriptors, then arrays/declarations/frames.
- Fresh reviewer: wrapper-state review first; independent gates, discrepancy history, inventory and progress.
- Shared tree: stage owned files, commit reviewed increments, never push. Coordinate final watched freezes.

[Runtime handoff](docs/semantics/RUNTIME-SUCCESSOR-HANDOFF.md),
[compiler handoff](docs/semantics/COMPILER-HANDOFF.md) and
[reviewer handoff](docs/semantics/REVIEWER-HANDOFF.md) record accepted contracts,
remaining drafts, commands and risks.

## Latest accepted checkpoints

The inventory has **169 constructors and 306 runtime obligations**. Only
[oracle selection/identity](coverage/semantics/oracle-pin-review.json) closes;
no constructor or PHP semantic family closes. Closure governance `ffdc131d`
requires exact original-source/raw-byte bindings, independent review and current
fingerprints. `--complete` must reject unfinished or stale entries.

Comparison implementation `0e065cc6` and reports `c94459fd` pass
**1,142 exact sources +25 outcome negatives** on `ba6075cd`. The
[independent review](coverage/semantics/comparison-review.json) adds 38 sources,
34 compiler alternatives plus 24 access checks, and six dense replay programs
with 4,974 assertions. A separate 83-pair/166-check string-order helper gate is
helper evidence only. All four retained overflow and 48 phase originals are
unchanged and integrated; both draft overflow differences now agree.

Canonical comparison 232 states/3,388 assertions, compiler 1,184 lint +15 emission
observations, comparison compiler 48/8/24, origins 25/333, runtime bridge 15/148
and ownership 617+96/5,434 pass the final closure. Strict result-type sources,
recursive errors, delayed greater operands, pool identity and resumption were
independently checked. Evidence preflight passes 15 identity, three path and 17
closure negatives. A required isolated-fixture repair invalidated the provisional
campaign; corrected gates were repeated, preserving earlier evidence as historical.

[Truth review](coverage/semantics/truth-review.json) `e7dac829`/`682bcba0` retains
all 63 original phase/copy/grouping cases and compiler redirect/archive integrity.
Frontend prerequisites preserve nested unpack flags (`d4706937`,
[review](coverage/semantics/destructuring-unpack-review.json)) and original array
syntax kind (`09f33419`, [review](coverage/semantics/destructuring-array-kind-review.json)).
First-hole comma metadata `87341500` is independently reviewed (31 author profiles/409
checks plus 20 independent profiles/140 checks); compiler consumption and array-omission
phase gaps remain pending. Their
[original loss witnesses](coverage/semantics/destructuring-metadata-disagreement.json)
and [expanded author captures](coverage/semantics/frontend-phase-originals-review.json)
remain alongside partial resolutions; all expanded 22 captures are independently repeated.

## Retained evidence and contracts

- [Control review](coverage/semantics/control-review.json): source `d87f3f9f`
  covers if/elseif/else, while/do/for and literal-depth jumps; 67 independent
  sources, compiler metadata/order controls and dense nested/COW resumption pass.
  Exceptions, switch/goto, foreach and lifecycle remain pending.
- [Read](coverage/semantics/dimension-read-review.json),
  [write](coverage/semantics/dimension-write-review.json) and
  [traversal retirement](coverage/semantics/traversal-temporary-review.json)
  evidence retain scalar/array/string lvalues, captured ownership, delayed reads,
  reference errors and temporary-target compiler errors. Production unchecked
  source traversal/classifiers are retired; only test fixtures retain a wrapper.
- [Compiler](docs/semantics/SOURCE-COMPILER.md),
  [constant context](docs/semantics/CONSTANT-CONTEXT.md),
  [pools](docs/semantics/COMPILED-POOLS.md) and
  [namespace review](coverage/semantics/namespace-constants-review.json) retain
  ordered compilation, structural origins, effective lines and reusable constant
  occurrences. FACTS, ordinary code-generation values and executable ACCESS roles
  remain distinct. Only actual compiled reads consume pooled values/redirects.
- [Numeric](docs/semantics/NUMERICS.md), [static](docs/semantics/STATIC.md) and
  [linking handoff](docs/semantics/LINKING-HANDOFF.md) retain earlier helper
  contracts; source context and declaration/frame integration remain partial.
- **146 independent oracle targets; 86 integrated**. Oracle-only and edited-helper
  evidence establish no additional source runtime coverage.

## Next gates and decisions

Repair the [open false-reference FETCH discrepancy](coverage/semantics/false-reference-fetch-review.json)
before update operators: three independent source mismatches and four controls
persist on the final comparison closure. Singleton unset retains observable
reference-wrapper history; generic dimension FETCH and final ASSIGN_DIM warn
differently. Runtime's proposed marker state remains under review. Independent scratch gates pass
72 expanded sources/1,288 assertions, alongside author source and graph gates.
[Four nested-UNSET originals](coverage/semantics/false-reference-unset-review.json)
are independently confirmed: two admitted mismatches and two controls. Production
publication and the full stable source gate remain required.
The current admitted runtime is not globally clean; no new divergence is selected.

Complete remaining destructuring provenance prerequisites, then pair compiler
and runtime unpack/destructuring. Foreach needs persistent bucket/cursor and
ownership rules. Compound lvalues, remaining numeric operators/casts, calls,
classes/objects, dynamic sources, callbacks and resumable lifetime remain open.
CORE's environment/intrinsic boundary is unchanged; ordinary-library exclusions
cannot discharge core obligations.

Preserve all retained read/prepass, write/error, phase/copy and emission-line
witnesses when their branches activate. Ordinary ternary copies selected values;
raw prepass redirects preserve delayed operands. Uncollected cycles retain
observable owners. Constant occurrences reuse installed values; distinct NaN
arrays retain distinct identity. Source collection and repeated function
execution remain pending.

[Discrepancies](docs/semantics/DISCREPANCIES.md) preserve raw failures and later
resolutions. Namespace-relative `static` remains the sole intentional divergence,
with source activation proof pending; other observed irregularities follow the
pin. The qualified import-prefix discrepancy is resolved by `d5d28dc6`.

The [30,980-record full syntax audit](coverage/frontend-syntax-repair.json) is
historical after metadata changes: 30,671 pass, 254 parser rejections, 41 classified
compile-phase differences, six redirects and eight non-source records. Copied
executables establish no new portability claim. Final full syntax validation and
fresh offline rebuild remain required.

Unsupported, crashes, timeouts and interrupted runs never count as passes.
Run evidence/inventory preflight before long campaigns whenever catalogs, archive
inputs or harnesses change; finish every core
obligation and independently review full scope before closing the project.
