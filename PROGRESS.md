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

- Runtime: compound operations and remaining numeric dispatch, then arrays/foreach.
- Compiler: nullable ordinary-array omission representation, then declarations/frames.
- Reviewer: independent gates, discrepancy history, inventory, concise docs and progress.
- Stage owned files, commit reviewed increments, never push. Save watched bytes and run evidence/inventory preflight before long campaigns.

[Runtime handoff](docs/semantics/RUNTIME-SUCCESSOR-HANDOFF.md),
[compiler handoff](docs/semantics/COMPILER-HANDOFF.md) and
[reviewer handoff](docs/semantics/REVIEWER-HANDOFF.md) retain interfaces and next gates.

## Latest accepted checkpoint

Inc/dec code `7d5718fb`, reports `5b24a5f8` and
[independent review](coverage/semantics/incdec-review.json) pass **1,484 exact
sources +25 outcome negatives** on `d399263a`. The raw audit verifies every
ordered catalog ID, original byte string/hash, stdout/stderr/status and retained
regression binding. This refresh includes the genuine-list and computed-write
prerequisites; earlier campaigns remain historical fingerprints.

Independent validation adds 339 source observations (331 distinct byte strings),
71 context replays/994 assertions and eight dense replays/4,152 assertions at every
budget 0–100. Actual replay-loaded semantic bytes are separately bound to identical
production files, preserving original fingerprints. Canonical helpers pass 154
runtime programs/2,226 assertions, 108 compiler lints/32 access paths/eight emission
lines/12 context checks, and broad compiler 1,526 lints/15 emission observations.
Origins 25/333, bridge 15/148, ownership 617+96/5,434 and prior wrapper helpers pass.

Four updates now use captured RW locations and copied pre/post results for the
current six values and variable/dimension/append lvalues. Direct global `$this`
fetch is eager; computed reads and updates follow their distinct name protocols.
Direct rebinding/final unset reject statically. Computed root diagnostics use the
stored root line; direct CV dimensions retain their containing opcode line.
All seven root-line originals, three prepass originals and eight callable-line
originals are unchanged and integrated. Compound operators and object contexts
are not inferred from this milestone.

Evidence/inventory preflight ran before long campaigns and independently passes
15 identity, three path and 17 closure negatives, plus nine ignored-log changes.
New helpers embed source literals; they consume no new archive dependencies.
The inventory has **169 constructors and 306 runtime obligations**. Four update
constructors become partial; only [oracle identity](coverage/semantics/oracle-pin-review.json)
closes. No constructor or semantic family closes. Governance `ffdc131d` requires
original-source evidence, independent review and current fingerprints; `--complete`
must reject unfinished or stale entries.

## Retained corrections and interfaces

- Wrapper history `3585707a` repaired five FETCH/UNSET differences but accidentally marked ordinary computed-name writes. Correction `84d70299`, reports `fa691044`, review `24c681d7` separates initialized writable fetch from actual reference acquisition. All seven callers were audited; all 28 retained originals (12 mismatches/16 controls) now agree. Independent correction gates add 12 source controls, 79 prior wrapper sources and 49 state checks. Current full validation refreshes its canonical cases.
- [Wrapper contract](docs/semantics/REFERENCE-WRAPPERS.md) preserves singleton history without extra roots. COW/union may unwrap copied aliases independently; generic FETCH/intermediate UNSET warnings differ from final dimension mutation. Source collection remains pending.
- [Comparison](coverage/semantics/comparison-review.json) `0e065cc6` retains overflow and phase originals; [truth](coverage/semantics/truth-review.json) `e7dac829`/`682bcba0` retains all 63 phase/copy/grouping witnesses. Ordinary ternary copies selected values; raw prepass redirects may preserve delayed operands.
- [Control](coverage/semantics/control-review.json) `d87f3f9f` covers conditionals, while/do/for and literal-depth jumps. Checked source occurrences, executable ACCESS, partial FACTS, permanent POOLS and held operands remain separate; actual compiled reads alone consume pooled values. Exceptions, foreach and unwinding remain open.
- Destructuring prerequisites preserve unpack (`d4706937`), original array kind (`09f33419`) and first-hole token line (`87341500`). Genuine-list conversion `5c756e5e`/review `861020db` admits 20 skipped sources, while 14 reached originals remain Unsupported. First-hole compiler consumption and ordinary Array_ omissions remain pending.
- Callable opening-token metadata `c6a7d67d`/review `1d32e9be` preserves eight old-AST witnesses, including identical trees with different native lines. Inc/dec now consumes it for rejected dynamic-call targets. Ordinary call execution remains pending.
- [Numeric](docs/semantics/NUMERICS.md), [static](docs/semantics/STATIC.md), [compiler](docs/semantics/SOURCE-COMPILER.md) and linking handoffs retain reviewed helpers and explicit activation limits. **146 independent oracle targets; 86 integrated**; helper-only evidence closes no source family.

## Next gates and decisions

Pair twelve compound assignments with checked PPRW/PFSTOP order, captured targets,
delayed CV RHS reads, array `+=` and exact diagnostics. The rebased private prototype
passes 81 author originals/1,204 assertions, with additional timing controls; it
still needs production admission. Independent review found an incorrect early
compound `$this` rejection and a delayed DIM diagnostic-line error; immutable
originals are linked in the discrepancy ledger. A corrected compiler guard passes
324 phase probes, and 133 independent runtime originals/3,377 state assertions
pass its bounded draft. DIM opcode-line correction and full gates remain pending. Remaining numeric/byte/power
operators, casts and literal-concat variable-name classification are separate
source work. Computed plain-write/reference/unset environment-name protocols remain
prior explicit boundaries. `??=` requires quiet reads and memoized writes.

Ordinary Array_ omissions should use nullable items and exact first-omission
context: Zend stores null entries and reports prior-element/compiler lines. No new
ArrayHole node is justified. Independently repeat the 16 fresh line originals,
then gate checked schema, deterministic consumer remapping, printer and exact
compiler visits together. Preserve skipped branches and original hole indices.

Then pair reached destructuring/unpack traversal with runtime keys, copies,
references and errors. Foreach requires persistent bucket/cursor identities and
mutation ownership. Calls/frames, linking/objects, modern properties, dynamic
sources, callbacks and resumable lifetime remain unfinished. The intrinsic versus
ordinary-library boundary in CORE cannot discharge unfinished core obligations.

[Discrepancies](docs/semantics/DISCREPANCIES.md) preserve raw failures separately
from resolutions. Namespace-relative `static` remains the sole intentional
divergence, with source activation evidence pending; no new divergence was selected.
The 30,980-record syntax audit is historical after metadata changes. Final complete
syntax validation and a fresh offline rebuild remain required; copied executables
alone establish no portability claim. Unsupported, crashes, timeouts and interrupted
runs never count as passes. Finish every core obligation before closing the project.
