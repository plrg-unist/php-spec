# Core PHP semantics progress

Target: PHP 8.5.10 CLI NTS 64-bit. [PLAN.md](PLAN.md) defines complete core;
[the inventory](coverage/semantics/features.json) tracks obligations. Selected
source agreement does not establish complete semantics. Large evidence remains
outside Git; [ARTIFACTS.md](docs/ARTIFACTS.md) locates it.

## Current checkpoint

The released canonical checkpoint is **d386a9f5d**, with finite inherited
internal method contracts 189 at **cbd5236d2** and the constant internal
catalogue accepted at **832250521**. Installed code also includes deferred
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

Ordinary fatal/Unsupported origin retirement and its focused current-base bridge
are privately reviewed and await installation. They preserve diagnostic origins,
traces and saved-frame cleanup. The ledger retains the original failures,
fixture corrections, composite pauses and timeout separately.
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

Source `__invoke`, callable/string precedence, array callables, constants,
remaining static members, traits, hooks, traversal, output handlers and
lifecycle callbacks remain active core work. File inclusion still needs
named/unpacked object operands for `chdir`, broader OS/INI behavior and
transformed wrappers. Static-variable coverage remains partial across trait
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
The [migration ledger](coverage/semantics/throwable-migration-review.json) and
[artifact guide](docs/ARTIFACTS.md) retain deferred failures and raw evidence.
