# Core PHP semantics progress

The target is **PHP 8.5.10 CLI, NTS, 64-bit**. Executable core semantics and
source-driven differential validation are active; complete PHP core, the later
Rocq interaction-tree model and BOLA/CRIS verification remain unfinished.
[PLAN](PLAN.md) defines settled scope and phase exit criteria.

## Current checkpoint

The [inventory](coverage/semantics/features.json) contains **169 constructors**
(162 partial, 7 pending) and **306 runtime obligations** (281 partial,
24 pending, 1 validated). Validated closure remains **0 constructors / 1 runtime
obligation**. No bounded family result closes the remaining core work.

The current reviewed cohort adds raw-FLOAT shorthand allocation bases, supplied
unary INT defaults for FLOAT formals, exact integer Divide/Modulo certificates
and emitted single-byte STRING bitwise return values. Complete core remains
unfinished; each family retains its source, state and failure cuts.

Two-child raw-FLOAT shorthands extend the one-row RHS CASTSTRING/CONCAT guard while retaining exact typed values, source/CODE, captured precision and full-state registry proofs. The [shorthand review](coverage/semantics/string-offset-runtime-allocated-float-shorthand-tree-rhs-concat-base-initial-raw-leading-key-review.json) keeps native2 once/source2, state and affected-control cuts separate; wider producers and lifetimes remain partial.

Supplied optional plain FLOAT formals preserve one signed INT default, its
whole checked AST and both metadata layers, with signed64 bounds on leaf and
effective value. Caller copies and private reference-cell ownership remain
distinct; see the [review](coverage/semantics/supplied-optional-unary-float-int-default-producer-reference-notice-review.json).

Quiet Divide requires an exact fitting integer quotient; Modulo preserves the
dividend sign, including MIN%-1=0. Both operand certificates remain required.
The [review](coverage/semantics/magic-property-methodclosure-static-raw-divide-modulo-operand-condition-typed-ternary-left-coalesce-quiet-get-review.json) keeps FLOAT controls and original resource exclusions separate.

Emitted STRING AND/OR/XOR handler returns require both input lengths to equal
one and preserve exact string storage, including derived NUL. Unequal or wider
allocations remain partial; see the [review](coverage/semantics/output-final-selected-emitted-byte-bitwise-cast-chain-return-modulo-error-review.json).

Shorthand, FLOAT-formal defaults and Divide/Modulo share one fixed production
SL509 load; output returns retain their separate fixed load. Metadata renews no
execution or native observation. Wider producers, types, owners and lifetimes
remain partial, and historical controls and failures retain their original credit.

## Integrated behavior and entrypoints

The checked path is original source → parsed nodes → checked SpecTec values →
authored semantics → structured events/completion. Syntax reconstruction remains
separate from original-source differential execution. Runtime modules are listed
once in `spec/semantics/modules.json`; current production loading uses 509 modules.

| Family | Maintained contract and remaining boundary |
| --- | --- |
| Source and compilation | [Source context](docs/semantics/SOURCE-CONTEXT.md), [linking](docs/semantics/LINKING-HANDOFF.md); wider acquisition and static contexts remain partial. |
| Values and operators | [Numerics](docs/semantics/NUMERICS.md), [comparisons](docs/semantics/COMPARISONS.md), [dimensions](docs/semantics/DIMENSIONS.md); producer/coercion/diagnostic interactions remain partial. |
| Arrays and references | [Reference wrappers](docs/semantics/REFERENCE-WRAPPERS.md), [array unpack](docs/semantics/ARRAY-UNPACK.md); wider graphs, COW and callback lifetimes remain partial. |
| Calls and declarations | [Source calls](docs/semantics/SOURCE-CALLS.md), [first-class callables](docs/semantics/SOURCE-FIRST-CLASS-CALLABLES.md); wider signatures, defaults and reentry remain partial. |
| Classes and properties | [Classes](docs/semantics/SOURCE-CLASSES.md), [properties](docs/semantics/SOURCE-PROPERTIES.md), [property references](docs/semantics/SOURCE-PROPERTY-REFERENCES.md); wider owners, linking, hooks and typed aliases remain partial. |
| Suspension | [Generators](docs/semantics/GENERATORS.md), [Fibers](docs/semantics/FIBERS.md); wider producers, delegation and teardown remain partial. |
| Lifecycle | [Eager destructors](docs/semantics/SOURCE-EAGER-DESTRUCTORS.md), [weak references](docs/semantics/WEAK-REFERENCES.md), [cycle collection](docs/semantics/CYCLE-COLLECTION.md); wider physical cleanup remains partial. |
| Diagnostics and environment | [Error handlers](docs/semantics/SOURCE-ERROR-HANDLERS.md), [output buffers](docs/semantics/OUTPUT-BUFFERS.md), [request inputs](docs/semantics/REQUEST-INPUTS.md); OB31 and wider buffering/shutdown/tick behavior remain partial. |

Build, public CLI and test entrypoints are in [README](README.md).
[CORE](docs/semantics/CORE.md) defines the intrinsic/environment boundary.
The project-local oracle supplies observations only; PHP evaluation, numeric
answers and dynamic compilation belong in authored `.watsup` rules. Unsupported
core dependencies stay explicit.

## Active work

The integration checkout has one writer. Implementation/review pairs retain their
active private trees and serialize their own heavy jobs. Genuine source readiness
requires all planned affected checks and WHOLE review to finish and reap. The
current lanes below remain bounded parts of unfinished families:

| Lane | Author / reviewer | Current work |
| --- | --- | --- |
| References | `recover47_reference_float_defaults_impl` / `recover48_reference_unary_defaults_review` | Unary INT defaults for plain FLOAT formals (REF147): integrated and independently reviewed; unary FLOAT literal defaults (REF148) are under independent review. Wider defaults, types and lifetimes remain partial. |
| Compiler | `recover40_compiler_intersection_impl` / `recover41_compiler_parent_review` | Scoped-self intersection conjuncts (COMP348) are integrated and independently reviewed; [family review](coverage/semantics/self-intersection-parentless-short-reference-get-hook-review.json). Named empty-parent self Get is in source-first validation; wider owners and lifetimes remain partial. |
| Quiet reference Get | `recover37_get_shift_impl` / `recover34_get_divmod_review` | Exact integer division and modulo integrated at `6c21ac59`; [review](coverage/semantics/magic-property-methodclosure-static-raw-divide-modulo-operand-condition-typed-ternary-left-coalesce-quiet-get-review.json) keeps source, FLOAT controls and resource cuts separate. Integer shift selectors are in source-first preparation; wider operators and lifetimes remain partial. |
| String fields | `recover48_string_alias_array_impl` / `recover51_string_array_review` | Array-valued ALIAS properties integrated at `97fb19a42` and independently reviewed; [family review](coverage/semantics/string-offset-nested-unset-bool-cv-object-array-alias-fields-post-review.json). Object-valued aliases, object-bearing/cyclic arrays and wider fields/lifetimes remain partial. |
| Allocated string bases | `recover65_dynamic_castfloat_impl` / `recover55_dynamic_castfloat_review` | [Raw-FLOAT shorthand bases](coverage/semantics/string-offset-runtime-allocated-float-shorthand-tree-rhs-concat-base-initial-raw-leading-key-review.json) integrated and reviewed; numeric-STRING FLOAT-cast source-first facts retained. |
| Enum/default reception | `recover42_enum_zero_impl` / `recover34_enum_zero_review` | Literal FLOAT sign-chain zero/FIELD2 defaults (321) are integrated and independently reviewed; wider defaults and lifetimes remain partial. |
| Output | `recover46_output_bitwise_impl` / `recover41_output_bitwise_review` | Emitted single-byte STRING AND/OR/XOR in handler returns (161): integrated and independently reviewed; [evidence](coverage/semantics/output-final-selected-emitted-byte-bitwise-cast-chain-return-modulo-error-review.json). Both operands must have length one; wider allocation and lifetime cases remain partial. |

Shared metadata belongs to the integrator: README, this checkpoint, the feature
inventory and ARTIFACTS. Authors supply bounded family records and literal/keyed
operations. Replace superseded checkpoint prose; keep detailed milestone counts,
commands, hashes and original failures in existing family records and the artifact
index. Metadata-only changes do not trigger semantic or native reruns.

## Held boundaries

V110, GC35, I106 and COMP123 remain held. ATTR87 and GC87 remain stopped; retain
their private drafts and raw evidence without restarting or rerouting those lanes.
I140 and GC84 remain unstarted pending exact user scope. The existing reserve
`93807cdd6` / `255` remains unchanged.

Do not resume or broaden these paused boundaries through neighboring work:

- OP12 increment/decrement dimension warnings.
- Source47 low-precision DEFINE-name NaN conversion.
- Owned-NUL source-release behavior.
- Undefined by-reference LIST key handling.
- COMP88 Stringable supplied-throw crash.

## Remaining core work

Finish the inventory obligations across source constructors and runtime
dependencies, including wider coercion/read/cast consumers; callable signatures,
reference parameters/returns and delayed reads; array/object/reference ownership,
COW and callback lifetimes; class/trait/enum/attribute/hook/readonly contexts;
Generator/Fiber suspension and cleanup; physical collection and weak protocols;
Traversable producers; dynamic compilation; startup/configuration and explicit
environment providers. Ordinary libraries and services remain a separate boundary,
not a way to hide required core behavior.

Final combined current-source validation and a fresh copied-path,
network-isolated offline rebuild are still required. Local tool reuse and
historical portability evidence do not establish that rebuild. Interaction trees
in Rocq and selected BOLA/CRIS proofs follow completed PHP core and renewed
differential validation.

## Validation and evidence

Preserve original source bytes/path/cwd, native profile, raw streams/status,
semantic completion, tested revision, compiler/runtime identities and commands.
Ordinary, explicit-request and callable profiles retain separate contracts.
Source agreement, state fixtures, static rejection and budget controls retain
separate counts. Interrupted, timed-out, Unsupported, malformed and stuck runs
never become semantic agreement credit.

Independent review addresses semantic correctness and test reliability. Fix
actual discrepancies narrowly and rerun affected checks only; pointwise disjoint
composition and metadata changes do not renew accepted campaigns. Large originals
and raw failures stay outside Git. [ARTIFACTS](docs/ARTIFACTS.md), existing family
ledgers and [MILESTONE-HISTORY](MILESTONE-HISTORY.md) retain historical lookup;
this file records current behavior, custody, open work and exact holds.
