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

The installed file-trace code checkpoint is **ffebfc971**, building on internal callable capture at **a4e7b8b62**, source-method capture at **139e66b13** and finite-provider file inclusion at **70fd71f12**. The original include increment had 26 exact source outcomes, 100 file-pause assertions, 43 mixed saved-frame assertions, 10 adapter assertions and 27 retained eval assertions; its classified file-syntax gate covered 30,980 rows with a separate one-file identity bridge. The trace extension has 39 exact source outcomes, 100 file-pause and 46 mixed saved-frame assertions, plus retained eval and Throwable trace selections. A private resolver-null followup at **dd9710518** has 41 exact include outcomes, 118 file-pause, 46 saved-frame and 20 adapter assertions; canonical integration remains pending. [Include contract](docs/semantics/INCLUDE-SOURCES.md) · [provider ledger](coverage/semantics/include-source-author.json) · [trace ledger](coverage/semantics/include-trace-review.json) · [resolver-null ledger](coverage/semantics/include-resolver-null-review.json).

Static/scoped methods, user-object string conversion, first-class source method capture and finite internal first-class captures are installed. The source-method increment retains its frozen 23-source and five-stage paused evidence; its include-base required-file capture, five focused source controls and three paused controls also pass on the installed tree, with independent exact replay of the included-file case. Its [ledger](coverage/semantics/first-class-method-review.json) separates these bases and hashes. The internal capture [ledger](coverage/semantics/first-class-internal-review.json) records nine exact source controls, four paused stages and independent replay, plus bounded installed checks. The full evidence and scope for earlier increments remain in [MILESTONE-HISTORY.md](MILESTONE-HISTORY.md).

The separate global closure-integrity repair is installed at **9e7879617** (code **60eea72cb**) with nine exact source controls and six paused stages, including retained getter wrappers. Its [ledger](coverage/semantics/first-class-internal-integrity.json) records the installed checks.

## Active work and remaining obligations

Active work covers Closure binding/call behavior, interface declarations and method lookup, remaining object conversion consumers, finite file-provider followups, and Throwable subclass behavior. These branches require their own current-base bridges and reviews before installation.

Eval object operand conversion is installed at **3a2997e10**. It reuses the owned source `__toString` call; the file-trace-base catalogue has 11 exact outcomes and one explicit weak nested-return Unsupported control. Installed focused throw, included-file bridge and five paused stages pass. The combined captured-closure/eval throw and full repository test target also pass. Earlier include-base evidence and the original failing bridge remain separate in the [ledger](coverage/semantics/user-string-eval-author.json). Concat and typed callbacks follow. [Contract](docs/semantics/USER-STRING.md).

Complete core still needs static/readonly members, traits, hooks, user magic methods, remaining Throwable accessors and internal protocols, conversion callbacks, output handlers, traversal and lifecycle integration, and broader source and pause closure. File inclusion still needs mutable CWD/include_path context, wider stream failures, and resolver-null wrappers beyond the bounded identity-transform witness. Generated finally linking remains transition-local; exit bypasses catch/finally while shutdown/destructor callbacks remain open. Rocq interaction-tree semantics and BOLA proofs follow the completed PHP core.

## Validation limits

The reviewed source, paused-state and syntax results are bounded observations, not complete-core acceptance. Interrupted runs, timeouts, Unsupported and budget controls are never native agreements. A fresh offline network-isolated rebuild and full current-source closure are still required. The [migration ledger](coverage/semantics/throwable-migration-review.json) and [artifact guide](docs/ARTIFACTS.md) retain deferred failures and raw evidence locations.
