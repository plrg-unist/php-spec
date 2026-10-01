# Core PHP semantics progress

Target: PHP 8.5.10 CLI NTS 64-bit. [PLAN.md](PLAN.md) defines complete core;
[the inventory](coverage/semantics/features.json) tracks obligations. Selected
source agreement does not establish complete semantics. Large evidence remains
outside Git; [ARTIFACTS.md](docs/ARTIFACTS.md) locates it.

## Current checkpoint

Canonical Git HEAD is **fdef6285d**, a documentation checkpoint over installed
code **a993dd191**, with ordinary fatal and Unsupported origin retirement,
finite inherited internal method contracts 189 at **cbd5236d2** and the constant
internal catalogue accepted at **832250521**. Installed code also includes deferred
Closure/arrow cache authentication 91, ordinary class static properties,
Stringable-`chdir`, and named/reference `Closure::call`.
[Milestone history](MILESTONE-HISTORY.md) links the bounded installed evidence
and preserves distinct historical, projected and installed fingerprints.

The finite 189 increment covers inherited Stringable/Throwable and
Exception/Error/ErrorException contracts plus source `__wakeup` checks.
Seven explicit Unsupported controls still bound compiler publication, and two
reporting-timing originals remain Unsupported. Real early declaration
publication and diagnostic ordering is the immediate next compiler milestone,
before constants183/184; it must remove the interim rooted wakeup guard.
[Renewed interface ledger](coverage/semantics/interface-internal-renewed-review.json)
· [declaration-order milestone](coverage/semantics/compiler-declaration-order-review.json).

Installed origin retirement preserves diagnostic origins, traces and saved-frame
cleanup. Its ledger distinguishes the minimal installed checks from the private
current bridge, original failures, fixture corrections, composite pauses and timeout.
[Cleanup ledger](coverage/semantics/error-origin-author.json).

## Validated baseline

The accepted post-arrow integration checkpoint is **1026/0ec57507**, with
arrow capture and returns 117/118 at **87cdc532f**. Its
[review](coverage/semantics/post-arrow-integration-review.json) binds distinct
profiles and independent audits:

| Gate | Accepted observations |
| --- | --- |
| Compiler | 5,751 source lints, 8 access sources, 15 line observations; verified existing binary reused |
| Explicit request | 263 source profiles, 526 responses with exact request/environment facts |
| Callable | 946 maintained rows in 18 suites plus one explicit regression; 1,894 responses |
| Ordinary | 5,706 source comparisons (4,060 normal, 1,006 PHP errors, 640 static rejections), 21 separate controls; 11,435 process records |

These are observations, not unique PHP programs. The ordinary profile inherits
process environment subject to LC_ALL/TZ settings; request and callable gates
have their own profiles. Their counts are not interchangeable.

## Active work and remaining obligations

Generic156 delayed reference-return replay remains open, including runtime
foreach/switch owners and consumed finalizers. Temporary-return Notice timing
and typed by-reference string conversion186 require separate repairs, captured
operand ownership, write-back and post-finally rejection. Weak parameter and
property string conversion, constrained references, interpolation and dynamic
names remain separate consumers; the inverse typed string-reference object
parameter/config callback combination is untested.
[Finally contract](docs/semantics/SOURCE-FINALLY.md) ·
[string contract](docs/semantics/USER-STRING.md).

Ordinary static properties187/188 and generic91 deferred default-cache
authentication are installed. Typed property/CV-reference object conversion,
default-false186 witness support, exceptional singleton clone provenance,
readonly/asymmetric set access and scoped defaults remain open.
[Property ledger](coverage/semantics/class-static-properties.json) ·
[property contract](docs/semantics/SOURCE-CLASS-STATICS.md) ·
[default-cache ledger](coverage/semantics/closure-default-cache-review.json).

The independent private lanes currently include:

- Include/configuration: named operands, array unpack, Stringable
  `set_include_path`/`ini_restore`, and `ini_set` option conversion have reviewed
  private checkpoints. Their current canonical projection and installation are
  pending. Pipe source24, two returned-callable sources, six paused stages/258
  assertions and two directory stages/158 assertions pass private review,
  with retained controls separate. The repaired fixture
  distinguishes intermediate ownership from terminal release; real `__invoke`
  wrapper pipes remain Unsupported. The current-fdef five-increment content
  projection is reviewed but its semantic bridges are pending.
  [Private include ledger](.tools/include-config-ini-option-current/coverage/semantics/include-stringable-ini-option-review.json)
  · [pipe ledger](.tools/include-config-pipe-string-current/coverage/semantics/include-config-pipe-string-review.json).
- Calls: static-method142 has reviewed fdef source2 and finite2/59 evidence;
  installation remains pending. The called-class mixed-snapshot aggregate is
  privately reviewed, with receiver-free116 independent coverage still pending.
  Callable capture remains open.
  [Selector ledger](coverage/semantics/method-class-selector-review.json).
- Properties: private197 review **a778904d** accepts combined-fdef source1,
  cleanup55 and body elaboration, separately from historical21/eight572.
  Asymmetric static access200/201 is the next lane; delayed writes remain open.
- Compiler: declaration publication190–196 is private work. Historical private
  raw observations show its first three groups passing, the rebound group
  failing, and later groups unrun. Publication Unsupported controls remain
  unaccepted. The reviewed195 bounds repair still encounters a valid-history
  rejection under diagnosis; constants183/184 depend on publication.
- Argument introspection198/199 has a development/review pair. Implementation
  and validation remain pending. The ignored
  [core roadmap](.tools/core-roadmap-11/roadmap.txt) guides remaining milestones
  and inventory gaps; it establishes no closure.

`returns_verify` is temporarily paused by the user. Preserve its branches and
evidence; do not retry the blocked engine experiment, substitute a reviewer,
merge changes awaiting its validation, or begin work depending on those
unaccepted changes. Independent work proceeds from the accepted baseline.

Source `__invoke`, callable/string precedence, array callables, remaining
static members, traits, hooks, traversal, output handlers, broader OS/INI
behavior, transformed wrappers and lifecycle callbacks remain core obligations.
Static-variable coverage remains partial across trait
and inheritance sharing, clone/bind, include/eval reactivation and lifecycle/GC.
[Include contract](docs/semantics/INCLUDE-SOURCES.md) ·
[method contract](docs/semantics/SOURCE-METHODS.md) ·
[named](coverage/semantics/function-statics-review.json),
[main](coverage/semantics/main-statics-review.json) and
[Closure](coverage/semantics/closures-review.json) static-cell ledgers.
Rocq interaction-tree semantics and BOLA proofs follow completed PHP core.

## Validation limits

The authorized cap is five numeric/model campaigns with explicit slot handoffs.
The [resource receipt](.tools/resume-recovery-20261001/resource-audit-10second.json)
records the observations supporting that cap. Reviewed source, paused-state and
syntax results are bounded evidence. Interrupted runs, timeouts, Unsupported
and budget controls are never native agreements. A fresh offline,
network-isolated rebuild and full current-source closure remain required.

Git write access is restored after the orchestrator's successful authorized
write check; the earlier denied
[recheck](.tools/calls-static142-git-write-recheck.json) remains historical.
Reviewed integrations resume under sole canonical writer leases. Calls holds
that lease for static142; installation has not yet occurred, and it waits for
the frozen fdef bridge to finish. This documentation edit grants no semantic
writer lease.

The [migration ledger](coverage/semantics/throwable-migration-review.json) and
[artifact guide](docs/ARTIFACTS.md) retain deferred failures and raw evidence.
