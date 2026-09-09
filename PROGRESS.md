# Core semantics progress

Target: PHP 8.5.10 CLI NTS 64-bit; [plan](PLAN.md),
[contract](docs/semantics/CORE.md), [inventory](coverage/semantics/features.json).
Complete core remains the goal. Syntax coverage is not semantic coverage.

## Milestones

| Milestone | Deliverable | Current status |
| --- | --- | --- |
| 0a | Contracts and inventory | Complete — contracts only |
| 0b | Checked AST runner and original-source harness | Complete — bounded bootstrap |
| 1a–c | Integers, bytes, binary64, conversions and power | Partial — helpers and arithmetic/update source paths reviewed |
| 2a | Slots, aliases, frames and access modes | Partial — scalar bindings/references reviewed; frames and properties pending |
| 2b | Arrays, strings, lvalues and sequencing | Partial — reads/writes/references/updates and omissions reviewed; unpack/foreach pending |
| 3a | Control, exceptions, diagnostics and unwinding | Partial — conditionals/loops/jumps reviewed; exceptions pending |
| 3b | Calls, closures and independent static checks | Partial — type/signature/compiler helpers reviewed; activation pending |
| 4a | Class linking, inheritance, traits, visibility and clone | Partial — local headers/relations reviewed; linking pending |
| 4b | Properties, modern declarations and internal protocols | Pending |
| 5a | Dynamic sources, autoload and explicit services | Pending |
| 5b | Generators/Fibers, lifetime, collection and callbacks | Pending |
| 6 | Full inventory/review closure, differential campaign and offline audit | Pending |

## Ownership and handoffs

- `runtime3`: remaining ordinary operators/casts, then unpack/destructuring/foreach; accepted compound handoff `3b3a7cd6` preserves exact private draft hashes.
- `compiler4`: paired ordinary operator and destructuring compilation, then declarations/frames and class lookup.
- `compiler3`: independent review, discrepancy history, inventory and concise documentation.
- Stage owned files, commit reviewed increments, never push. Run evidence/inventory preflight after watched changes and before long campaigns.

[Runtime](docs/semantics/RUNTIME-SUCCESSOR-HANDOFF.md),
[compiler](docs/semantics/COMPILER-HANDOFF.md) and
[reviewer](docs/semantics/REVIEWER-HANDOFF.md) handoffs retain exact interfaces.

## Current accepted checkpoints

Nullable-array/context prerequisite code `9b82507a`, author reports `22b36687` and review `91f035e0`
([independent evidence](coverage/semantics/array-omission-review.json)) pass **262 exact
sources/lints**, 2,135 resumption assertions, 2,943 compiler lints and 106 metadata
profiles/1,751 checks on `1ff3da3b`. Independent gates add 176 current source
observations, 32 extra sources, 136 metadata boundaries, 24 fresh encoding/print
profiles and 277 preserved compound programs/5,393 assertions. All 41 publication
paths, 44 loaded modules and four tools are bound; two redundant EOF newlines are
the only explicit private-to-production byte adjustments.

Ordinary Array.items now shares nullable List.items domains, preserving indices
and trailing omissions. Visited holes fail using the previous original expression
line or active compiler context; skipped holes remain legal. Four narrow metadata
fields preserve first-hole, concat, nullary and clone reduction context. Complete
identical-AST/different-native-line witnesses justify the added fields. Synthetic
unqualified exit/die/clone calls use closing lines; qualified/relative calls retain
name lines. Five retired syntax exemptions now have literal regression checks.
Classconstant lookup remains explicitly pending where its value can affect branch
selection; replacing the wrong nonconstant result with Unsupported is not a pass.

This prerequisite **does not refresh the full source campaign**. The last complete
campaign remains compound code `63028b5a`, reports `76129823`, review `d61eccde`:
**2,639 exact sources +25 negatives** on historical `c394a6e7`. Its raw audit verifies
every ordered ID, original byte/hash and exact stdout/stderr/status, including all
retained wrapper/incdec/compound originals. Twelve compound forms preserve captured
locations, delayed reads, array union ownership, eager global `$this` and the split
between target opcode diagnostics and final compiler context. Original phase/line
failures and the ordinal-filename infrastructure correction remain documented.

Evidence preflight independently passes 15 identity, three path and 17 closure
negatives plus nine ignored-log changes. Helpers embed literal sources without new
archive dependencies. Inventory remains **169 constructors/306 runtime obligations**,
with 70 field domains. New prepass-only constructor entries are partial and do not
admit their ordinary execution. Only oracle identity closes. Governance `ffdc131d`
requires current original-source evidence and independent review; `--complete` must
reject unfinished or stale entries.

## Retained contracts

- Inc/dec `7d5718fb`/review `a3cee6bd` preserves RW access, copied results, callable opening-token context, prepass barriers and computed-root lines. Its 1,484-source acceptance remains historical evidence.
- Wrapper correction `84d70299`/review `24c681d7` distinguishes ordinary writable fetch from true reference acquisition. Singleton wrapper history creates no extra roots; COW/union can unwrap copies independently. Generic fetch/intermediate unset warnings differ from final dimension mutation. Source collection remains pending.
- Comparisons `0e065cc6` and truth `e7dac829`/`682bcba0` retain original phase, overflow, copying and grouping witnesses. Occurrences, ACCESS, FACTS, permanent POOLS and held operands remain distinct; only compiled reads consume pooled values.
- Destructuring prerequisites preserve unpack, original array kind and first-hole token line. Genuine-list `5c756e5e` admits skipped sources; 14 reached originals still need real execution. Callable-line `c6a7d67d` supports rejected call targets, not call execution.
- Numeric/static/linking handoffs retain helper-only activation limits. **146 independent oracle targets; 86 integrated**. Helper evidence closes no source family.

## Next gates and decisions

Runtime3's private ordinary operator/cast/concat gates pass 833 initial and 673
expanded source observations; its canonical helper embeds 1,506 admitted selections.
The 25 state programs pass 2,875 assertions, including five loops at every budget
0–100. Independent review adds 62 source controls for delayed/eager operands,
alias/cycle casts, compiler-warning priority and parser-literal versus computed
names. Frozen native archives contain 805 initial, 28 timing and 680 expanded
observations; seven request-environment cases remain explicitly Unsupported.
Computed `$this` write/unset and parser-concat `$GLOBALS` read/discard/cast/write/
unset require real environment semantics. Quiet `??=` remains separate. Final
combined publication and a single 4,407-source campaign are next; no draft report
is relabeled as a complete current source closure.

Shared cast helpers pass 155 native inputs/496 assertions; independent checks add
NaN diagnostic attribution and 62 alias/cycle/allocation/abrupt-state assertions.
Bitnot passes 31 author and 19 independent inputs. Ordinary cast execution is not
inferred from accepted CT folding. Required classconstant/named-class/magic-context
lookup remains assigned; arbitrary constant facts never imply parser designation.
Private unpack/list helpers have additional source/state/resumption probes, but
source compiler pairing and independent review remain necessary. New multiline
list/RHS originals preserve direct-CV versus computed-expression line and `$this`
distinctions for the next bounded activation.

Then complete unpack/destructuring keys/copies/references/errors and foreach cursor
ownership. Calls/frames, linking/objects, modern properties, exceptions, dynamic
sources, callbacks and resumable lifetime remain unfinished. The intrinsic versus
ordinary-library boundary cannot discharge unfinished core obligations.

[Discrepancies](docs/semantics/DISCREPANCIES.md) separate raw failures from resolutions.
Namespace-relative `static` remains the sole intentional divergence, with source
activation pending. The 30,980-record syntax audit is historical; full syntax and a
fresh offline rebuild remain mandatory. Unsupported, crashes, timeouts and
interrupted runs never pass. Close the project only after every core obligation.
