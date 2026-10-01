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

The current semantic code checkpoint is **aed684e4a** (ordinary `Closure::call`),
following selected configuration calls **7b1392648**, unused reference-return
retention **08b929694**, finite-mode
dispatch guard **5d717bbeb**, mutable file context **35b226471** and
provider-fixture repair **badc320f28b**. It retains weak typed string returns, interface,
Closure-binding and source-Throwable code. Interfaces check
ordered links, nominal membership, method variance, abstract obligations and
authenticated `Exception`/`Error` ancestry for direct or transitive
`implements Throwable`. Their [ledger](coverage/semantics/interface-author.json)
separates installed compiler/runtime checks from historical syntax evidence.

File inclusion and generic file traces, resolver-null identity, directory
open-failure diagnostics, static/scoped methods, first-class callables,
Closure binding, source Throwable subclasses, and echo/print/cast/eval/concat
object-string callbacks are installed. The bounded source, paused and bridge
counts belong in [milestone history](MILESTONE-HISTORY.md) and their linked
ledgers. [Include contract](docs/semantics/INCLUDE-SOURCES.md) ·
[method contract](docs/semantics/SOURCE-METHODS.md) ·
[string contract](docs/semantics/USER-STRING.md).

## Active work and remaining obligations

Weak by-value typed string returns 185 are installed. The historical
source-Throwable catalogue, paused stages, two-file strictness and
Closure-binding bridge pass. On the installed tree, a class implementing an
interface-declared `__toString` matches PHP under a measured 90-second model
limit; one paused marker stage and inventory pass. The same source times out
under the generic 45-second runner; both failed reports remain distinct from
the bounded agreement.
[Ledger](coverage/semantics/user-string-typed-author.json).

Finite mutable include context is installed at **35b226471** on typed returns **e4d3b837b**. Versioned lookup keys, narrow `include_path` mutations, and authenticated finite `chdir` facts pass three installed source controls (including typed-return callback output `77`), 107 directory-pause, 19 adapter, 57 INI and 46 saved-frame assertions. The earlier 28-source catalogue remains historical to the interface/Closure base. [Ledger](coverage/semantics/include-mutable-context-review.json). Stringable operands and broader OS/INI behavior stay open.

Reached configuration calls without finite file mode return explicit
`Unsupported` before scalar dispatch. One checked source control, six paused
stages (63 assertions), and three retained finite native/model sources pass;
the unsupported control is not native agreement.
[Ledger](coverage/semantics/include-no-file-guard-review.json).

Module99 retains unused reference-return operands through finalizers while
preserving used temporary aliases. Five installed source comparisons and two
paused stages (30 assertions) pass, independently of pending generic156 replay.
[Ledger](coverage/semantics/reference-unused-finally-installed.json).

Exit-origin cleanup is installed at **b54f984b4** independently of return replay.
Six installed sources preserve exact output and exit status; two public paused
stages (64 assertions) cover suppression and saved-caller foreach cleanup.
Private six-stage evidence (163 assertions), retained exit checks (126 assertions),
the original pause failure and draft reporting assertion remain distinct.
[Ledger](coverage/semantics/exit-origin-author.json).
Generic156 recovery, temporary-return Notice timing and conversion186 remain open.

Selected configuration calls authenticate computed strings and pipes across
argument evaluation, saved frames and a `chdir` pause. Four source comparisons
and nine paused stages (113 assertions) at **949b6a938** project across the
installed reference-return change. One current source
matches both unused reference-return branches while a selection is saved,
including exact Notice bytes. The original 35-source and retained-frame gates
remain historical; the maintained catalogue now contains 36 sources.
[Ledger](coverage/semantics/include-dynamic-selected-review.json).

Ordinary `Closure::call` 182 has passed bounded source, paused and compatibility
review, with focused installed selected-call, typed-string callback and
reference-return finalizer checks. Private36-source/7-stage evidence retains its
earlier executable snapshot. Named receivers, unpacking and reference formals
remain active extensions. Current private named receiver sources11/stages5 and
reference-formal sources14/stages9 pass on the verified current adapter; canonical
projection has a passing focused forwarding/exit bridge; installed identity
remains pending. A source-derived deferred
real-closure default cache still fails its global state guard and requires a
separate generic91 repair.
[Ledger](coverage/semantics/closure-call-review.json).
[Argument extension review](coverage/semantics/closure-call-arguments-review.json).

By-reference typed return conversion 186 needs captured-alias write-back and a
generic post-`finally` rejection replay. Weak parameters, properties,
constrained references, interpolation,
dynamic names and other string contexts remain separate consumers. Source
`__invoke` and callable/string precedence, `Closure::call`, array callables,
inherited internal interface method signatures, constants, static/readonly
members, traits, hooks, traversal, output handlers and lifecycle callbacks
remain active core obligations. The inventory still needs its pending
`calls.static-variables` row reconciled with accepted bounded named, main and
Closure static bindings ([named](coverage/semantics/function-statics-review.json),
[main](coverage/semantics/main-statics-review.json),
[Closure](coverage/semantics/closures-review.json)); broader static-variable
obligations remain open.
Canonical file inclusion still needs stringable `chdir` operands, wider OS/INI
failure modes and transformed wrappers. Rocq
interaction-tree semantics and BOLA proofs follow the completed PHP core.

## Validation limits

The reviewed source, paused-state and syntax results are bounded observations, not complete-core acceptance. Interrupted runs, timeouts, Unsupported and budget controls are never native agreements. A fresh offline network-isolated rebuild and full current-source closure are still required. The [migration ledger](coverage/semantics/throwable-migration-review.json) and [artifact guide](docs/ARTIFACTS.md) retain deferred failures and raw evidence locations.
