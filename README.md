# PHP syntax in P4-SpecTec

Compressed historical evidence is stored outside Git; see the
[artifact locations and commit map](docs/ARTIFACTS.md) for lookup and recovery.

This project specifies the abstract syntax of **PHP 8.5.10** and connects
PHP-Parser 5.8.0 to checked P4-SpecTec values. The grammar/scanner inventory
contains 169 constructors. The current [inheritance syntax audit](coverage/semantics/inheritance-review.json)
classified all 30,980 corpus entries and independently bridged 306 exact syntax
inputs to this checkout. Earlier [frontend repair](coverage/frontend-syntax-repair.json)
and [switch syntax](coverage/semantics/switch-review.json) audits remain historical.
The [portability evidence](coverage/portability.json) records an offline rebuild
before these audits; the current syntax gate used copied executables.
Executable core semantics are now being implemented; see the
[plan](PLAN.md), [progress](PROGRESS.md) and [core contract](docs/semantics/CORE.md).
The syntax reports above do not establish semantic coverage. BOLA verification
remains later research.

All required non-system inputs are local and pinned. See
[dependencies/README.md](dependencies/README.md) for prerequisites, provenance,
licenses and offline dependency builds. The PHP source contains matching PHPT
inputs; `corpora/bolaray` contains the pinned application snapshots.

```sh
./scripts/build-deps.sh
./scripts/verify-inputs.py
```

Build the adapter with `make build`. Use `bin/php-syntax check FILE`,
`bin/php-syntax parse FILE` (checked transport), or `bin/php-syntax pretty FILE`.
`--elaborate` additionally checks a typed SpecTec fixture; `--short-tags` enables
short opening tags. Repeat `--ini KEY=VALUE` for source encoding profiles, for
example `--ini zend.multibyte=1 --ini zend.script_encoding=SJIS`.
`print-ast` checks and prints an edited transport file.
[Representation and checking](docs/DESIGN.md) explains the data path.

No application or PHPT helper code is executed to collect syntax. Parsing and
compilation checks are separate; PHP-Parser's version selection is best effort,
so validation compares its raw outcomes with the pinned Zend parser.

`make test` runs extraction, malformed-value, targeted syntax and generated
interaction checks. `make validate` checks all imported source candidates in
four independently checked shards and verifies their complete ordered merge;
`make inventory` regenerates source coverage evidence. See
[validation](docs/VALIDATION.md) for classifications and normalization.

`bin/php-semantics FILE` executes the currently implemented rules through checked
SpecTec values and emits a structured observation. `make test-semantics` runs the
source execution regressions; unfinished behavior returns explicit Unsupported.
Reviewed truth/logical operators and ternary preserve PHP's distinct compiler
and runtime phases; [truth evidence](coverage/semantics/truth-review.json) records
source comparisons, selected-value copying and budget resumption.
[Loose and ordered comparisons](docs/semantics/COMPARISONS.md) now cover scalar
and array values, with [independent evidence](coverage/semantics/comparison-review.json).
[Prefix/postfix increment and decrement](docs/semantics/UPDATES.md) execute for
current scalar/array locations, preserving copied results and diagnostic order;
[independent review](coverage/semantics/incdec-review.json) records the source and resumption gates.
All twelve [compound assignments](docs/semantics/UPDATES.md) preserve captured
targets, delayed reads and alias ownership; [independent evidence](coverage/semantics/compound-review.json)
records 2,639 exact source comparisons and the corrected diagnostic phases.
[Ordinary binary operators and casts](docs/semantics/ORDINARY-OPERATORS.md) now pair
source dispatch with scalar/array conversions, delayed variable reads and concat
compile/runtime diagnostics. The admitted catalog adds 1,506 exact source inputs;
seven preserved request-environment boundaries now have separate explicit-input witnesses.
[Destructuring and retained expression effects](docs/semantics/DESTRUCTURING.md)
now execute current scalar/array list patterns and nonvariable-left coalescing.
[Independent acceptance](coverage/semantics/destructuring-review.json) binds 263
new source cases, effect ordering, aliases and dense resumption.
Object/frame-dependent targets remain unfinished.
[Array unpacking](docs/semantics/ARRAY-UNPACK.md) now preserves key order, copied
values, reference history and compiler/runtime rejection phases. Its
[independent review](coverage/semantics/array-unpack-review.json) audits 155 exact
sources; Traversable objects remain unfinished. Array call arguments are covered by the later call-unpack checkpoint below.
[Ordinary array omissions](docs/semantics/ARRAY-OMISSIONS.md) now retain skipped
slots and exact compiler diagnostic context. Object/frame-dependent destructuring and required
class-constant lookup remain unfinished.
[Foreach syntax and prechecks](docs/semantics/FOREACH-COMPILER.md) preserve reference
and list keys through checked printing and report exact compiler errors;
[independent review](coverage/semantics/foreach-publication-review.json) verifies
the original sources and retired exceptions. [Array foreach execution](docs/semantics/FOREACH-REVIEW.md)
now retains captured values/reference cells, saved copy positions and abrupt-exit
cleanup. [Targeted acceptance](coverage/semantics/foreach-runtime-review.json) binds
155 sources and complementary dense state checks. The historical [full container audit](coverage/semantics/container-campaign-audit.json)
passes 4,997 exact sources and 24 outcome controls; objects, frames and two compiler
contexts remain unfinished.
Current variable/array quiet access, isset/empty, coalescing assignment,
request initialization/GLOBALS and top-level magic constants have a combined
[independent checkpoint](coverage/semantics/quiet-integration-review.json):
5,706 ordinary and 263 explicit-request comparisons, with21 separate outcome
controls on 846/14d17662. All 4,997 historical source bytes and the complete raw
archives are retained. This full runtime checkpoint remains historical after later
call changes and does not close the full-core inventory.
[Named source calls](docs/semantics/SOURCE-CALLS.md) execute declarations,
positional value/reference parameters, recursion, local/global frames, returns
and fatal cleanup. [Reference-parameter acceptance](coverage/semantics/reference-parameter-review.json)
binds 166 exact source replays, 61 independent original agreements, 283 shared
destructuring regressions and eight independent state programs with 1,868 assertions.
[Reference sends and temporary DIM/list behavior](docs/semantics/SOURCE-REFERENCE-PARAMETERS.md)
preserve alias cells, COW, diagnostic phases and checked continuation ownership.
[Ordinary user constants](docs/semantics/SOURCE-USER-CONSTANTS.md) now preserve
ordered activation, namespace/import lookup, initializer diagnostics and array
ownership. [Their independent review](coverage/semantics/user-constant-review.json)
binds source, allocation-class, state/resume and shared quiet/call checks.
[Untyped positional defaults](docs/semantics/SOURCE-POSITIONAL-DEFAULTS.md) now preserve
omitted receives, declaration context, observable caches and fresh reference/array
ownership. [Independent acceptance](coverage/semantics/default-parameter-review.json)
binds exact909 source, protocol, state and production checks.
[Source strict_types declarations](docs/semantics/SOURCE-STRICT-DECLARATIONS.md) now
execute with source-checked unit/function flags; [independent review](coverage/semantics/strict-declaration-review.json)
binds917 source, protocol, cache/resume and complete weak-state bridges.
[Typed positional parameters and value returns](docs/semantics/SOURCE-TYPED-FUNCTIONS.md)
now execute builtin scalar/container checks, sequential receives and uncoerced
default caching while preserving aliases and cleanup. [Independent acceptance](coverage/semantics/typed-function-review.json)
binds926 source/state/protocol gates and the one-test correction bridge.
Remaining callable/type protocols stay pending.
[Call-result reference assignment](docs/semantics/SOURCE-CALL-REFERENCE-ASSIGNMENT.md)
now preserves target aliases, source diagnostic lines and returned-array ownership;
[its review](coverage/semantics/call-reference-review.json) binds933 source/state/protocol
gates, exact926 state bridges and canonical CLI8.
[Source reference returns](docs/semantics/SOURCE-REFERENCE-RETURNS.md) now preserve
caller demand, alias ownership and shared-cell type coercion; [independent review](coverage/semantics/reference-return-review.json)
binds942 source/state/protocol gates and the one-state-test bridge.
[Error suppression](docs/semantics/SOURCE-ERROR-SUPPRESSION.md) now preserves folded
effects, deferred reads and frame-owned masks through cleanup; [review](coverage/semantics/error-suppression-review.json)
binds951 gates and its print-only bridge. Reporting configuration, handlers,
remaining call protocols and full callable integration remain required.
[Parameter phase correction](docs/semantics/PARAMETER-PHASE.md) now sends variadic-default
and void-parameter sources through the existing static compiler; [review](coverage/semantics/parameter-phase-review.json)
binds exact PHPT/CLI diagnostics and reproducible parser patches. Positional
variadic execution is now [independently reviewed](coverage/semantics/variadic-review.json).
[Positional tails](docs/semantics/SOURCE-POSITIONAL-VARIADICS.md) preserve ordered
coercion, reference owners and error traces. [Named user-function arguments](docs/semantics/SOURCE-NAMED-ARGUMENTS.md)
are now [independently reviewed](coverage/semantics/named-review.json), including
hole-default preflight, typed/reference aliases and source-bound SEND lines.
[Builtin named compilation](docs/semantics/BUILTIN-NAMED-COMPILER.md) now has
[independent review](coverage/semantics/builtin-named-review.json) of configured
fixed-name lookup and fetch modes. [Array call arguments](docs/semantics/SOURCE-CALL-UNPACK.md)
now preserve insertion order, named holes and reference owners through errors;
[independent review](coverage/semantics/call-unpack-review.json) binds source/state
checks and complete old-state compatibility. Builtin execution and Traversable
remain required. [Dynamic string user calls](docs/semantics/SOURCE-DYNAMIC-CALLS.md)
now preserve callee selection, reference modes and ownership before argument effects;
[review](coverage/semantics/dynamic-call-review.json) binds990 source/state/protocol
gates and complete old-state bridges. The [earlier integration](coverage/semantics/callable-integration-review.json)
retains5706 ordinary comparisons,263 explicit requests,751 callable rows and5751
compiler phases on981 under distinct profiles. [Named-function statics](docs/semantics/SOURCE-FUNCTION-STATICS.md) now retain
persistent reference cells through recursive initialization, local rebinding and
error cleanup; [review](coverage/semantics/function-statics-review.json) binds
source/state/protocol evidence and22 old-state bridges. [Main-script statics](docs/semantics/SOURCE-MAIN-STATICS.md)
now bind persistent cells through the global symbol table; [review](coverage/semantics/main-statics-review.json)
retains source/state/protocol checks and20 complete old-state responses.
[Real closure instances](docs/semantics/SOURCE-CLOSURES.md) now retain explicit captures,
selected callee owners and per-instance statics through invocation and cleanup.
[Independent review](coverage/semantics/closures-review.json) binds source, object
operation, ownership and compatibility evidence. [Arrow functions](docs/semantics/SOURCE-ARROWS.md)
add implicit undefined snapshots and source-authenticated expression returns; their
[review](coverage/semantics/arrows-review.json) also records the shared suppression
guard correction. Ordinary objects, method/Closure services, cycle collection and
dynamic-source lifetime remain required.
[First-class named function callables](docs/semantics/SOURCE-FIRST-CLASS-CALLABLES.md)
preserve named static roots and existing closure identity through conversion;
[their review](coverage/semantics/first-class-review.json) binds 17 source outcomes
and the separate reference and paused-state gates.
[Pipe arrow grouping](coverage/semantics/pipe-syntax-review.json) survives checked
syntax and printing, so a bare arrow RHS receives the matching compile error
before operand effects. [Pipe execution](docs/semantics/SOURCE-PIPE.md) forces the
left value before selecting a named or closure callable; its
[runtime review](coverage/semantics/pipe-review.json) binds 12 source outcomes
and separate paused-state controls.
[Switch execution](docs/semantics/SOURCE-SWITCH.md) scans cases in source order,
retains the subject through fallthrough, and distinguishes constant-boolean
branching from dynamic equality; its [review](coverage/semantics/switch-review.json)
binds 18 source outcomes and separate compiler and paused-state checks.
[Named empty classes](docs/semantics/SOURCE-CLASSES.md) now support early and
conditional activation, allocate owned objects, and support identity, exact class
types and literal `instanceof`; their [review](coverage/semantics/object-classes-review.json)
binds source and paused-state checks. [Internal `stdClass` identity](docs/semantics/SOURCE-STDCLASS.md)
now allocates an owned empty object with exact nominal typing and ordinary
empty-object behavior; its [review](coverage/semantics/stdclass-review.json)
binds source and ownership checks. [No-constructor allocation arguments](docs/semantics/SOURCE-NOCTOR-ARGS.md)
evaluate positional, named and unpacked values after class lookup while retaining
sent values through the dummy call; their [review](coverage/semantics/noctor-args-review.json)
binds source, compiler and paused-state checks. [Empty-class inheritance](docs/semantics/SOURCE-INHERITANCE.md)
links eligible source and `stdClass` parents at their required publication time;
`instanceof` and class types follow transitive ancestry. Its [review](coverage/semantics/inheritance-review.json)
binds source, compiler, syntax and paused-state checks. Constructors,
other internal-class bodies and method callbacks remain open.
[Public object properties](docs/semantics/SOURCE-PROPERTIES.md) now have typed
and uninitialized slots, source-backed defaults, inherited public overrides,
dynamic names, direct access, live foreach, casts and comparison. The
[property review](coverage/semantics/properties-review.json) binds source,
compiler and paused-task checks. [Public property references](docs/semantics/SOURCE-PROPERTY-REFERENCES.md)
now attach ordered typed sources to shared cells, check writes atomically, and
preserve aliases across unset and object traversal. Their
[review](coverage/semantics/property-references-review.json) records exact source,
compiler and paused-state gates. [Nullsafe property access](docs/semantics/SOURCE-NULLSAFE-PROPERTIES.md)
short-circuits only the active property/dimension chain, skips later names and
keys, and preserves quiet probes and by-reference argument error ordering. Its
[review](coverage/semantics/nullsafe-properties-review.json) binds source,
compiler and paused-state controls. Nullsafe methods, visibility beyond public,
static and readonly members, hooks and magic methods remain open.
[Labels and goto](docs/semantics/SOURCE-GOTO.md) now resolve within each callable,
enter nested branches without evaluating skipped guards, and preserve or release
active loop, foreach and switch owners; their [review](coverage/semantics/goto-review.json)
binds static, source and paused-state checks. Jumps involving `try`/`finally`
remain open.
Historical first-call and full quiet/request campaigns retain their own identities.
[Reference-wrapper history](docs/semantics/REFERENCE-WRAPPERS.md) now preserves
the distinct warnings from intermediate fetching and final dimension mutation;
[independent review](coverage/semantics/reference-wrapper-review.json) retains the
original disagreements and their source-level resolution. Ordinary computed-name
writes preserve existing history without creating a reference;
[corrective review](coverage/semantics/wrapper-dynamic-write-review.json) retains
the later diagnostic regression and resolution.
See [semantic design](docs/semantics/DESIGN.md) and
[numeric reference](docs/semantics/NUMERICS.md) and
[static checks](docs/semantics/STATIC.md) for interfaces and helper checks.
[Source occurrences](docs/semantics/SOURCE-CONTEXT.md) define retained checked
units and structural identities. [Declaration continuation](docs/semantics/LINKING-HANDOFF.md) records the compiler
context and linking work that remains before source activation.
Intentional departures are recorded in [engine discrepancies](docs/semantics/DISCREPANCIES.md).
