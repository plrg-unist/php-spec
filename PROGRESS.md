# Core PHP semantics progress

Target: PHP 8.5.10 CLI NTS 64-bit. [PLAN.md](PLAN.md) defines complete core;
[the inventory](coverage/semantics/features.json) tracks obligations. Selected
source agreement does not establish complete semantics. Large evidence remains
outside Git; [ARTIFACTS.md](docs/ARTIFACTS.md) locates it.

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

These counts are observations, not unique PHP programs. The ordinary profile
inherits process environment subject to the producer's LC_ALL/TZ settings;
request and callable gates have their own profiles. Interrupted prefixes,
timeouts, runner failures, Unsupported and budget controls are not agreements.

## Current checkpoint

The current canonical semantic checkpoint is Stringable-`chdir` **1043567c4**,
installed at **0b6a15cbb** on named/reference `Closure::call` **9cdadc172**.
[Milestone history](MILESTONE-HISTORY.md) and the linked ledgers
retain bounded installed counts and historical snapshot identities.

Installed code includes finite file context, selected configuration calls and
weak positional Stringable-`chdir` operands,
weak by-value typed string returns, interfaces, Closure binding/calls, source
Throwable subclasses, and echo/print/cast/eval/concat object-string callbacks.
[Include contract](docs/semantics/INCLUDE-SOURCES.md) ·
[method contract](docs/semantics/SOURCE-METHODS.md) ·
[string contract](docs/semantics/USER-STRING.md).

The Stringable ledger separates the projected catalogue of 52 sources and
protocol/retained evidence
at **15d2451bf** from three installed sources and one directory stage/52 assertions.
Callback traces preserve declaring identity and explicit invocation frames.
The nested-conversion producer alone uses 180 seconds after a measured
five-request replay; model requests keep their 60-second limit. Historical
nine-source evidence and the interrupted 50-source prefix remain separate.
[Ledger](coverage/semantics/include-stringable-chdir-review.json).

## Active work and remaining obligations

Generic156 return/Notice replay remains open. By-reference typed string return
conversion186 still needs captured-alias write-back and post-`finally` rejection.
Deferred real-Closure default caches fail the global state guard and need a
separate generic91 repair.
[Argument review](coverage/semantics/closure-call-arguments-review.json).

Static class properties 187/188 have a private bounded candidate on this base: declaration-owned cells, inherited sharing, typed aliases and source access pass prior 40+9 exact cases, with current-base typed-return/include bridges and retained alias integrity passing. [Ledger](coverage/semantics/class-static-properties.json). Canonical installation, resumable typed object conversion and post-evaluation selector provenance remain open.

Weak parameter and property string conversion, constrained references,
interpolation and dynamic names remain separate consumers. The inverse typed
string& object-parameter/config callback combination is untested. Source
`__invoke`, callable/string precedence, array callables, inherited internal
interface signatures, constants, static/readonly members, traits, hooks,
traversal, output handlers and lifecycle callbacks remain active core work.
File inclusion still needs named/unpacked object operands for `chdir`, broader
OS/INI behavior and transformed wrappers. Rocq interaction-tree semantics and
BOLA proofs follow completed PHP core semantics.

The inventory's pending `calls.static-variables` row still needs reconciliation
with accepted bounded [named](coverage/semantics/function-statics-review.json),
[main](coverage/semantics/main-statics-review.json) and
[Closure](coverage/semantics/closures-review.json) bindings; wider static-variable
obligations remain open.

## Validation limits

The authorized cap is five numeric/model campaigns with explicit slot handoffs.
The [resource receipt](.tools/resume-recovery-20261001/resource-audit-10second.json)
records the CPU, memory and pressure observations supporting that cap.

Reviewed source, paused-state and syntax results are bounded observations,
not complete-core acceptance. Interrupted runs, timeouts, Unsupported and budget
controls are never native agreements. A fresh offline network-isolated rebuild
and full current-source closure remain required. The
[migration ledger](coverage/semantics/throwable-migration-review.json) and
[artifact guide](docs/ARTIFACTS.md) retain deferred failures and raw evidence.
