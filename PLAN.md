# Implementation plan: executable PHP core semantics

This is a standalone handoff for extending this project from checked PHP syntax
to executable PHP language semantics in P4-SpecTec. It records the agreed scope,
the inspected starting architecture, and the proposed implementation sequence.
A future agent should be able to resume from this file without the conversation
or workspace skills.

**Status at creation:** planning only. No evaluation semantics, arithmetic
model, semantic runner, or differential execution harness has been implemented
by this planning work. Existing syntax validation reports are not evidence of
semantic coverage. The initial deliverable is this plan; its implementation
steps describe subsequent work, not work already performed.

All paths below are relative to the project root containing this file. Commands
are run from that root unless stated otherwise. Proposed files and interfaces
are labeled as proposals; do not mistake them for existing commands.

Implementation is now active. [PROGRESS.md](PROGRESS.md) records current
milestones, assignments and validation evidence; the historical starting status
above is retained to distinguish this plan from implementation results.

## 1. Objective and settled requirements

The eventual objective is **all PHP language core semantics at the project's
pinned target**, excluding ordinary libraries. Build an executable, readable
high-level specification, derive rules primarily from the matching PHP engine,
and validate it through differential execution. This is preparation for a later
interaction-tree semantics and foundational verification, including research on
BOLA bugs. It does not itself state or prove BOLA absence.

The research sequence is PHP core in P4-SpecTec → differential validation → an
interaction-tree semantics in Rocq with renewed differential validation → stating
and proving the selected BOLA absence property in CRIS. The application-security
scope is deliberately the bug classes reported by BolaRay. Library/service models,
authorization policies and reusable BOLA proof techniques are later research;
they must not be inferred from PHP visibility or claimed from evaluator tests.
UrFlow is an optional future conceptual reference for authorization definitions,
not a settled security policy or a dependency of this implementation. Neither
CRIS nor Rocq nor any outside paper/artifact is required to build or run this
P4-SpecTec project.

The following decisions are settled:

1. Target **PHP 8.5.10 CLI, NTS, 64-bit**, matching this project's existing pins.
   Do not substitute a sibling PHP checkout, a system PHP, or a newer release.
2. Keep the **complete existing `vendor/php-src`** and its existing local build.
   The sole differential oracle is the project-local binary built from that
   source, currently `.tools/php/bin/php`. **Do not add an external-oracle path
   or command option.**
3. Preserve self-containment: all non-system source/build/runtime inputs remain
   inside this directory and rebuild offline. The outer `.git` relationship is
   the existing submodule exception. No sibling imports, absolute workspace
   dependencies, escaping symlinks, or implicit package downloads are allowed.
   Documented system prerequisites remain as described in the dependency policy.
4. Cover language constructs and the explicitly identified minimum runtime
   intrinsics/internal-class protocols needed for them. Exclude ordinary
   standard-library and extension functionality. “Implemented in C” or “looks
   like a function call” is not a sufficient exclusion criterion.
5. Represent unsupported functionality explicitly. `Unsupported` is distinct
   from a PHP error, a failed semantic derivation, a runner failure, and a timeout.
   Do not silently execute unsupported operations through Zend or return a stub
   value such as null.
6. The **reference arithmetic model is pure executable `.watsup`**, including
   PHP result typing, conversions, binary64 operations and relevant formatting.
   Do not use Zend evaluation to compute semantic answers. A native acceleration
   path is optional later, only if needed, with explicit equivalence obligations
   and validation against the reference. It is not the initial shortcut.
7. Follow the matching engine's observable behavior primarily, while abstracting
   implementation strategies and optimizations. The engine is not infallible.
   Preserve and investigate discrepancies; any deliberate disagreement needs a
   documented rationale and must not be reported as engine agreement.
8. Retain the existing checked syntax pipeline. A staged implementation is the
   execution strategy, not a permanent replacement of the full-core objective
   with a small subset.
9. Do not push. Preserve unrelated work, make surgical changes, and record
   evidence sufficient for the next agent to continue without guessing.

There is no outstanding required user decision before beginning implementation.
Defining the precise intrinsic list, observation format, and internal module
boundaries is implementation design work within this scope. Record assumptions
and investigate actual ambiguities; do not reopen settled decisions routinely.

## 2. Verified starting point and first reads

Read [README.md](README.md),
[dependency provenance](dependencies/README.md),
[representation](docs/DESIGN.md), and
[syntax validation](docs/VALIDATION.md) before changing the architecture.

The inspected state has these properties:

| Existing component | Verified role and constraint |
| --- | --- |
| `vendor/php-src` | Complete PHP 8.5.10 release, including matching PHPTs and `run-tests.php`; tag commit `34308a6666b2d489c509541ea9befea9e2b42348`. |
| `vendor/p4-spectec` | Pinned framework tree `da36ac3c434cd291940293a63da64544307730a3`, already imported locally with required build dependencies. |
| `vendor/php-parser` | PHP-Parser 5.8.0 with documented local corrections; unchanged upstream evidence is under `vendor/php-parser-source`. |
| `spec/php.watsup` | Generated abstract syntax domains, not an evaluator and not a source-parser generator. |
| `spec/nodes.json`, `spec/schema.json` | Ordered node-field contracts and checked conversion mappings. The syntax inventory currently contains 169 node constructors. |
| `frontend/worker.php`, `frontend/FileLexer.php` | PHP-Parser frontend using native file-mode tokens and source configuration. |
| `native/php_file.c` | Matching Zend file-scanner/parser bridge. It does not compile or evaluate submitted programs. |
| `adapter/main.ml` | Constructs actual `Runtime.Value` objects, checks their structure against elaborated domains, and converts them back. Current operations check/elaborate, not execute. |
| `bin/php-syntax` | Public checked source/AST interfaces; lower-level workers do not replace its checking boundary. |
| `tests/corpus.py` | Syntax-only source discovery/extraction. Its runtime information is intentionally incomplete for semantic testing. |
| `coverage/portability.json` | Existing evidence for an offline copied-path syntax rebuild/validation; not a new audit of future semantics. |

The build script already compiles local PHP and the native bridge. Read
[scripts/build-deps.sh](scripts/build-deps.sh) and
[native/README.md](native/README.md); removing the vendored engine is neither
necessary nor part of this plan.

The frontend and oracle share Zend lexing. Differential execution can validate
independently implemented semantics for the checked parsed AST; it does not
establish independent lexical correctness. Preserve the separate syntax checks
and be explicit about this boundary in reports.

The broader workspace's manuals, engine, and historical KPHP material may be
consulted during research, but they are optional research resources, never
operational prerequisites. Their PHP versions may differ. Incorporate necessary
findings and provenance into local documentation so future agents need no
outside skill or file to understand the implemented contract.

## 3. Evidence discipline

For each feature, trace the matching engine's parser/compiler/runtime path and
identify the smallest high-level rule that preserves its observable effects.
Use manuals, migration notes and historical work as complementary evidence.
Record source symbols and the dependency pin; line numbers alone become stale.

Useful local routes are:

| Question | Start in `vendor/php-src/` |
| --- | --- |
| Accepted source and parser actions | `Zend/zend_language_parser.y`, `Zend/zend_language_scanner.l`, `Zend/zend_ast.c` |
| Static rejection, binding, constant evaluation, sequencing | `Zend/zend_compile.c`, particularly `zend_compile_expr`, `zend_compile_stmt`, declaration/call/assignment lowering |
| Runtime operation behavior | `Zend/zend_vm_def.h` and called helpers; prefer these authored handlers over generated dispatch in `zend_vm_execute.h` |
| Slots/references/typed writes | `Zend/zend_types.h`, `Zend/zend_execute.c`, `Zend/zend_execute.h` |
| Keys, ordered arrays, copying, iteration | `Zend/zend_hash.c`, `Zend/zend_hash.h`, dimension and `FE_RESET_*`/`FE_FETCH_*` handlers |
| Arithmetic, coercion and comparisons | `Zend/zend_operators.c`, `Zend/zend_operators.h`, `Zend/zend_long.h` |
| Numeric text and floating operations | `Zend/zend_strtod.c`, `Zend/zend_float.c`, numeric-string and printing paths in `zend_operators.c` |
| Calls, argument binding, type checks | `Zend/zend_execute_API.c`, `Zend/zend_API.c`, compiler/VM send/receive/call rules |
| Objects and class linking | `Zend/zend_object_handlers.c`, `Zend/zend_objects.c`, `Zend/zend_objects_API.c`, `Zend/zend_inheritance.c` |
| Closures, enums, attributes, suspension | `Zend/zend_closures.c`, `Zend/zend_enum.c`, `Zend/zend_attributes.c`, `Zend/zend_generators.c`, `Zend/zend_fibers.c` |
| Runtime protocols and intrinsic declarations | `Zend/zend_interfaces.stub.php`, `Zend/zend_builtin_functions.stub.php`, and corresponding class stubs/implementations |
| Errors, handlers, cleanup | `Zend/zend.c`, `Zend/zend_exceptions.c`, `Zend/zend_builtin_functions.c`, `Zend/zend_variables.c`, `Zend/zend_gc.c`, `main/main.c` |
| Dynamic source and autoload | VM `INCLUDE_OR_EVAL`, `zend_compile.c`, `zend_execute_API.c`, `ext/spl/php_spl.c` |
| Version changes | `UPGRADING`, `UPGRADING.INTERNALS`, matching regression tests |
| PHPT format and execution profiles | `run-tests.php`, `docs/source/miscellaneous/writing-tests.rst` |

Do not turn opcode specialization, packed-array layout, hash buckets, reference
counts, or JIT machinery into specification structure merely because they appear
in source. Conversely, do not discard an optimization-related detail before
checking whether it affects reads, aliases, conversion order or destructor timing.
Compiler folding and delayed variable reads can matter even with OPcache disabled.

This is a pinned implementation-oriented target, not a claim that every observed
expression order is a portable language guarantee. Keep documented unspecified
behavior and optimizer/platform sensitivities visible in the evidence ledger.

## 4. Full-core inventory and intrinsic boundary

Create a feature/dependency inventory before implementing the first semantic
slice. Proposed location: `coverage/semantics/features.json`. Every syntax
constructor must map to one or more obligations, even if it is metadata-only,
compile-invalid in a particular context, or currently unsupported. Constructor
coverage alone is not enough: many runtime behaviors have no unique AST node.

Inventory at least the following families and their interactions:

| Family | Obligations that must remain visible until resolved |
| --- | --- |
| Source/context | Inline HTML, tags/preamble, source encodings, namespaces, declarations, magic constants, line/file identities, `__halt_compiler` payload/offset behavior |
| Scalars/operators | All literal kinds, unary/binary/compound operations, precedence versus evaluation order, comparison/identity, casts, numeric strings, interpolation, increments/decrements, short circuiting, null coalescing/assignment, ternary, nullsafe access, pipe |
| Variables/storage | Dynamic names, globals/superglobals, `$GLOBALS` restrictions, statics, reads/writes/unset, references and rebinding, temporary lifetimes |
| Containers | Ordered arrays, keys/append history, destructuring/list, unpacking, string offsets, nested writes, copied embedded references, recursion/cycles, all foreach modes and mutation interactions |
| Control | Blocks, conditionals, loops, switch/match, labels/goto restrictions, break/continue levels, return, throw/catch/finally, exit, suspension and termination |
| Functions/callables | Named/conditional declarations, namespaces/imports/fallback, positional/named/unpacked/variadic arguments, by-reference arguments/returns, defaults, strict/weak typing, closures/arrows/capture, first-class callables, static variables, recursion, pipe evaluation |
| Types/static checks | Nullable/union/intersection/DNF forms, scalar and class types, `mixed`/`void`/`never`, variance, context restrictions, compile-time errors versus runtime checks |
| Classes | Declarations/linking, interfaces/traits/adaptations, inheritance/private identities, anonymous/abstract/final classes, object creation/identity/clone, static and instance lookup, late static binding |
| Properties | Typed/uninitialized/readonly properties, dynamic properties, promotion, asymmetric visibility including static properties, hooks, magic access, reference type constraints and indirect writes |
| Modern declarations | Enums/cases/backed values and generated operations; attributes and runtime-relevant builtin attributes; constants, typed class constants, constant-expression evaluation and closures/callables in supported constant contexts |
| Diagnostics/lifecycle | Notices/warnings/deprecations, suppression, error/exception handlers, throwable hierarchy, fatal/compile errors, destructor calls, shutdown, cycles/collection and observable ordering |
| Resumable execution | Generators, `yield`/`yield from`, generator methods/protocol, Fiber operations, cleanup during suspension/resumption/unwinding |
| Dynamic/environmental constructs | `eval`, include/require variants and once state, autoload callbacks, shell-execution syntax and its service dependency, environment initialization and externally supplied values |

Use `spec/schema.json`, the grammar/scanner inventories, and the matching
`UPGRADING` file together. In particular, this target includes pipe, `(void)`,
and modern constant-expression changes. Do not import an 8.6-only feature from
an unrelated source study. Parser-accepted legacy nodes do not imply executable
support; record the target's actual rejection when appropriate.

Maintain a separate explicit intrinsic/protocol catalog, proposed as
`docs/semantics/CORE.md`, with name, purpose, dependency, rules, tests and status.
Begin from language necessity rather than all of Zend's function table:

- `stdClass`, closure identity/invocation and required callable behavior;
- the throwable/error hierarchy and constructors/properties needed to throw,
  catch and observe core exceptions;
- `Traversable`, `Iterator`, `IteratorAggregate`, `ArrayAccess`, `Stringable`
  and their language-triggered dispatch;
- enum-generated operations and generator operations;
- `exit`/`die` and clone behavior, accounting for callable forms at this target;
- Fiber operations and minimal registration/control APIs necessary for core
  error handlers, exception handlers, autoload and shutdown callbacks;
- builtin attributes, constants and declaration metadata that change language
  behavior, rather than treating every attribute as an ignored annotation.

At this pin `exit`/`die` and `clone` have builtin declarations, while Generator
and Fiber behavior is exposed through internal-class methods. They demonstrate
why a blanket exclusion of native functions would erase core language behavior.
Registration APIs can live in a small intrinsic module; their callbacks must
execute the ordinary PHP semantics and can reenter it.

Review borderline facilities explicitly: argument introspection, closure binding,
reflection-created lazy objects, weak references/maps, explicit GC controls,
output-buffer controls, tick registration, stream wrappers, and resource-producing
APIs. Record whether each is necessary core machinery, an excluded ordinary
library, or an environment dependency. An excluded API cannot secretly initialize
semantic state in a test. The behavior of objects that cannot be created under
the accepted environment must not be advertised as validated.

Backticks/shell-execution syntax must stay in the construct inventory even though
its execution reaches a service normally exposed through a library function.
Specify its dispatch and dependency boundary; a missing shell service is visible
as `Unsupported`. Do not implement the ordinary process library incidentally.
Likewise, an include source provider is not an implementation of every PHP stream.

The eventual claim is complete core behavior **under the stated environment and
ordinary-library boundary**, not every extension/SAPI/operating system. A language
construct's dependency must be specified, and its supported environment cases
tested, before marking the construct complete. Boundary classification must not
be used to hide unfinished core rules.

## 5. Integration with checked syntax and static semantics

Preserve the path source bytes → PHP-Parser nodes → OCaml conversion → checked
SpecTec values. Add evaluation after the check; do not replace it by unchecked
JSON traversal or execution of original PHP source in the semantic process.

`spec/php.watsup` is generated by `scripts/generate-schema.py` from the explicit
node contracts. Add authored semantic modules separately, for example under
`spec/semantics/`, with an explicit ordered file list. These proposed names are
organizational suggestions, not existing modules. Ensure syntax-only commands
can still select the syntax declarations and semantic commands include all their
dependencies exactly once.

Keep representation metadata distinct from evaluation context:

- Byte and floating payloads are base64 bytes and hexadecimal binary64 bits;
  decode them into semantic representations without host PHP coercion.
- Original file identity, directory, source positions, declaration context and
  halt offsets can affect execution. Preserve or add explicit checked context
  rather than using pretty-printed source positions or the runner's own path.
- `docs/DESIGN.md` warns that printing can change `__LINE__`, file locations and
  halt offsets. Differential tests use original input bytes and context.
- If metadata needed for execution is absent on an edited AST, require an explicit
  context or return a clear input/unsupported result. Do not invent source facts.
- If transport/schema changes are needed, update generators, membership checking,
  conversion in both directions, reconstruction and relevant tests together.
  Keep existing byte safety, float bits, omitted fields and deep-wire checks.

Add independent PHP static/contextual semantics. Zend parsing, Zend compilation,
the checked syntax domain, and semantic execution are separate boundaries.
Functions/classes/constants may become available at different phases; blanket
hoisting is wrong. Investigate namespace/import resolution, class linking,
constant expressions, invalid lvalues, control-target restrictions and declaration
constraints. Preserve compile-time diagnostics and their timing where observable.

Zend lint/compile observations are test evidence, not an implementation of this
static semantics. Runtime `eval`/include compiles new source within execution;
its errors therefore occur at that point, not necessarily at initial startup.
Introduce a semantic intermediate representation only if it makes these actual
requirements clearer. Avoid reproducing a Zend opcode compiler.

## 6. Proposed execution and state architecture

Recommended architecture: an explicit small-step control machine for stateful,
abrupt and resumable execution, with pure recursive helper relations/functions
where appropriate. This is a design recommendation; its first executable slice
must test binding/representation choices before large-scale rule authoring.

At minimum define these distinct domains:

| Domain | Meaning |
| --- | --- |
| PHP value | Null, booleans, signed-range integers, binary64 floats, byte strings, ordered array values, object identities, and explicitly admitted external values |
| Slot/place | Designation of writable storage, potentially a nested access path with an access mode; not interchangeable with its current value |
| Reference cell | Shared storage for PHP aliases, including type-source constraints when typed properties participate |
| Heap/object state | Object identity, class, distinguishable declaring-class private properties, initialization state and relevant lifetime information |
| Environment/frame | Local/global/static bindings, function/class/namespace context, `$this`, late-static context, argument and return constraints |
| Declaration state | Functions/classes/constants, linking/availability state, included files and persistent per-request statics |
| Control | Continuation frames, pending abrupt completion, loop targets, exception/finally context, iterator/generator/Fiber state |
| Request/environment | Configuration, source-unit map, input values, handler registrations, permitted service responses, output/diagnostic events |

Historical KPHP provides reusable conceptual guidance: separate environments,
heap and control components; distinguish a location/path from a read value; put
lookup/write/copy helpers beneath surface rules; preserve shared alias locations
inside copied arrays. This plan incorporates those principles directly and does
not require its external artifact to build or execute.

Do not copy KPHP's PHP-5 `is_ref`/refcount representation, old array-pointer foreach
rules, unsupported modern features, or approximate builtins. Modern PHP has
reference wrappers with property type sources and append-index history (inspect
`zend_reference` and `zend_array` in `Zend/zend_types.h`). KPHP is architectural
inspiration and a source of test ideas, not the target oracle.

Specific invariants to preserve:

1. Ordinary assignment, assignment through an alias and reference rebinding have
   different effects. By-reference parameter rebinding does not simply redirect
   the caller's variable name. Object identity is distinct from PHP aliasing.
2. Array copying preserves order and embedded references/object identities.
   Append history survives relevant deletion and negative-key cases; it is not
   merely the current maximum key plus one. Iteration has mode-specific state.
3. Missing variables, absent keys, null and uninitialized typed properties remain
   different. Read, write, read-modify-write, `isset`, `unset`, coalescing and
   reference acquisition select different access behavior.
4. Lookup and conversion can invoke PHP callbacks: hooks, magic methods,
   `ArrayAccess`, iterators, string conversion, autoload, errors and destructors.
   Save/restore context and propagate their state and abrupt effects correctly.
5. Evaluate subexpressions and reads at the target's required times. A left AST
   child being compiled first does not prove its variable value is read first.
   Test lvalue designation, RHS side effects and delayed access separately.
6. Make normal, return, break/continue, throw, exit, generator/Fiber suspension
   and runtime-fatal outcomes explicit. `finally` can preserve or replace pending
   completion; exit must not be approximated as an ordinary catchable exception.
7. Logical copying may replace COW, but must preserve lifetime observations.
   Do not erase destructor/GC/shutdown behavior, cycles or weak-reference effects
   included by the core boundary. Model only necessary lifetime facts, then test
   that abstraction against source/probes; raw engine refcounts are not the goal.

The semantic state and observable event trace should be explicit values. An
environment step can request source bytes or a modeled service and resume with
an explicit response. Prefer a deterministic finite source/file environment for
initial include/eval tests, with clear failure responses and provenance.

Dynamic parsing must reuse the checked frontend in the proper mode/context,
including eval's distinction from file parsing. The semantic rules decide scope,
declaration effects, errors and execution. A parser/source service must never
delegate compilation/evaluation answers to Zend. Snapshot included source units
and file identities so both engines consume the same bytes without accidental
reads of unrelated workspace files.

This explicit state/event split is preparation for later interaction trees.
Record internal transitions versus environment observations so a state relation
and trace projection can be formulated later. Testing does not establish that
transfer theorem; do not design an application BOLA policy as part of this step.

## 7. P4-SpecTec runner and execution obligations

The vendored framework already exposes a plausible direct route:

- `vendor/p4-spectec/p4spec/lib/backend-boot/build.ml`:
  `spec_of_mode` compiles specifications and `build_null` constructs a generic
  runner;
- `vendor/p4-spectec/p4spec/lib/runtime/dynamic-runner/signature.ml`:
  `Runner.Interp.eval_rel` and `eval_func` accept `Runtime.Value` inputs;
- `vendor/p4-spectec/p4spec/lib/runner/make.ml` and the same signatures describe
  custom interfaces/externs if explicit source services eventually need them.

The current adapter creates these values but does not execute them. Add a local
runner, reuse the checking boundary, and link the required public libraries
(including `p4spectec.backend_boot` where using that composition). Existing
`adapter/dune` currently links pass/runtime/JSON libraries only. No modification
of vendored P4-SpecTec is known to be necessary for the initial route.

The generic `build_null` composition is a starting point for pure specifications,
not a ready PHP source runner. Stock `p4spectec parse/run/sim` interfaces use P4
adapters. Do not feed PHP into those commands or rebuild the syntax frontend.
The AL/SL meta-interpreters under `vendor/p4-spectec/spec-meta/` are optional
cross-layer checks; direct execution is the practical initial corpus route.

Implement a result-returning wrapper with nonzero exits for tool failures.
At this framework pin some CLI diagnostics can accompany exit code zero; inspect
diagnostics and expected artifacts, or use the Result-returning library APIs.
Validate elaboration, algorithmic binding and structuring before execution.

DSL rules need particular care:

- Declare relation input positions and make each premise executable from values
  already available. Equality can bind/check patterns; it is not equation solving.
- Use recursive state-threading for sequential evaluation. An iterated premise
  over a list with a shared initial state is not a stateful fold.
- Make short-circuit and abrupt propagation cases explicit. Avoid performing
  effects in a failed branch or evaluating an unselected branch.
- Distinguish ordinary relation rejection from interpreter errors and explicit
  PHP outcomes. A supported computation getting stuck is a defect, not a PHP error.
- Rulegroups and `otherwise` affect execution; fallback has binding restrictions.
  Do not use permissive fallback to erase missing semantic cases.
- Start with caches disabled where useful to establish correctness. Hidden host
  state invalidates caching assumptions. Native I/O is not rolled back by rule
  backtracking or determinism checking.
- `-det` checks alternative successful paths encountered on executed inputs;
  it proves neither global determinism, totality nor termination.
- Keep complete step-budget exhaustion separate from PHP nontermination. A
  bounded runner cannot generally decide that a program diverges.

Treat PHP output and diagnostics as semantic events; keep framework debug output
off their channels. If a user diagnostic causes a callback that throws, preserve
that effect instead of merely appending a warning string and continuing.

## 8. Pure reference arithmetic and byte semantics

### 8.1 Expressibility and trusted boundary

Current SpecTec numerics are arbitrary-precision `nat`/`int`, with arithmetic,
comparisons and recursion. See `p4spec/lib/lang/xl/num.ml` and
`examples/fibo.watsup` under `vendor/p4-spectec/`. The available operations are
sufficient in principle to implement machine-range integers and binary64 bit
algorithms. **No fundamental arithmetic expressibility barrier was identified.**
An exact PHP floating model has not yet been implemented or performance-tested.

Do not identify DSL arithmetic with PHP arithmetic. For example, DSL addition
does not promote on signed-64-bit overflow, DSL integer division does not select
PHP integer versus float results, and generic text helpers do not parse PHP
numeric strings. PHP semantics chooses types, conversions, diagnostics and
ordering; mathematical DSL operations implement those choices beneath the rules.

Keep the reference pure and project-local. Binary64 bits can be represented by
a bounded mathematical integer or an explicit sign/exponent/significand value,
with checked encode/decode functions matching the existing literal payload bits.
The exact representation is an implementation choice; test it before proliferating
constructors. Byte strings likewise need a checked semantic representation, not
operations on their base64 transport spelling.

### 8.2 Integer and conversion work

Implement and test these separately:

1. Signed-64-bit range, negation boundaries, arithmetic result typing, overflow
   promotion, division/remainder and shift/bitwise rules. Guard zero divisors and
   invalid operands before invoking partial DSL operations.
2. Overflow follows the source's conversion sequence. For integer addition,
   detect range overflow using mathematical integers, then convert **each input**
   to binary64 and add them as floats, as `fast_long_add_function` does. Rounding
   an exact integer sum once is not automatically equivalent. Check multiplication,
   subtraction and unary operations independently rather than extrapolating.
3. PHP `/`: integer operands with exact divisibility can return an integer;
   nonexact division returns float; a float operand leads to floating division;
   minimum integer divided by `-1` is a special floating case. Division by zero
   raises the modeled PHP exception. Inspect `div_function_base`/`div_function`
   in `Zend/zend_operators.c`.
4. Numeric-string grammar and classification: signs, whitespace, decimal/exponent
   forms, leading numeric data, overflow/underflow, and byte-level termination
   cases. Keep full numeric, leading numeric and nonnumeric classifications apart.
5. Separate arithmetic, explicit-cast, array-key, parameter/return/property-type,
   comparison and output conversions. Preserve weak/strict typing and diagnostics.
6. Integer/string bitwise operations, shift widths/signs, increment/decrement
   behavior, array addition and comparison are PHP dispatch rules, not generic
   mathematical operations on uniformly coerced operands.

Small probes against the pinned local binary have already confirmed these useful
seeds; they are observations to turn into retained tests, not a complete model:

| Input | Observed result |
| --- | --- |
| `PHP_INT_MAX + 1` | float representing `2^63` |
| `6 / 3` | integer `2` |
| `5 / 2` | float `2.5` |
| `6.0 / 3` | float `2.0` |
| `"01" + 1` | integer `2` |
| `(int) "foo"` | integer `0` |
| `"foo" + 1` | `TypeError` |
| Array keys `"01"`, `"1"` | string `"01"`, integer `1` |

### 8.3 Binary64, parsing and formatting work

Define an executable mathematical model with explicit intermediate rounding:

- bit decoding/encoding and classification of normal, subnormal, signed zero,
  infinities and NaNs;
- integer-to-float and relevant float-to-integer conversion, with range and
  diagnostic rules chosen by the PHP operation;
- finite significand/exponent arithmetic, normalization, guard/remainder/sticky
  information and the selected rounding behavior;
- overflow, underflow, signed-zero propagation, special-value comparisons,
  unordered/NaN behavior and PHP strict/loose comparison dispatch;
- floating addition/subtraction/multiplication/division and all remaining core
  numeric operators, including power, with their exceptional/special cases;
- decimal/based-literal and numeric-string conversion into binary64, and output
  conversion with the target's precision/configuration and exponent conventions;
- locale-independent or locale-dependent behavior according to matching source,
  rather than the host parser/formatter's convenient default.

Do not promise all numerical behavior from the phrase “IEEE-754” alone. Audit
the pinned operation and configuration. Power and decimal formatting may need
additional algorithmic work beyond basic binary64 arithmetic, and source use of
host/library routines can make exact edge behavior platform-dependent. Record
the supported platform and observations; determine intended versus incidental
behavior through the discrepancy process rather than silently calling host math.

Avoid relying on a generic bit helper without reading its contract. Some existing
SpecTec native helpers impose width/shift bounds and use host containers. Such
helpers are not PHP shift semantics. Pure recursive mathematical helpers can
avoid inappropriate restrictions; measure their cost on adversarial inputs.

Required tests include boundary integers, operand-conversion versus final-rounding
distinctions, halfway rounding cases, adjacent representable floats, subnormal
boundaries, signed zero, infinities/NaNs, mixed-type divisions, numeric-string
prefixes/suffixes, key collisions and output precision. Test arithmetic both as
pure helper values and through original PHP source/checked AST execution.
Use symbolic/bit expectations where possible so decimal display does not hide a
wrong bit result. On the oracle side prefer core-language distinguishing programs;
if a bit-inspection helper is eventually used, identify it as test instrumentation
with an independently checked contract, not an implicit library implementation.

### 8.4 Optional later acceleration

Only consider native acceleration after the pure model exists and profiling
shows a material need. The framework already has extensible builtin interfaces
(`p4spec/lib/interface/builtin/call.ml`) and custom runner composition, so an
optional local primitive need not require vendored-framework edits.

An accelerated operation must implement the same value/bit contract, preserve
purity, and be validated against the pure reference with boundary/generated cases.
Record platform assumptions and the remaining proof/trust gap. Shared host
floating hardware reduces independence at that layer; calling Zend arithmetic
would make the corresponding differential checks circular and is disallowed.
Keep the pure path available for research, regressions and later formal transfer.

## 9. Observation contract and local differential oracle

Use only `.tools/php/bin/php`, built through the existing dependency scripts.
Resolve the path from the project root, never from `PATH`. Record the binary
hash, source/dependency pin, version, SAPI, integer size, thread-safety setting,
loaded extensions and relevant runtime settings in every authoritative run.

The inspected binary is PHP 8.5.10, CLI, 8-byte integers, NTS. A probe verified
that `-n` loads no php.ini, but **Zend OPcache is still listed by this build**.
Use these explicit baseline arguments:

```sh
.tools/php/bin/php -n -d opcache.enable_cli=0 -d opcache.jit=disable
```

Do not assume `-n` removes all extensions. Extension availability in the oracle
does not imply the spec supports its library calls. Record/fix output precision,
diagnostic settings, timezone/locale/environment and source profiles. The inspected
defaults were `precision=14` and `serialize_precision=-1`; make the chosen baseline
explicit rather than depending on defaults. PHP profile overrides from a reviewed
test must be applied consistently, with optimizer/JIT-specific cases excluded
from the baseline campaign instead of silently changing its target.

A proposed baseline diagnostic profile uses explicit display destination,
`html_errors=0`, `log_errors=0`, and a recorded error-reporting mask. Implement
and verify the exact profile as part of phase 0; keep stdout, stderr, structured
semantic diagnostics and harness output distinct. PHPT cases requiring another
display profile need their own recorded matching profile.

Execute each selected program in a fresh process with a bounded time/resource
budget and a controlled working directory/environment. Supply original bytes,
file identity, arguments, stdin and reviewed companion files consistently to
both engines. Preserve relative paths and `__FILE__`/`__DIR__` meaning. Do not
use pretty-printed source as the oracle input or invoke the oracle from inside
semantic rules. Avoid loading the syntax native bridge into the oracle execution
unless a test explicitly needs it as reviewed instrumentation.

Define a structured run record with at least:

- source/test identifier, byte hash, source context, configuration, environment
  and fixture hashes;
- implementation and binary fingerprints before/after the run, runner mode,
  seed, budgets and selected feature profile;
- frontend outcome, static/compile outcome, semantic outcome, oracle outcome;
- exact stdout/stderr bytes, output/diagnostic event projection, exception/fatal
  information and process exit status under the chosen observation contract;
- modeled external requests/responses and effects where the test includes them;
- comparison result, PHPT expectation result if applicable, and discrepancy or
  exclusion identifier.

Keep these outcomes distinct: normal completion, modeled PHP exception/error,
explicit exit, suspension where exposed by a runner test, static rejection,
`Unsupported`, frontend failure, malformed input, interpreter error/stuck state,
process crash, timeout and resource-budget exhaustion. A PHP fatal is not a
generic tool failure; unsupported/crashed/timed-out runs are never passes.

For values, use core observers such as `echo`, conditionals, `===`, order-sensitive
array iteration and controlled alias/object mutations. These can reveal types,
identity relationships and side effects without modeling `var_dump`. Do not
inject an error handler or generic dumper into every test: callbacks, scope,
destruction and diagnostic presentation can change the behavior being observed.

Normalize only explicitly justified differences, for example a known fixture-root
prefix while retaining file relationships. Never remove all whitespace, erase
warning text indiscriminately, sort array output, or collapse types. Distinguish
stable semantic diagnostic identity/severity from the separately tested renderer.
No normalized comparison should hide an unvalidated renderer or ordering gap.

## 10. PHPT reuse and generated differential tests

Matching PHPTs are already in `vendor/php-src`. Start with reviewed relevant
`Zend/tests` and `tests` cases, but classify dependencies regardless of directory.
Many such tests use library observers or extension APIs; directory membership
and keyword counts are not semantic eligibility or coverage evidence.

Preserve the syntax extractor. It correctly serves syntax-only discovery but
filters INI to syntax settings and does not emit complete runtime expectations.
Use its trusted container/source extraction where suitable and create a separate
semantic manifest, proposed under `tests/semantics/` and `coverage/semantics/`.

For every semantic PHPT candidate retain:

1. Original PHPT path/hash/license provenance and extraction section. Respect
   `FILE`, `FILEEOF`, `FILE_EXTERNAL`, companion-path semantics and source bytes.
2. Original runtime `INI`, `ENV`, `ARGS`, `STDIN`, `EXTENSIONS`, capture/SAPI
   requirements, `EXPECT`/`EXPECTF`/`EXPECTREGEX` and external expectation forms,
   `SKIPIF`, `CLEAN`, redirects, expected-failure markers and other relevant
   sections. Unknown sections must remain visible, not silently discarded.
3. Eligibility decision: required core features/intrinsics, ordinary libraries,
   fixtures, platform/SAPI/extensions, environment services and runner features.
4. A reviewed way to meet each condition, or a precise exclusion reason. Do not
   run arbitrary helpers while discovering eligibility. Initially choose simple
   self-contained cases; subsequently run only reviewed helper logic in controlled
   fixture environments with its effects recorded.
5. Raw oracle result as well as the reference expectation result. Expected-failure
   labels are evidence to inspect, not automatic permission to ignore differences.

`var_dump`, `print_r` and similar ordinary-library observers are excluded by
default. Prefer handwritten core tests and carefully reviewed derived versions
of suitable PHPTs. A derived case must retain its origin hash, exact changes,
reason, and new expectations; do not rewrite the vendored original. Replacing
an observer can change scope, evaluation, callbacks or lifetime, so it requires
review. A separately validated observation adapter is a later explicit design,
not a default exception to the ordinary-library boundary.

The matching `run-tests.php` is the PHPT format authority. Its matcher trims and
normalizes some output and implements formatted/regex expectations. Maintain two
separate comparisons:

- raw semantic-versus-oracle observations under our declared contract;
- conformance of an observation to the PHPT expectation under the pinned matcher.

Both engines matching a broad `EXPECTF` pattern does not establish that they
agree. Test the semantic manifest/matcher itself using controlled format cases,
including external sections, malformed containers and normalization boundaries.
Do not reuse an old KPHP harness or turn regex prefix matches into exact equality.

Add deterministic generated and minimized programs once feature slices work.
Generation must know declarations, types, aliases, access modes, abrupt paths and
the supported intrinsic set; random AST membership alone produces mostly invalid
programs. Also deliberately generate compiler-invalid programs for static checks.
Record seeds, complete input bytes/configuration, shrinking history and the
smallest retained discrepancy. A timeout is bounded inconclusive evidence, not
proof of a loop or an eligible-case exclusion.

Prioritize interaction suites:

- arrays copied with embedded references and object identities;
- by-reference parameter/return rebinding, foreach residual aliases and mutation;
- nested lvalue/RHS side effects and delayed variable reads;
- absent/null/uninitialized accesses under each access mode;
- numeric-string, mixed-type comparison, key conversion and strict-type boundaries;
- callbacks during coercion/property access/iteration and exceptions from them;
- `finally` replacing returns/throws, nested cleanup and destructor effects;
- namespace/declaration availability across dynamic includes and eval;
- generator/Fiber suspension, reentry, exception injection and cleanup;
- property hooks/readonly/type-source constraints through indirect aliases.

BolaRay whole applications remain unsuitable as default core execution tests
because of their libraries and service dependencies. Later extracted language-only
witnesses can be useful if their provenance and changed environment are explicit.

## 11. Discrepancy adjudication

When the spec and oracle disagree, retain raw evidence before editing either:

1. Reproduce with the same original bytes, target binary, profile and fixtures.
   Ensure the implementation did not change during the run.
2. Minimize while preserving the discrepancy. Check frontend/context conversion,
   static phase, observation wrapper/matcher, supported-feature classification,
   primitive model and semantic rule separately.
3. Trace the matching compiler/VM/helper path and nearby regression tests. Use
   documentation/version notes to distinguish intended, historical and incidental
   behavior. Investigate optimizer/platform variation only as a separate campaign.
4. Classify the cause: frontend, static semantics, dynamic semantics, primitive,
   runner/harness, environment mismatch, unsupported dependency, engine candidate,
   documented unspecified behavior, or unresolved.
5. If proposing an engine bug, preserve the minimized reproducer, actual/expected
   results, source reasoning and corroborating evidence. Do not infer a bug merely
   because a simpler spec gives another answer. A suspected bug is not confirmed
   by this project's disagreement alone.
6. For a deliberate specification departure, record the chosen behavior, scope,
   rationale and reviewed disposition. Preserve the oracle mismatch in results;
   do not count it as exact agreement or broadly suppress nearby failures.

Proposed ledger: `tests/semantics/discrepancies.json`, with a local human-readable
explanation for nontrivial cases. Reports should distinguish exact matches,
documented divergences and unresolved issues. An engine-bug report can be prepared
as an artifact; this plan does not authorize sending messages or filing external
reports on the user's behalf.

## 12. Phased implementation with exit criteria

Each phase produces finite artifacts and tests. Maintain the whole feature
inventory throughout; do not label the project complete at an early phase.
Cross-cutting static checks, errors, effects and regression tests accompany every
new construct rather than being postponed wholesale to the last phase.

### Phase 0 — contracts, inventory and execution skeleton

Deliver:

- explicit target/configuration/observation/core catalogs and dependency inventory;
- result/outcome types and a local semantic runner over checked AST values;
- separate authored semantic files with compilation-stage checks;
- local-oracle driver and structured run records using original source context;
- one complete constant/scalar/echo program and one intentional PHP error or
  static rejection, plus an explicit unsupported case and runner-failure test.

Exit when source → checked AST → `.watsup` execution → observation comparison
works using only local inputs, unsupported/tool failures cannot pass, and the
existing syntax checks remain intact. Verify the actual direct-runner APIs and
result handling here; the feasibility study did not prototype this integration.

### Phase 1 — pure values, bytes, numeric primitives and conversions

Deliver the integer, byte, binary64 and numeric-text reference modules described
in section 8, with incremental vertical source tests. Keep PHP dispatch and
mathematical helpers separate. Resolve operation-specific rounding, power,
parsing and formatting contracts rather than leaving opaque extern declarations.

Exit when all numeric/operator obligations in the phase inventory have explicit
rules and targeted/generated boundary evidence, intermediate rounding is tested,
and no Zend/host PHP evaluator supplies primitive answers. Record performance and
unresolved numerical/platform cases honestly; do not mark partial float support
as complete arithmetic. Subsequent independent state work may proceed in parallel
with unfinished numerical subfamilies if their dependency limitations are recorded.

### Phase 2 — storage, arrays, access modes and expression sequencing

Deliver environment/slot/reference/object-identity foundations; ordinary and
reference assignment; arrays/keys/append/copy; string offsets; destructuring and
unpacking; variable/global/static rules required by the supported contexts;
short-circuit and access-mode expression rules.

Exit when alias topology, copied embedded references, append history, missing/null
behavior and state/abrupt propagation pass discriminating interaction tests.
Track object-protocol access as a dependency until phase 4 completes it.

### Phase 3 — control, functions, binding and static semantics

Deliver loops/switch/match/goto restrictions; returns/break/continue; functions,
arguments/types/references, closures/arrows/callables/pipe; namespaces/imports and
declaration availability; relevant constant evaluation; exceptions, handlers and
`finally` with explicit unwinding.

Exit when valid and compile-invalid cases are distinguished independently of
Zend's compiler, call frames preserve scope/alias/type semantics, and nested
stateful control/exception interactions pass. Add error-handler registration only
through the cataloged intrinsic contract, not hidden harness initialization.

### Phase 4 — class system, properties and runtime protocols

Deliver class linking/inheritance/interfaces/traits/visibility; object lifecycle
basics and clone; type constraints/variance; modern properties/hooks/readonly/
asymmetric access; magic methods; enum/attribute/constant behavior; necessary
internal-class protocols and callable intrinsics.

Exit when callbacks use ordinary execution with correct context and reentry,
private property identities/type sources cannot be bypassed through aliases,
and protocol-triggered abrupt effects and static rejection cases pass. Keep any
reflection/lazy/weak-reference boundary decisions explicit in the catalog.

### Phase 5 — dynamic source, resumable execution and lifecycle closure

Deliver eval/include/require/once with checked source services and contexts;
autoload registration/dispatch; generators/yield-from/Fibers; shutdown and
observable destructor/collection behavior; remaining required intrinsic and
environment-boundary contracts, including dispatch from shell-execution syntax.

Exit when suspension/resumption/unwinding, dynamic declarations, included-file
scope/identity and cleanup interactions have source-backed rules and tests.
No opaque fallback may invoke Zend evaluation. Environmental exclusions must
state their contract and cannot stand in for unfinished core control behavior.

### Phase 6 — coverage closure, differential campaigns and portability

Deliver a complete audited feature/dependency matrix; broad reviewed PHPT and
generated campaigns; rule/branch/interaction coverage; minimized discrepancy
ledger; performance/resource characterization; documentation and final offline
copied-path evidence for the actual implementation.

Exit only when every in-scope core obligation is implemented and validated or
has a specifically documented intentional engine divergence. No unresolved
unsupported **core** construct, stuck supported computation, unexplained mismatch
or untested operational dependency may be hidden by a “complete” label. Ordinary
library/environment exclusions remain visible and separately counted.

Passing selected tests or exercising every rule is evidence, not proof of
equivalence with Zend. Describe the achieved scope, profile, corpus and remaining
foundational work precisely.

## 13. Existing validation and self-containment obligations

Use the existing local build path; do not introduce package-manager resolution
outside the vendored closure. When tools are absent, the documented bootstrap is:

```sh
./scripts/build-deps.sh
./scripts/verify-inputs.py
make build
```

Choose checks appropriate to changes:

- Every semantic change: relevant elaboration/algorithmic/structuring checks,
  focused execution/differential tests, and explicit negative/failure outcomes.
- Adapter/frontend/schema changes: checked round trips, malformed-value/deep-wire
  checks, targeted original-versus-printed observations, and `make test` as
  appropriate. Update generation sources and regenerate instead of hand-editing
  generated schemas.
- Syntax acceptance/printing/configuration changes: required full classified
  syntax validation (`make validate`) and inventory updates (`make inventory`)
  when affected. Preserve extraction provenance and exact discrepancy ledgers.
- Dependency/build/path changes and final semantics portability: extend and run
  `scripts/portable-check.sh` so the new semantic build/tests run from a fresh
  copied path without workspace/network access. Keep the existing system
  prerequisites and local source/license provenance explicit.

Read `scripts/portable-check.sh` before extending it. Its existing audit uses
Linux namespace/isolation facilities and preserves logs; it is not a generic
unit test. A passing pre-semantics portability report cannot validate newly added
files, subprocesses, services or absolute-path assumptions.

If vendored sources genuinely need changes, follow existing reproducible patch
and import-provenance practices; inspect `patches/README.md` and
`dependencies/README.md`. No vendored framework modification is currently known
to be necessary just to express PHP arithmetic or accept checked AST execution.

## 14. Handoff, progress and evidence

### Collaboration workflow

The user's preferred workflow is orchestration by the primary agent. Keep that
agent focused on scope, coordination, evidence review and context management;
delegate token-heavy source study and bounded implementation/review tasks to
subagents. Do not have the primary agent duplicate the same codebase study.

Give each task a concrete deliverable, applicable requirements, relevant local
entrypoints, allowed mutations, verification obligations and explicit file
ownership. Parallelize independent work; serialize changes to shared schemas,
runner interfaces, catalogs and reports. Agents share the filesystem: do not
let parallel assignments edit the same file without an explicit handoff.

Require compact progress checkpoints and final handoffs naming findings, changed
files, evidence paths/source symbols, checks and unresolved dependencies. Keep
the feature matrix authoritative across agents. Review integration against the
settled requirements and run the relevant combined checks before declaring a
phase complete. Preserve the user's current authorization scope: a read-only
study remains read-only, and a plan-only task changes only the plan. This section
does not require spawning extra agents to finish this planning deliverable.

### Persistent artifacts

Recommended local artifacts, to create only as their implementation work begins:

| Proposed artifact | Required content |
| --- | --- |
| `docs/semantics/CORE.md` | Target/profile, core/intrinsic/environment boundary, observation contract, justified exclusions |
| `docs/semantics/DESIGN.md` | Chosen state/control/numeric representations, invariants, source routes and abstraction arguments |
| `coverage/semantics/features.json` | Every constructor/runtime obligation, dependencies, implementation/tests/status, remaining work |
| `tests/semantics/` | Authored and derived cases, generation/minimization/matcher tests and provenance |
| `tests/semantics/discrepancies.json` | Exact cases/configurations, cause, evidence, disposition and unresolved questions |
| `coverage/semantics/` | Fingerprinted run manifests, classified results, coverage and portability evidence |

Keep this plan's status section or a clearly linked local progress file current.
For each completed increment record:

1. Implemented behavior and relevant source symbols/pins.
2. Changed files and chosen representation/invariant decisions.
3. Exact checks run, profiles/seeds/corpus selection, outcomes and report paths.
4. Remaining dependencies, open discrepancies and the next concrete task.

Reports must name partial selections and interrupted runs honestly. Fingerprint
implementation/tests/oracle before and after long campaigns; invalidate a run
whose inputs changed. When sharding, verify complete exact membership and a stable
merge rather than adding unrelated counts. Do not reuse stale reports as current
evidence or count unsupported/timeout cases as successfully validated semantics.

Outstanding technical work is substantial: the direct semantic runner has not
been prototyped here, the pure numeric model's performance is unknown, the full
intrinsic catalog needs source review, and lifecycle/dynamic-source observation
details must be settled through implementation evidence. These are visible design
and validation tasks within the agreed direction, not reasons to abandon the
full-core objective or introduce an external oracle/native arithmetic shortcut.
