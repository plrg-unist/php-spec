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

## Subsequent reviewed increments

| Modules | Behavior and evidence |
| --- | --- |
| 119/120 | First-class named-function callables: 17 source outcomes, reference-context pairs and paused guards. [Review](coverage/semantics/first-class-review.json) |
| 121–123 | Pipe arrow syntax and execution: separately reviewed 30,980-entry classified syntax gate, 12 runtime source outcomes and five paused stages/89 assertions. [Syntax](coverage/semantics/pipe-syntax-review.json) · [runtime](coverage/semantics/pipe-review.json) |
| 124/125 | Switch ordering, fallthrough and saved subject ownership: 18 source outcomes, six paused stages/85 assertions and separately reviewed classified syntax gate. Constant-boolean branching uses an authenticated compiler fact. [Review](coverage/semantics/switch-review.json) |
| 126/127 | Named empty classes: early/conditional publication, owned instances, exact nominal types and literal `instanceof`; 31 source outcomes and paused guards. Pinned `-n` catalogue reserves 166 internal names. [Review](coverage/semantics/object-classes-review.json) |
| 128/129 | Callable-local labels/goto: source-derived targets and loop/foreach/switch owner transfer; static, source and paused guards. [Review](coverage/semantics/goto-review.json) |
| 130 | Internal `stdClass` identity, empty casts and nominal consumers: 17 source outcomes and paused ownership guards. [Review](coverage/semantics/stdclass-review.json) |
| 131/132 | No-constructor arguments for admitted empty classes and `stdClass`: 18 source outcomes, 59 compiler assertions and 77 maintained paused assertions. [Review](coverage/semantics/noctor-args-review.json) |
| 133/134 | Empty-class inheritance, early/deferred links and transitive nominal types: 33 source outcomes, 81 compiler assertions, 32 graph assertions and one classified syntax gate. [Review](coverage/semantics/inheritance-review.json) |
| 135/136 | Public instance properties: typed/default/uninitialized slots, invariant inherited overrides, dynamic and computed names, live foreach, casts and comparison; 31 source outcomes, 146 compiler and 58 paused-task assertions. [Review](coverage/semantics/properties-review.json) |
| 137/138 | Public property references: ordered typed sources, atomic constrained writes, by-reference calls/returns and object traversal, typed overflow; 52 admitted source outcomes and paused ownership guards. Three originals were excluded then; 139/140 closes the nullsafe send dependency. [Review](coverage/semantics/property-references-review.json) |
| 139/140 | Nullsafe property and active property/dimension chains: 21 exact source outcomes, 15 compiler sources/63 assertions, and paused source/owner guards. [Review](coverage/semantics/nullsafe-properties-review.json) |
| 141/142 | Public instance methods and constructors: inherited dispatch/signatures, lexical and called scope, bound closures, ordinary/nullsafe argument protocols and authentic Closure invocation trampolines. [Review](coverage/semantics/methods-review.json) |
| 143/144 | Match expressions: strict lazy selection, delayed CV subjects, compiler priority, owned results and unhandled diagnostics; 88 source outcomes, 13 compiler sources/67 assertions and paused ownership checks. [Review](coverage/semantics/match-review.json) |
| 145/146 | Print constant-result effects, conversion lines, reference demand and paused ownership. [Review](coverage/semantics/print-review.json) |
| 147/148 | Exit/die intrinsic calls, ordered binding, conversion, internal traces and explicit terminal cleanup; 87 source tuples, 25 compiler sources/133 projections and paused ownership guards. [Review](coverage/semantics/exit-review.json) |
| 149/150 | Object and closure cloning: shallow slots/live aliases, receiver/static ownership and positional/named/array-unpacked property updates. [Review](coverage/semantics/clone-review.json) |
| 151/152 | Generated builtin Throwable identities, ordered no-finally try/catch, strict catch references, throw/rethrow, source-authenticated search and owned traces. [Contract](docs/semantics/THROWABLES.md) · [review](coverage/semantics/throwable-review.json) |
| 153/154 protected | Protected instance properties: lexical prototype access, mangled keys across existing consumers, typed binding correction and memoized property coalescing. The protected foundation is retained as a separate reviewed increment. [Review](coverage/semantics/property-visibility-review.json) |
| 153/154 private | Independent declaring-class slots, lexical ancestor selection and inherited-private dynamic fallback across existing consumers; typed-reference location rules now distinguish aliased slots. [Review](coverage/semantics/property-private-review.json) |
| 155/156 A | Normal/throw finally, previous chains, suppression and exit: 19 source tuples, 11 compiler sources and six paused stages/103 assertions. [Stage A ledger](coverage/semantics/finally-author.json) |
| 155/156 B | Value/reference return, loop/switch/foreach jumps and goto across finally: 20 additional source tuples, six transfer controls and ten transfer paused stages. A focused repair disambiguates goto entry into try/catch with and without finally and authenticates the rebuilt region across saved calls. [Contract](docs/semantics/SOURCE-FINALLY.md) · [Stage B ledger](coverage/semantics/finally-stage-b-author.json) · [repair ledger](coverage/semantics/finally-goto-repair.json) |

The current integration combines protected properties, public methods and
constructors, cloning, nullsafe chains, match, print and exit/die with generated
Throwable control and reviewed Stage B finally transfers. Source, paused-state and terminal migration evidence have
bounded review. The [migration ledger](coverage/semantics/throwable-migration-review.json)
keeps deferred broader pause sweeps and baseline fixture failures explicit;
these results do not establish complete-core regression closure.

The [checked eval parser transport](docs/semantics/DYNAMIC-SOURCE-SERVICE.md)
is a syntax-service increment only. Eleven focused eval-source cases and eleven
protocol negatives pass; the separate 30,980-entry classified gate checks
existing file syntax on the same frontend/adapter commit. Its
[provenance ledger](coverage/dynamic-eval-helper-review.json) records the frozen
inputs, inventory results and a pre-existing grammar-mapping sync obligation.
Reached eval/include still returns `Unsupported`; native parse-only diagnostics,
authored `ParseError` handling and stateful source continuation are the next
steps.

## Next work

Throwable constructors, accessors, canonical internal property backing, structured
trace payloads and user subclasses follow. Constructor-created previous cycles
need separate handling beyond stage A generated-only acyclicity. Nonpublic/static methods,
static/readonly members, hooks, magic methods, remaining internal parents,
conversion callbacks, output handlers, traversal and lifecycle integration remain
open. Exit bypasses catch/finally; shutdown/destructor callbacks remain required.
Full current-source closure and a fresh offline network-isolated rebuild are
required before complete-core acceptance. Rocq interaction-tree semantics and
BOLA proofs remain downstream.
