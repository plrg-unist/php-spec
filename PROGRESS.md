# Core PHP semantics progress

Target: PHP 8.5.10 CLI NTS 64-bit. [PLAN.md](PLAN.md) defines complete core;
[the inventory](coverage/semantics/features.json) tracks obligations. Selected
source agreement does not establish complete semantics. Large evidence remains
outside Git; [ARTIFACTS.md](docs/ARTIFACTS.md) locates it.

## Current checkpoint

Raw INI storage and effective C-string paths are composed with public object
invocation. The exact tested union **6e7ddca894**, on **6ba0ee71/1305**, accepts
13 original sources (ten normal, three expected PHP errors) and thirteen finite
fixtures/675 assertions: author source11/510 and independent source2/file165.
The source-equivalent composition preserves current CALLS metadata **339553f6e**
and its tested source **18a1383d7**. The 2,011 local runtime inputs and compiler
are reused; no fresh offline rebuild is claimed.
[Prefix ledger](coverage/semantics/include-ini-prefix-review.json).

Public-source object invocation is installed at **18a1383d7**, on
**b3a02ebc/1304**. The [CALLS ledger](coverage/semantics/source-invoke-current-review.json)
records its bounded gates and distinct private history.

Installed Stringable SET evidence binds tested **13c9c4ddf**, with code
**3e3608369** over **9c8d8cab0**, on **d7d59e41/1302**. Author gates accept
source27 and five finite stages/188 assertions; six Unsupported checks remain
separate. Independent gates accept the recovered source2 tuples and fresh
owner79/finally50. [SET review](coverage/semantics/include-set-current-review.json)
preserves the unknown original source2 launcher exit, NUL-free old-value limits
and distinct private evidence. Restore04, remaining INI05 option conversion,
PIPE and full core closure remain open.

Earlier capture checkpoint is **c536d1f74**, with code **094761c66** and
tests through **8795d9c39** over **c8bee41e6**. Author and independent gates each
accept source9 and seventeen finite stages/541 maintained assertions on
**44edf5d2/1302**; the reviewer also accepts creator2/89.
[Capture review](coverage/semantics/method-capture-current-review.json) keeps
preinstallation source35/state40 and historical evidence separate.

Earlier selector142 checkpoint **e9af13fd0** accepts source2 and finite CONFIG1/26
on **87aa3f33/1294**. Whole-source ordinary CONFIG agreement remains untested
here. Earlier installed code **a993dd191** includes
ordinary fatal and Unsupported origin retirement, finite inherited internal
method contracts 189 at **cbd5236d2** and the constant
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

- Include/configuration: named Stringable `chdir` is installed at **09907c150**
  on **1f354b61/1302**, with author source17/four185 and independent source2/two89.
  Array-unpacked configuration calls are installed at **7423fc162** on
  **d2764798/1302**: author source23/six208, retained source3/four38 (six
  Unsupported controls) and named source3/four185. Independent fresh source2/two139
  passes; earlier private **63cd23b84** evidence and the original active fixture
  failure retain separate receipts.
  Stringable SET is installed at tested **13c9c4ddf**, code **3e3608369**, on
  **d7d59e41/1302**: author source24/four107, shared source3/directory1/81 and
  six separate Unsupported checks; independent recovered source2 and fresh
  owner79/finally50. Those earlier old-value witnesses are NUL-free. Current
  raw/effective INI-prefix acceptance is recorded at the checkpoint above.
  Restore and INI-option remain reviewed private increments.
  PIPE source24/returned2, callback210 plus48 Unsupported guards and directory158
  remain private; real CONFIG `__invoke` wrapper pipes remain Unsupported.
  Earlier c8/calls-base named and copied-c8 renderer/content bridges keep their
  separate receipts. Wider OS/INI behavior and lifecycle remain open.
  [Named ledger](coverage/semantics/include-named-current-review.json)
  · [unpack ledger](coverage/semantics/include-unpacked-current-review.json)
  · [SET ledger](coverage/semantics/include-set-current-review.json)
  · [pipe ledger](.tools/include-config-pipe-string-current/coverage/semantics/include-config-pipe-string-review.json).
- Calls: public/default-public nonstatic source `__invoke` is installed at
  **18a1383d7/b3a02ebc/1304**, over final SET **4015f160d**. Author checks
  accept source21/finite20/537; independent checks accept source37/finite29/997,
  including FIRST7/331 then SET79/finally50 before source/common finite20.
  Original stream/exit observations and fresh checked fixtures are independently
  audited; existing capture, named/unpack and finite CONFIG/SET guards survive.
  Private **486874ba6** source54/49-1,475 and source70/58-1,935, earlier47ed/9c8
  and the unexecuted named294 blueprint retain separate identities.
  Array classification, callable/string precedence, nonpublic/static publication,
  transformed weak wrappers, real CONFIG PIPE and correlated retired history remain open.
  [Public invocation ledger](coverage/semantics/source-invoke-current-review.json)
  · [capture ledger](coverage/semantics/method-capture-current-review.json)
  · [selector ledger](coverage/semantics/method-class-selector-review.json).
- Properties: the bounded private-c8 projection of typed static Stringable
  assignment197 and default-false reference infrastructure is accepted, with
  archival tip **55bbaf047**; no186 producer or installation is claimed.
  Author source2/private41/corrected callback63 and independent source1/68 remain
  separate from historical21/eight572. Declaration200 is privately accepted
  and archived at **502654618**. Direct201 accepts author54 native/model source
  tuples and independent source3/three188; earlier203d2/112,1c4/170 and failures
  remain distinct. Fresh actual-master projection/installation, delayed receivers,
  non-CV reference acquisition and full201 remain open.
- Compiler: publication190–196 remains private/unaccepted. Freeze17 has four
  bounded runtime passes; receiver-free/null-scope fails before SOURCE_PENDING.
  The null/null181 producer repair has source-only approval; runtime renewal,
  native18/file20, current capture compatibility and full publication/syntax remain
  pending. Earlier freezes and failures retain their identities. Constants183/184
  depend on publication.
- Argument introspection198/199 remains private on fdef. All111 ordinary
  native/model tuples agree; the original112 aggregate remains FAIL with a
  separately accepted focused status correction. Finite evidence combines its
  original16/373 pass subset with four corrected legal fixtures/87, preserving
  the failed aggregate; no fresh full source/finite run is claimed. Compatibility
  corrections, independent state/final code review and installation remain pending.
  Generator/Fiber/handler interactions are later gates. The ignored
  [core roadmap](.tools/core-roadmap-11/roadmap.txt) guides remaining obligations.

`returns_verify` is temporarily paused by the user. Preserve its branches and
evidence; do not retry the blocked engine experiment, substitute a reviewer,
merge changes awaiting its validation, or begin work depending on those
unaccepted changes. Independent work proceeds from the accepted baseline.

Nonpublic/static `__invoke` publication, array callables, remaining
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

Root's force-index write and the fresh actor's
[write check](.tools/git-integration-static142-permission-20261002.json) succeeded.
Static142 and the capture union are installed with accepted bounded gates. The
legacy author's denied [recheck](.tools/calls-static142-git-write-recheck.json)
and [staging receipt](.tools/calls-static142-git-add-denial-20261002.json) remain
historical and actor-specific. Fresh implementors integrate independently reviewed
milestones under temporary coordinated canonical writer leases.

The [migration ledger](coverage/semantics/throwable-migration-review.json) and
[artifact guide](docs/ARTIFACTS.md) retain deferred failures and raw evidence.
