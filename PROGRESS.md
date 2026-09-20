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

Pipe semantics is reviewed in a private candidate but not installed. It has 12
maintained outcomes (7 normal, 5 PHP errors) and a separately reviewed 30,980
entry classified syntax gate for the pipe arrow grouping prerequisite. Their
fingerprints and raw audits remain separate from this baseline.

## Next work

Install the reviewed pipe grouping/static prerequisite and pipe runtime/compiler
increment as small commits after the first-class successor.
Keep the parser's cumulative patches reproducible, preserve exact test profiles,
and update the inventory and documentation with each accepted increment.

The next independent language lane is switch: case selection, fallthrough,
continue/break levels, compile priorities and semicolon-case metadata. Empty
class linking/allocation and object identity form a separate foundation for
methods, properties and Throwable. Match, goto, exceptions/finally, remaining
core intrinsics, traversal, dynamic lifetime and collection obligations remain
open. Full current-source closure and a fresh offline network-isolated rebuild
are required before complete-core acceptance. The early research goal of Rocq
interaction-tree semantics and BOLA proofs remains downstream of this work.
