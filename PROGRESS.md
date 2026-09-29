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

The current canonical checkpoint is **0832d4a42** (weak typed string returns 185)
on the installed interface, Closure-binding and source-Throwable code. Interfaces check
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

A private mutable-context candidate is rebased onto installed typed returns at **e4d3b837b**. It adds versioned include lookup keys, narrow `include_path` mutations, and authenticated finite `chdir` facts. A focused typed-return callback that includes after `chdir`, then includes again in its caller, matches PHP (`77`); six retained source rows, directory/INI/saved-frame protocols and independent three-source replay pass. The earlier 28-source catalogue remains historical to the interface/Closure base. [Ledger](coverage/semantics/include-mutable-context-review.json). Canonical installation remains; dynamic selected calls, stringable operands and broader OS/INI behavior stay open.

By-reference typed return conversion 186 needs captured-alias write-back and a
generic post-`finally` rejection replay. Weak parameters, properties,
constrained references, interpolation,
dynamic names and other string contexts remain separate consumers. Source
`__invoke` and callable/string precedence, `Closure::call`, array callables,
inherited internal interface method signatures, constants, static/readonly
members, traits, hooks, traversal, output handlers and lifecycle callbacks
remain active core obligations. File inclusion still needs mutable CWD and
`include_path`, wider failure modes and transformed wrappers. Rocq
interaction-tree semantics and BOLA proofs follow the completed PHP core.

## Validation limits

The reviewed source, paused-state and syntax results are bounded observations, not complete-core acceptance. Interrupted runs, timeouts, Unsupported and budget controls are never native agreements. A fresh offline network-isolated rebuild and full current-source closure are still required. The [migration ledger](coverage/semantics/throwable-migration-review.json) and [artifact guide](docs/ARTIFACTS.md) retain deferred failures and raw evidence locations.
