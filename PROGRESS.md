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
| 2b | Arrays, strings, lvalues and sequencing | Partial — reads/writes/references/updates reviewed; omissions, unpack and foreach pending |
| 3a | Control, exceptions, diagnostics and unwinding | Partial — conditionals/loops/jumps reviewed; exceptions pending |
| 3b | Calls, closures and independent static checks | Partial — type/signature/compiler helpers reviewed; activation pending |
| 4a | Class linking, inheritance, traits, visibility and clone | Partial — local headers/relations reviewed; linking pending |
| 4b | Properties, modern declarations and internal protocols | Pending |
| 5a | Dynamic sources, autoload and explicit services | Pending |
| 5b | Generators/Fibers, lifetime, collection and callbacks | Pending |
| 6 | Full inventory/review closure, differential campaign and offline audit | Pending |

## Ownership and handoffs

- Runtime successor: remaining ordinary operators/casts, then unpack/destructuring/foreach; `runtime_next` leaves the accepted compound checkpoint and exact private draft hashes.
- `compiler4`: nullable ordinary-array frontend/schema and exact prepass traversal, then paired operator and declaration/frame compilation.
- `compiler3`: independent review, discrepancy history, inventory and concise documentation.
- Stage owned files, commit reviewed increments, never push. Run evidence/inventory preflight after watched changes and before long campaigns.

[Runtime](docs/semantics/RUNTIME-SUCCESSOR-HANDOFF.md),
[compiler](docs/semantics/COMPILER-HANDOFF.md) and
[reviewer](docs/semantics/REVIEWER-HANDOFF.md) handoffs retain exact interfaces.

## Latest accepted checkpoint

Compound code `63028b5a`, reports `76129823` and review `d61eccde`
([independent evidence](coverage/semantics/compound-review.json)) pass **2,639 exact
sources +25 outcome negatives** on `c394a6e7`. The raw audit checks every ordered
catalog ID, original byte string/hash, stdout/stderr/status and retained regression
binding. All previous 1,484 inc/dec checkpoint sources remain present unchanged;
older reports retain historical fingerprints.

All twelve compound assignments now use captured RW locations for the current
six values and direct/computed variable, dimension and append targets. Names/keys
are evaluated once; delayed CV reads, alias rebinding, array union ownership and
copied results preserve PHP ordering. Direct global `$this` uses eager FETCH_THIS;
computed-name rebinding has a distinct runtime protocol. No static compound-this
rejection is invented. Final DIM diagnostics use captured target opcode lines;
compiler descriptors retain their final context after RHS compilation.

Independent gates pass **277 source programs/5,393 assertions**, including three
loops at every budget 0–100, plus **324 compiler sources/156 access paths/six line
checks**. Canonical compound gates pass 951 runtime programs/13,454 assertions,
289 compiler lints/34 paths/24 emission observations/12 contexts. Broad compiler
validation passes 2,681 lints; inc/dec, writable-fetch, wrappers, origins, bridge
and ownership all refresh on the same closure.

Two real draft defects are resolved with unchanged evidence: 72 `$this` phase
originals and three actual runtime DIM-line failures with 72 compiler controls.
Every original occurs byte-for-byte in the full passing catalog. A separate harness
failure treated `/=` in logical IDs as a path: fixtures now use unique ordinal
filenames, with every source written before subprocess execution. Independent
preflight verifies 2,639 catalog IDs plus ten hostile IDs and preserves the exact
infrastructure traceback. No engine disagreement was introduced.

Evidence preflight independently passes 15 identity, three path and 17 closure
negatives plus nine ignored-log changes. New helpers embed source literals without
new archive dependencies. The inventory remains **169 constructors/306 runtime
obligations**; twelve compound constructors become partial. Only oracle identity
closes. Governance `ffdc131d` requires current original-source evidence and review;
`--complete` must reject unfinished or stale entries.

## Retained contracts

- Inc/dec `7d5718fb`/review `a3cee6bd` preserves RW access, copied results, callable opening-token context, prepass barriers and computed-root lines. Its 1,484-source acceptance remains historical evidence.
- Wrapper correction `84d70299`/review `24c681d7` distinguishes ordinary writable fetch from true reference acquisition. Singleton wrapper history creates no extra roots; COW/union can unwrap copies independently. Generic fetch/intermediate unset warnings differ from final dimension mutation. Source collection remains pending.
- Comparisons `0e065cc6` and truth `e7dac829`/`682bcba0` retain original phase, overflow, copying and grouping witnesses. Occurrences, ACCESS, FACTS, permanent POOLS and held operands remain distinct; only compiled reads consume pooled values.
- Destructuring prerequisites preserve unpack, original array kind and first-hole token line. Genuine-list `5c756e5e` admits skipped sources; 14 reached originals still need real execution. Callable-line `c6a7d67d` supports rejected call targets, not call execution.
- Numeric/static/linking handoffs retain helper-only activation limits. **146 independent oracle targets; 86 integrated**. Helper evidence closes no source family.

## Next gates and decisions

Nullable ordinary Array_.items uses the existing list(ArrayItem|null) domain,
keeping original indices and exact first-hole context; no ArrayHole node is needed.
Parser concat metadata records reduction lookahead lines, while pure parser-literal
classification remains separate from compiler constant facts. The frozen private
107-source snapshot passes author lint/runtime/resumption/metadata gates; independent
review repeats 68 revised originals and audits all 34 files. A further 15 prepass
constructor originals expose explicit Unsupported gaps; compiler4 is resolving exact
Zend barriers and coalesce/classconstant traversal in a distinct revision. Preserve
all originals and rebase generated-domain consumers over accepted compound code.

Shared cast helpers pass 155 native inputs/496 assertions; independent checks add
NaN diagnostic attribution and 62 alias/cycle/allocation/abrupt-state assertions.
Bitnot passes 31 author and 19 independent inputs. Ordinary operator/cast/concat
runtime task drafts have only elaborated: 805 native originals await paired source
execution. Cast CT eligibility differs from runtime conversion; parser designation
must never follow arbitrary constant-fact equality. Quiet `??=` and computed plain
write/reference/unset name protocols remain separate boundaries.

Then complete unpack/destructuring keys/copies/references/errors and foreach cursor
ownership. Calls/frames, linking/objects, modern properties, exceptions, dynamic
sources, callbacks and resumable lifetime remain unfinished. The intrinsic versus
ordinary-library boundary cannot discharge unfinished core obligations.

[Discrepancies](docs/semantics/DISCREPANCIES.md) separate raw failures from resolutions.
Namespace-relative `static` remains the sole intentional divergence, with source
activation pending. The 30,980-record syntax audit is historical; full syntax and a
fresh offline rebuild remain mandatory. Unsupported, crashes, timeouts and
interrupted runs never pass. Close the project only after every core obligation.
