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
| 137/138 | Public property references: ordered typed sources, atomic constrained writes, by-reference calls/returns and object traversal, typed overflow; 52 admitted source outcomes and paused ownership guards. Three retained originals remain explicit dependencies. [Review](coverage/semantics/property-references-review.json) |

The current property-reference checkpoint keeps source-authenticated access
separate from mutable cell contents. A failed type check or integer overflow
preserves the prior value and owner graph; resumed tasks revalidate source and
captured operands. The 137/138 review binds the exact source and paused-state
profiles. It does not close nullsafe reference sends or property visibility,
static and readonly members, hooks, magic access and methods.

## Next work

Nullsafe property evaluation and reference-send priorities, property
visibility, static and readonly members, hooks, methods, constructors, remaining
internal parents and Throwable follow. `try`/`finally` goto
interaction, match, remaining intrinsics, traversal, dynamic lifetime and
collection obligations remain open. Full current-source closure and a fresh
offline network-isolated rebuild are required before complete-core acceptance.
Rocq interaction-tree semantics and BOLA proofs remain downstream.
