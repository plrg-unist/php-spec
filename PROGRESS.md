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

- Runtime: inc/dec, compound operations and remaining numeric dispatch, then arrays/foreach.
- Compiler: update descriptors and ordinary-array omission phase repair, then declarations/frames.
- Reviewer: independent gates, discrepancy history, inventory, concise docs and progress.
- Stage owned files, commit reviewed increments, never push. Save watched bytes and run evidence/inventory preflight before long campaigns.

[Runtime handoff](docs/semantics/RUNTIME-SUCCESSOR-HANDOFF.md),
[compiler handoff](docs/semantics/COMPILER-HANDOFF.md) and
[reviewer handoff](docs/semantics/REVIEWER-HANDOFF.md) retain interfaces and next gates.

## Latest accepted checkpoints

Computed-write correction `84d70299`/reports `fa691044` fixes an admitted
reference-history regression. [Independent review](coverage/semantics/wrapper-dynamic-write-review.json)
resolves all 28 retained originals (12 mismatches/16 controls), adds 12 timing/COW
sources, and passes 79 prior wrapper sources, 49 state checks and ownership
617+96/5,434. Canonical 30-source/505-assertion and selected 30-source/25-negative
gates pass on `055e533c`; full source refresh shares the following inc/dec gate.

The inventory has **169 constructors and 306 runtime obligations**. Only
[oracle selection/identity](coverage/semantics/oracle-pin-review.json) closes;
no constructor or PHP semantic family closes. Closure governance `ffdc131d`
requires exact original-source/raw-byte bindings, independent review and current
fingerprints. `--complete` must reject unfinished or stale entries.

Historical reference-wrapper correction `3585707a` and reports `eebf79e9` passed
**1,163 exact sources +25 outcome negatives** on `1f71f10d`.
[Independent review](coverage/semantics/reference-wrapper-review.json) verifies
79 public sources, 72 replay programs/1,288 assertions and 45 additional state
checks. All eleven retained FETCH/final-write/UNSET originals remain unchanged
and integrated; five prior mismatches now agree. Singleton wrapper history adds
no roots, COW/union copies can unwrap independently, and intermediate FETCH/UNSET
warnings remain distinct from final dimension mutation. No divergence was added.

That historical closure includes origins, compiler bridge and ownership gates.
[Comparison review](coverage/semantics/comparison-review.json) retains `0e065cc6`:
38 independent sources, 34 compiler alternatives and six dense replays/4,974 checks.
Its overflow and phase originals remain unchanged and source-integrated.

First-hole metadata `87341500` is independently accepted in `79951ad4`:
31 author profiles/409 checks, 20 additional profiles/140 checks, and 12 exact
original line witnesses. Nested unpack (`d4706937`) and original array kind
(`09f33419`) remain reviewed prerequisites. All 16 genuine-list and six ordinary
array-hole [phase originals](coverage/semantics/frontend-phase-originals-review.json)
are independently repeated. Genuine-list conversion `5c756e5e` now passes 20 exact
skipped sources +25 negatives, 32 checked/printer profiles and independent review;
14 reached originals remain explicitly Unsupported. First-hole compiler consumption
and ordinary-array omission repair remain pending. Callable invocation metadata
`c6a7d67d` passes [independent review](coverage/semantics/callable-line-review.json):
eight old-AST originals, 35 canonical profiles/477 checks, 24 additional profiles
and 24 native error-line witnesses. Its semantic consumer remains a separate gate.

## Retained contracts

- [Truth](coverage/semantics/truth-review.json) `e7dac829`/`682bcba0` preserves all 63 phase/copy/grouping originals. Ordinary ternary copies selected values; raw prepass redirects can preserve delayed operands.
- [Control](coverage/semantics/control-review.json) `d87f3f9f` covers conditionals, while/do/for and literal-depth jumps, with 67 independent sources and dense resumption. Exceptions, switch/goto, foreach and lifecycle remain pending.
- [Read](coverage/semantics/dimension-read-review.json), [write](coverage/semantics/dimension-write-review.json) and [traversal retirement](coverage/semantics/traversal-temporary-review.json) retain scalar/array/string lvalues, delayed reads, captured ownership and reference/compiler errors. Production unchecked source traversal is retired.
- [Compiler](docs/semantics/SOURCE-COMPILER.md), [constant context](docs/semantics/CONSTANT-CONTEXT.md), [pools](docs/semantics/COMPILED-POOLS.md) and [namespace review](coverage/semantics/namespace-constants-review.json) distinguish structural origins, partial FACTS, ordinary values, executable ACCESS and redirects. Only actual compiled reads consume pooled values; distinct NaN occurrences retain distinct array identity.
- [Numeric](docs/semantics/NUMERICS.md), [static](docs/semantics/STATIC.md) and [linking handoff](docs/semantics/LINKING-HANDOFF.md) retain reviewed pure helpers; source contexts, declarations and frames remain partial.
- **146 independent oracle targets; 86 integrated**. Oracle-only and edited-helper evidence establishes no additional source runtime coverage.

## Next gates and decisions

Pair four inc/dec forms with compiler PPRW access, then compound lvalues and the
remaining numeric/string operations. The private update draft is not
admitted; independent probes retained two missing array-prepass barriers and a control.
The corrected private draft passes 140 author programs/2,030 assertions, including
top-level `$this` contexts; independent acceptance remains pending.
Preserve acquisition timing, copied pre/post results, error lines,
append legality and held locations. Coalescing assignment needs a separate quiet
read and memoized write path.

Genuine-list frontend conversion is reviewed as a compatible prerequisite; its
full source refresh shares the upcoming inc/dec gate. Preserve reached-target
errors as pending rather than counting Unsupported as agreement.
Ordinary Array_ omissions should use nullable items with required first-omission
context; the engine stores null holes and uses prior-element/compiler lines.
No ArrayHole constructor is justified by current evidence. Gate checked schema,
mechanical consumer remapping, printer and exact compiler visits together.

Then pair unpack/destructuring compile traversal with runtime copying/references,
keys and errors. Foreach requires persistent bucket/cursor identities and mutation
ownership. Calls, classes/objects, modern properties, dynamic sources, callbacks
and resumable lifetime remain open. CORE's intrinsic/environment boundary is fixed;
ordinary-library exclusions cannot discharge unfinished core obligations.

[Discrepancies](docs/semantics/DISCREPANCIES.md) retain raw failures and separate
resolutions. Namespace-relative `static` remains the sole intentional divergence,
with source activation evidence pending. Other observed irregularities follow the
pin, including numeric boundary scanning and singleton wrapper diagnostics.

The [30,980-record syntax audit](coverage/frontend-syntax-repair.json) is historical
after metadata changes: 30,671 pass, 254 parser rejections, 41 classified compile
phase differences, six redirects and eight non-source records. Final full syntax
validation and a fresh offline rebuild remain required. Copied executables alone
establish no portability claim.

Unsupported, crashes, timeouts and interrupted runs never count as passes.
Finish and independently review every core obligation before closing the project.
