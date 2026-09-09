# Core semantics progress

Target: PHP 8.5.10 CLI NTS 64-bit; [plan](PLAN.md),
[contract](docs/semantics/CORE.md), [inventory](coverage/semantics/features.json).
Complete core remains the goal. Syntax coverage is not semantic coverage.

## Milestones

| Milestone | Deliverable | Current status |
| --- | --- | --- |
| 0a–b | Contracts, inventory, checked runner and source harness | Complete — bounded bootstrap |
| 1a–c | Integers, bytes, binary64, conversions and power | Partial — scalar/array operator and cast source paths reviewed |
| 2a | Slots, aliases, frames and access modes | Partial — bindings/references reviewed; quiet access and frames pending |
| 2b | Arrays, strings, lvalues and sequencing | Partial — array unpack/list/foreach reviewed; quiet access and object protocols pending |
| 3a | Control, exceptions, diagnostics and unwinding | Partial — array loops/jumps reviewed; return/frames and exceptions pending |
| 3b | Calls, closures and independent static checks | Partial — static helpers reviewed; source activation pending |
| 4a–b | Linking, objects, traits, properties and internal protocols | Partial — local headers/relations reviewed; execution pending |
| 5a | Dynamic sources, autoload and explicit services | Pending |
| 5b | Generators/Fibers, lifetime, collection and callbacks | Pending |
| 6 | Full inventory/review closure, differential campaign and offline audit | Pending |

## Ownership and handoffs

- `runtime4`: storage/source integration, currently quiet access/CV/request-environment rules.
- `compiler4`: paired compiler/frontend work, then declarations/frames and class lookup.
- `review6`: independent evidence, inventory, phase ledger and concise status/docs.
- Root orchestrates; stage owned files, commit reviewed increments, never push.
  Use canonical-root Dune builds and coordinate shared binaries.

[Runtime](docs/semantics/RUNTIME-SUCCESSOR-HANDOFF.md),
[compiler](docs/semantics/COMPILER-HANDOFF.md) and
[reviewer](docs/semantics/REVIEWER-HANDOFF.md) handoffs retain interfaces and history.

## Latest accepted checkpoints

Array foreach code **`1f0e8810`**, author evidence **`7cdd513c`** has
[bounded independent acceptance](coverage/semantics/foreach-runtime-review.json):
155 exact sources, nine author state programs/6,498 assertions and eight independent
programs/3,096 assertions. Independent source replay covers 143 originals; the 12
added prerequisite originals also agree. The catalogue-only bridge preserves all
selected state sources, fixtures and executable inputs. Public tagged cursors,
reference ownership, copy history and cleanup pass; four original defect classes
remain preserved, including a stale ORIGIN invisible in final output comparisons.
The fresh **4,997-source +24-negative campaign is running**, not yet accepted.
Objects/Traversable, frames/return and two compiler contexts remain unfinished.

Foreach syntax/key-precheck code **`75672577`** preserves reference/list key
designations and retires exactly three historical parser exceptions. The frozen
private and canonical inputs match **`ac2aaca6`** (815 inputs): 17 exact source
static errors +24 outcome negatives, 66 parser profiles, 18 typed/printer checks,
26 compiler metadata controls and the 4,884-source compiler gate pass.
[Independent review](coverage/semantics/foreach-publication-review.json) reproduces
33 original observations and verifies all three retirements. At that checkpoint normal foreach
compilation remained pending. All 12 original Unsupported controls are now retained
unchanged in the later 155-source runtime catalogue.

Destructuring/effect/coalesce code **`77f8d3c0`**, compiler reports **`c2893aea`**
and runtime reports **`54bda2fa`** share **`f1699a75`** (812 inputs).
**283 selected sources +24 outcome negatives** pass: 263 additions and 20 retained
cases. Seven state programs/3,633 assertions, 23 mechanism checks, 328 retained
cross-family sources, 18 context checks and all five compiler gates pass, including
4,867 source lints and 108 focused list lints/32 metadata controls.
[Independent acceptance](coverage/semantics/destructuring-review.json) verifies
exact raw/archive membership, 44 earlier and 16 additional source controls,
12 dense programs/6,192 assertions and the four effect-marker consumers.
[Contract](docs/semantics/DESTRUCTURING.md) records original-occurrence effects,
fetch/store order, aliases and the restricted coalesce scope.

Array-unpack code **`4ca826d2`**, evidence **`7ac2519f`** and review **`ceedbed3`**
previously passed 155 exact sources +24 negatives, 31 state programs/2,454 assertions,
42 compiler lints/10 controls and eight independent source/state programs/1,368
assertions. Its [review](coverage/semantics/array-unpack-review.json) preserves
154 original memberships and the retired empty-spread Unsupported control.
Traversable objects/callbacks and argument unpacking remain unfinished.

The last full source campaign is historical: ordinary code **`dba21cee`** and
review **`2ab579eb`** passed **4,407 exact sources +25 negatives** on `a8f6aa0c`.
Its [raw audit](coverage/semantics/ordinary-campaign-audit.json) binds every ordered
source/outcome, 16 archive groups and the 13 reports current at that checkpoint.
Earlier nullable/context `9b82507a`, compound `63028b5a`, incdec `7d5718fb` and
wrapper `84d70299` contracts and original failures remain linked in those reviews.

Inventory remains **169 constructors/306 runtime obligations**, with 70 field
domains. Only oracle identity closes. Helper tests, compiler prepass traversal and
syntax acceptance do not close ordinary source-execution families.

## Next bounded work

Finish the current container campaign raw audit. Array iteration now retains
persistent insertion occurrences, per-iterator saved copy positions and explicit
ownership/unwinding. [Contract and independent review](docs/semantics/FOREACH-REVIEW.md)
retain source rebinding, table replacement, copy selection and abrupt-exit originals.

Complete request environment, named/class/magic lookup, quiet access and
coalescing assignments before broader calls/frames, declarations, linked objects,
exceptions, dynamic sources, resumable services, lifetime and core intrinsics.
One header diagnostic case, five quiet-coalescing cases and seven ordinary
request-environment cases remain explicit Unsupported work; none count as source
agreements. [Quiet/CV design review](docs/semantics/QUIET-CV-REVIEW.md) and 28 native
originals distinguish delayed CV reads, temporary reuse and header compiler state.
Ordinary-library exclusions cannot discharge required core behavior.

Raw protection **`de04828e`** creates exclusive per-run files; its
[independent review](coverage/semantics/raw-output-review.json) verifies repeated
runs preserve historical bytes. List/compiler failures, the fourth consumer's
partial helper and twelve reused private source filenames are preserved with
separate classifications in the independent integration/mechanism reports.

## Validation cadence and closure

Each coherent increment needs exact source/native originals, focused compiler
phase/line checks, appropriate state/ownership/resumption gates and independent
review. Run evidence/inventory preflight after watched changes, before long runs.
Commit compatible prerequisites separately and dependent source rules atomically.

Run full current source campaigns at integration checkpoints: unpack/list/foreach;
calls/declarations/frames; linked objects/properties; exceptions/dynamic/resumable
services. Unresolved shared numeric/compiler/ownership risk can require an earlier
broad run. Changed inputs leave previous full reports explicitly historical.

[Discrepancies](docs/semantics/DISCREPANCIES.md) distinguish engine behavior from
specification defects. Namespace-relative `static` remains the sole intentional
divergence, with source activation pending. The 30,980-record syntax audit is
historical. Final full syntax validation, a fresh offline rebuild, current source
closure and every core obligation remain mandatory. Unsupported, tool failures,
timeouts and interrupted runs never pass. Final design/departure reporting waits
until the entire requested goal is complete.
