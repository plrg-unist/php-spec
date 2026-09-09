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

- Runtime successor: comparisons, then compound/numeric operations and arrays/foreach.
- Compiler: unpack/destructuring preservation and descriptors, then declarations/defaults/frames.
- Reviewer: independent gates, discrepancy history, inventory, progress and closure evidence.
- Shared tree: stage owned files, commit reviewed increments, never push. Coordinate final watched freezes.

[Runtime handoff](docs/semantics/RUNTIME-SUCCESSOR-HANDOFF.md) `6873f110` records
accepted contracts, comparison drafts and a retained scanner-overflow defect.
[Reviewer handoff](docs/semantics/REVIEWER-HANDOFF.md) records commands and risks.

## Latest accepted checkpoints

The inventory has **169 constructors and 306 runtime obligations**. Only
[oracle selection/identity](coverage/semantics/oracle-pin-review.json) closes;
no constructor or PHP semantic family closes. Closure governance `ffdc131d`
requires exact original-source/raw-byte bindings, independent review and current
fingerprints. `--complete` must reject unfinished or stale entries.

Source truth/logical operators and full/shorthand ternary `e7dac829`, independently
reviewed in `682bcba0`, passed **854 exact sources +25 outcome negatives** on
`10a40a12`. All 63 archived phase/copy/grouping originals are integrated. Review
adds 44 exact sources, 44 alternate compiler cases, five redirect/access and three
grouping checks; dense replay adds 3,316 assertions over 163 budgets for each of
four programs. [Truth evidence](coverage/semantics/truth-review.json) also binds
the compiler's consumed oracle archive and its mutation-rejection test.

At that source checkpoint, canonical truth71/1,344, compiler896 lint +15 emission
observations, truth compiler79/3/3, constant42/5, origins25/333, runtime bridge15/148
and ownership617+96/5,434 passed. Descriptor roles and edited metadata remain
separate from original-source execution evidence.

Frontend prerequisite `d4706937` subsequently preserves nested destructuring
unpack flags. [Review](coverage/semantics/destructuring-unpack-review.json) passes
16 author profiles/96 checks, ten independent profiles/80 checks, bounded syntax,
inventory and exact distribution patch reconstruction on `108f3eda`. This is a
new watched closure, with no refreshed full source campaign claimed. Original
long-array syntax kind and first-hole comma context remain pending; all 28
[original loss witnesses](coverage/semantics/destructuring-metadata-disagreement.json)
are preserved beside their partial resolution.

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

Finish the comparison draft's two retained integer-prefix overflow disagreements
before admission. A later exponent can rescale the float into range while the
scanner's earlier overflow flag still changes smart string comparison. Preserve
original left-to-right operand evaluation for greater comparisons, NaN/array
non-antisymmetry and recursion/ownership behavior. No intentional divergence is
selected for these draft defects.

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
Run evidence-integrity negatives with inventory checks; finish every core
obligation and independently review full scope before closing the project.
