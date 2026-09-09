# Core semantics progress

Target: PHP 8.5.10 CLI NTS 64-bit; [plan](PLAN.md),
[contract](docs/semantics/CORE.md), [inventory](coverage/semantics/features.json).
Complete core remains the goal. Syntax coverage is not semantic coverage.

## Milestones

| Milestone | Deliverable | Current status |
| --- | --- | --- |
| 0a–b | Contracts, inventory, checked runner and source harness | Complete — bounded bootstrap |
| 1a–c | Integers, bytes, binary64, conversions and power | Partial — scalar/array operator and cast source paths reviewed |
| 2a | Slots, aliases, frames and access modes | Partial — bindings/references reviewed; quiet variable/DIM access reviewed; frames pending |
| 2b | Arrays, strings, lvalues and sequencing | Partial — array unpack/list/foreach reviewed; quiet access and object protocols pending |
| 3a | Control, exceptions, diagnostics and unwinding | Partial — array loops/jumps reviewed; return/frames and exceptions pending |
| 3b | Calls, closures and independent static checks | Partial — static helpers reviewed; source activation pending |
| 4a–b | Linking, objects, traits, properties and internal protocols | Partial — local headers/relations reviewed; execution pending |
| 5a | Dynamic sources, autoload and explicit services | Pending |
| 5b | Generators/Fibers, lifetime, collection and callbacks | Pending |
| 6 | Full inventory/review closure, differential campaign and offline audit | Pending |

## Ownership and handoffs

- `runtime5`: storage/source integration, currently quiet access/CV/request-environment rules.
- `compiler4`: paired compiler/frontend work, then declarations/frames and class lookup.
- `review7`: independent evidence, inventory, phase ledger and concise status/docs.
- Root orchestrates; stage owned files, commit reviewed increments, never push.
  Use canonical-root Dune builds and coordinate shared binaries.

[Runtime](docs/semantics/RUNTIME-SUCCESSOR-HANDOFF.md),
[compiler](docs/semantics/COMPILER-HANDOFF.md) and
[reviewer](docs/semantics/REVIEWER-HANDOFF.md) handoffs retain interfaces and history.

## Latest accepted checkpoints

The historical full container checkpoint passed **4,997 exact sources +24 outcome controls**
on **`a0e3709a`** (819 public inputs), author evidence **`d71d4107`**.
[Independent audit](coverage/semantics/container-campaign-audit.json) verifies every
ordered source/outcome and actual native/semantic subprocess pair, 26 source archive
groups, two separately scoped compiler archives and all 4,407 historical sources.
The exclusive raw file starts **`f0fc89de`**; [stable source report](coverage/semantics/container-source.json)
retains this checkpoint when later selections run. Its sixteen required core controls and four parser controls remain separate in that
immutable report. Quiet publication below retires four of those core controls;
twelve remain. No full-core or final-syntax claim follows.

Variable/DIM `isset` and `empty` code **`701e39fa`**, author evidence
**`65cefcc1`** and compiler evidence **`72c30740`** are accepted by
[independent review](coverage/semantics/isset-empty-review.json):232 exact sources,
22 separate controls, author9 state programs/4,230 assertions and independent7/
2,655. Twelve fresh canonical CLI probes and the exact frozen831-to-canonical835
bridge pass. Four GLOBALS outcomes remain Unsupported. Ordered CV descriptors and
GLOBALS compiler prerequisites are reviewed; request bootstrap and snapshots remain
pending. Current835/`afbaa198` supersedes earlier checkpoint identities.
[Contract](docs/semantics/ISSET-EMPTY-REVIEW.md) records terminal string behavior,
quiet ancestors, effects, static rejection and cleanup. The full quiet/CV campaign
is still due after request/GLOBALS integration.

Request fixture transport **`be12200b`** and evidence **`add0e4c1`** are
[independently reviewed](coverage/semantics/request-provider-independent-review.json).
It supplies explicit native clock/environment facts; PHP bootstrap/source semantics
remain pending. Both fresh copied-source builds passed under separate network
namespaces with identical provider bytes. Its checkpoint has 830 inputs/`96c18e4d`;
prior 826 source reports retain their historical identity. Final whole-project
offline validation remains required.

Variable/DIM coalescing assignment code **`f073c750`**, runtime evidence
**`784492ab`** and compiler evidence **`012cd357`** are accepted by
[independent review](coverage/semantics/coalesce-assignment-review.json):137 exact
sources +18 controls, fresh author 8 state programs/3,760 assertions, independent 7/
3,024 and nine edited-descriptor controls/74. Eighteen fresh canonical CLI cases
pass; the GLOBALS original remains Unsupported. Canonical 826/`cc1d3e5e` exactly
retains guarded 834 runtime dependencies. [Contract](docs/semantics/COALESCE-ASSIGNMENT-REVIEW.md)
records delayed CVs, retained reference temporaries and separate write lines.

Quiet variable/DIM coalescing and compiled header/name conversion code **`a42fddfe`**
is accepted by [independent review](coverage/semantics/quiet-access-review.json):
295 exact sources, 18 separate outcome controls, author 8 state programs/3,760
assertions and independent 6/2,277. The previous286 independent source cases and
nine new originals are bound by exact bytes; nine canonical public CLI replays
also pass. Compiler gates cover5,336 lints plus focused 240 quiet,90 foreach and 111
list cases. Previous full source reports are historical after these watched changes.
The remaining old core controls are seven environment, three object quiet forms,
return and one nullsafe-reference iterable compiler context.

Array foreach code **`1f0e8810`**, runtime evidence **`7cdd513c`**, compiler evidence
**`c409e4be`** and [targeted independent review](coverage/semantics/foreach-runtime-review.json)
cover155 exact sources, author9 state programs/6,498 assertions and independent8/
3,096 assertions. Captured values/reference cells, per-iterator copy positions,
live insertion occurrences and abrupt loop cleanup are reviewed. The original
AssignRef, dead-map, serialization and hidden DIM-origin defects remain preserved.
Compiler evidence retains the historical5,027 aggregate, fresh89 focused lints/
20 metadata controls and final12 catalogue lints; exact bridges do not relabel old runs.
Objects/Traversable, frames/return and two compiler contexts remain unfinished.

Earlier accepted containers remain linked: [destructuring/effects](coverage/semantics/destructuring-review.json)
(`77f8d3c0`, selected283/state7/3,633, independent12/6,192),
[array unpack](coverage/semantics/array-unpack-review.json)
(`4ca826d2`, selected155/state31/2,454) and [foreach key prerequisites](coverage/semantics/foreach-publication-review.json)
(`75672577`, exactly three retired parser exceptions). The current full campaign
includes all155 unpack,263 list,17 precheck and155 foreach additions. Historical
ordinary4,407/25 on`a8f6aa0c` remains preserved by [its own audit](coverage/semantics/ordinary-campaign-audit.json).

Inventory remains **169 constructors/306 runtime obligations**, with 70 field
domains. Only oracle identity closes. Helper tests, compiler prepass traversal and
syntax acceptance do not close ordinary source-execution families.

## Next bounded work

The container checkpoint is audited. Array iteration now retains
persistent insertion occurrences, per-iterator saved copy positions and explicit
ownership/unwinding. [Contract and independent review](docs/semantics/FOREACH-REVIEW.md)
retain source rebinding, table replacement, copy selection and abrupt-exit originals.

Complete request environment, named/class/magic lookup, quiet access and
coalescing assignments before broader calls/frames, declarations, linked objects,
exceptions, dynamic sources, resumable services, lifetime and core intrinsics.
Three object quiet-coalescing forms and seven ordinary request-environment
cases remain explicit Unsupported work; none count as source agreements.
GLOBALS compiler candidates have independent private evidence; request-environment
and terminal isset/empty source publication remain pending. [Quiet/CV design review](docs/semantics/QUIET-CV-REVIEW.md) and 28 native
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
