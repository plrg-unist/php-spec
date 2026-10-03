# Core PHP semantics progress

Target: PHP 8.5.10 CLI NTS 64-bit. [PLAN.md](PLAN.md) defines complete core;
[the inventory](coverage/semantics/features.json) tracks obligations. Selected
source agreement does not establish complete semantics. Large evidence remains
outside Git; [ARTIFACTS.md](docs/ARTIFACTS.md) locates it.

## Current checkpoint

Two-slot `ini_set` converts the normalized option before value rejection and
full-name lookup, then samples the full raw old value after callbacks. Strict
non-string options reject; null, empty and leading-NUL include-path updates
return false. Current SENT arrays must remain allocated; completed unpack
containers may retire. Tested **8cc6d7da5**, over accepted compiler/property
**d5208161a**, on **0100a13d/1349**, accepts three fresh normal source tuples
and the complete independent 83-assertion fixture. Nested property callbacks
preserve argument frames, and captured unpack survives container retirement.
Its 193-module SL and full83 AL compile; the 2,011 runtime inputs and compiler
are reused. Earlier **35fb2e410** accepts author49 source tuples and twelve
finite fixtures/494 assertions (464 ordinary, 30 Unsupported separate), plus
two independent source tuples. The original wrong caught-message assertion
and failed81/83 probes stay failed. The exact passed83 body is now a maintained
CONFIG regression; metadata adds no execution credit.
[INI ledger](coverage/semantics/include-stringable-ini-option-review.json).
Next: raw `get_include_path`/`ini_get`, shared primitive/null Restore option
parsing, then PIPE. Wider directives, lifecycle and full core remain open.

Typed static Stringable assignment197 composes with current Restore172,
ARG198/199, callable-first admission and raw/effective INI171/172. Tested
**7c5d4d06c** over **c95946455** accepts the nested Restore/property source
`BPR0.:1|s\0typed`: callbacks see zero arguments, the saved caller keeps one,
Restore resets the initial path and the property preserves all string bytes.
Earlier **f19c0a0bc** accepts the live `func_get_arg(0)` source `BS|ok`; focused
INI **a09291886** accepts source2/755 (normal266, throw256, captured file165,
static68). Its original normal329 timeout has no state credit. Prior **b566**
author31/independent15 gates remain distinct.
[Property ledger](coverage/semantics/typed-static-string-assignment-review.json).
Reused executables and source-equivalent publication add no rebuild or fresh
execution credit; broader property consumers and full core remain open.

Stringable Restore now converts weak options through checked callbacks and uses
full-name lookup: exact `include_path` resets the initial raw value, while
empty, case and NUL-name misses preserve callback mutations. Original tested
**b33f42f080** accepts 34 source tuples and thirteen finite fixtures/524 assertions
(496 ordinary, 28 Unsupported separate). Two fresh callable-priority sources on
**240bf5a75** remain distinct. Current ARG composition **88f8d2bd5**, over
**b0dbe76ce** on **14344140/1322**, accepts two further normal sources: callers
retain their two arguments, callbacks see zero, and strict owned Restore remains
weak. Its 185-module SL compilation passes; the 2,011 runtime inputs and compiler
are reused. [Restore ledger](coverage/semantics/include-stringable-restore-review.json).
The two-slot INI checkpoint above extends option/value conversion separately.
Raw getters, primitive/null Restore parsing, PIPE and wider INI remain open.

Ordinary-frame argument introspection198/199 is installed in composition with
accepted public object invocation, raw/effective INI paths and callable-first
parameter admission. Tested **244837b72**, over **b8a6f43f8**, accepts one fresh
normal source tuple and two finite checkpoints/106: the callable object survives
weak `callable|string` reception and its named source `__invoke` keeps genuine
current and saved argument frames. Prior INI composition **f8cc91079** accepts
source1/two133; prior CALLS union **1d61537bf** retains distinct author mixed
source3/finite19-596 and independent source2/finite2-147 evidence.
[Argument union ledger](coverage/semantics/argument-introspection-calls-current-review.json).
Source-equivalent installation adds no fresh execution credit. Local executables
are reused; a fresh offline rebuild and full core remain open.

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
and distinct private evidence. The later INI checkpoint above is separate;
raw readback, primitive/null Restore, PIPE and full core remain open.

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

The publication190–196 rules preserve ordered class/function availability,
earlier diagnostics, and authenticated declaration history. The seven former
publication Unsupported controls and typed companion now have maintained
regressions; the interim rooted wakeup guard is removed. Compile-stop retains
completed mutations and freezes saved callers while retiring active file replies.
[Publication review](coverage/semantics/compiler-publication-review.json) separates
the fresh copied revision from later INI/argument/Restore compositions.
Constants183/184 is next; two reporting-mask/error_reporting controls
remain later core obligations.

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
operand ownership, write-back and post-finally rejection. Broader weak parameter
and property string conversion, constrained references, interpolation and dynamic
names remain separate consumers; the inverse typed string-reference object
parameter/config callback combination is untested.
[Finally contract](docs/semantics/SOURCE-FINALLY.md) ·
[string contract](docs/semantics/USER-STRING.md).

Ordinary static properties187/188 and generic91 deferred default-cache
authentication are installed. Broader property/CV-reference object conversion,
default-false186 witness support, exceptional singleton clone provenance,
readonly/asymmetric set access and scoped defaults remain open.
[Property ledger](coverage/semantics/class-static-properties.json) ·
[property contract](docs/semantics/SOURCE-CLASS-STATICS.md) ·
[default-cache ledger](coverage/semantics/closure-default-cache-review.json).

Current family status:

- Include/configuration: raw/effective paths, Stringable SET/Restore and
  two-slot INI conversion are covered by distinct checkpoints above. The current
  nested property/captured-unpack source3/full83 checks are separate from prior
  source51/finite494 and original failed81/83. Raw `get_include_path`/`ini_get`
  and primitive/null Restore parsing are next, then PIPE; wider OS/INI stays open.
  [INI ledger](coverage/semantics/include-stringable-ini-option-review.json)
  · [Restore ledger](coverage/semantics/include-stringable-restore-review.json)
  · [INI prefix ledger](coverage/semantics/include-ini-prefix-review.json)
  · [SET ledger](coverage/semantics/include-set-current-review.json).
- Calls: public source `__invoke` is installed at **18a1383d7**; callable-before-
  string parameter admission is installed at **b8a6f43f8**. Its distinct private
  author25/eleven394 and independent17/eight241 gates retain separate Unsupported
  controls; the current INI interaction adds source2/one53 without replay.
  Array/broader class-method classification, nonpublic/static publication,
  transformed wrappers and real CONFIG PIPE remain open. No new return agreement
  or paused-return dependency is claimed.
  [Invocation ledger](coverage/semantics/source-invoke-current-review.json)
  · [callable parameter ledger](coverage/semantics/callable-string-current-review.json).
- Properties197: weak simple typed static Stringable assignment, live-row alias
  rechecks and callback ownership are implemented and independently accepted in
  the current Restore/ARG/CALLS/INI composition above. Nested Restore keeps
  current/saved argument frames; full-byte INI/property separation, leading-NUL
  rejection, inherited capture/file and original static controls pass.
  Delayed receivers, non-CV reference acquisition, constrained-reference object
  conversion, readonly/asymmetric access and broader consumers remain open.
  [Property ledger](coverage/semantics/typed-static-string-assignment-review.json).
- Compiler publication190–196 passes the isolated private `4b3c1a85` rebuild:
  source30, history6/107, modifier26/286, classified corpus30980 and complete
  inventories. Later INI composition accepts one paired source and four finite
  fixtures/200. Its argument callback adds one paired source and one finite
  fixture/42 predicates, with count0 before mutation and compile-stop.
  Accepted Restore adds one paired fatal source and one finite fixture/42: the
  callback sees count0 and its completed raw mutation survives the compiler cut.
  Typed-static conversion adds one paired fatal source and one finite fixture/57:
  the row stays `old`, and the frozen caller retains the owned RHS.
  [Publication ledger](coverage/semantics/compiler-publication-review.json)
  separates tested revisions and original failures. Full core remains open.
- Argument introspection198/199 is installed with bounded acceptance at the
  current checkpoint. Its fdef, SET13c, CALLS18a, INI7dd and callable-b8 evidence
  remains distinct in [the union ledger](coverage/semantics/argument-introspection-calls-current-review.json)
  and linked historical reviews. The original legal getter witness is nativepass/
  modelUnsupported with zero agreement; getter admission is an open include
  obligation. Generator/Fiber/handlers, broader callable interactions, a fresh
  rebuild and full core remain open.

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
