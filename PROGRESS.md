# Core PHP semantics progress

Target: PHP 8.5.10 CLI NTS 64-bit. [PLAN.md](PLAN.md) defines complete core;
[the inventory](coverage/semantics/features.json) tracks obligations. Syntax
agreement and selected differential cases do not establish complete semantics.
Large historical evidence is outside Git; [ARTIFACTS.md](docs/ARTIFACTS.md)
locates it.

## Current checkpoint

The accepted post-arrow integration baseline is **1026/0ec57507**, with accepted arrow capture
and returns 117/118 at commit **87cdc532f**. Its [post-arrow integration review](coverage/semantics/post-arrow-integration-review.json) binds independent audits:

| Gate | Accepted result and profile |
| --- | --- |
| Compiler | 5,751 source lints, 8 access sources and 15 line observations; verified existing binary reused |
| Explicit request | 263 source profiles, 526 responses with exact primitive request and environment facts |
| Callable | 946 maintained rows in 18 suites plus one separate explicit regression, 1,894 responses |
| Ordinary | 5,706 source comparisons (4,060 normal, 1,006 PHP errors, 640 static rejections) and 21 separate outcome controls; 11,435 process records |

These gates have distinct source/request profiles and may repeat programs; counts
are observations, not unique PHP programs. The earlier interrupted ordinary
prefix and callable partial suite are preserved as incomplete. The ordinary
profile inherits process environment, qualified by the producer's LC_ALL/TZ
settings. The control timeout, runner failure, budget and Unsupported outcomes
are controls, not source agreements.

First-class named-function callable conversion 119/120 is installed after the
1026 integration checkpoint. Its [review](coverage/semantics/first-class-review.json)
binds exact accepted semantic bytes, 17 source outcomes (13 normal, 3 PHP errors,
1 static rejection), four separate reference-context pairs and paused-state
guards. Canonical checks passed: 17 source outcomes, eight compiler projections,
three paused stages/49 assertions and inventory consistency. Its maintained
source report is retained under `.tools/first-class-gsi1pf5r/` with the same
4082bb8c implementation fingerprint as the accepted private audit. This is a
partial callable increment; builtin/method/array/constant-context forms remain.

Pipe arrow grouping and static rejection 121 are installed after 119/120.
[Syntax review](coverage/semantics/pipe-syntax-review.json) records the exact
private-candidate file matches, eight focused source/roundtrip/lint profiles,
missing-fact control, cumulative parser patch reproduction and the separately
reviewed 30,980-entry classified syntax gate. Pipe compiler/runtime 122/123 are
now installed as a separate increment. [Runtime review](coverage/semantics/pipe-review.json)
binds 12 maintained outcomes (7 normal, 5 PHP errors), nine separately reviewed
original-source pairs, and paused task/ownership guards. Canonical checks passed:
12 source outcomes, five protocol stages/89 assertions, first-class regression
17 source outcomes and three stages/49 assertions, and inventory consistency.
The canonical pipe report is under `.tools/pipe-xae4rjrd/` with implementation
fingerprint f7ae0856; the accepted private 39b89d3c identity remains distinct.
Builtin/method/array/object callable dependencies remain open.

Switch syntax and compiler/runtime 124/125 now support ordered case scanning,
default selection, fallthrough, typed break/continue, compile diagnostics and
saved subject ownership. [Switch review](coverage/semantics/switch-review.json)
binds 18 maintained source outcomes (12 normal, 2 PHP errors, 4 static
rejections), six paused stages/85 assertions, and six independently replayed
original-source pairs. The constant-boolean subject branch uses an authenticated
compiler fact, preserving its NaN warning without changing dynamic equality.
The full 30,980-entry classified syntax gate is recorded separately in the
review. Object-dependent comparisons and remaining control forms are open.

Named empty user classes 126/127 now have source-authenticated early and
conditional publication, nominal allocation and identity, literal `instanceof`,
exact class types, and known empty-object consumers. The pinned `-n` catalogue
reserves 166 internal class/interface/enum names for redeclaration diagnostics.
The [object review](coverage/semantics/object-classes-review.json) binds 31
maintained source outcomes and paused class/task/ownership guards; this is a
partial object increment.

Labels and goto 128/129 now compile per callable with exact label spelling and
source-derived target and owner paths. Runtime jumps can enter ordinary branches,
reuse the active loop/foreach/switch continuation or release exited owners.
The [goto review](coverage/semantics/goto-review.json) binds retained static
observations, source outcomes, descriptor projections and paused ownership/task
guards. `try`/`finally` interaction remains open.

## Next work

Authored internal `stdClass` identity is the next adjacent object step;
inheritance, properties, methods and Throwable follow. Match,
exceptions/finally, remaining
core intrinsics, traversal, dynamic lifetime and collection obligations remain
open. Full current-source closure and a fresh offline network-isolated rebuild
are required before complete-core acceptance. The early research goal of Rocq
interaction-tree semantics and BOLA proofs remains downstream of this work.
