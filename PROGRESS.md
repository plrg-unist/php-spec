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

The current reviewed cohort covers bounded direct quiet stdClass ARRAY fields,
fully qualified Boolean defaults, nonnull FLOAT coalesce bases and certified
zero/FIELD2 defaults. Each family retains its original source, state, failure
and production-load cuts; complete PHP core remains unfinished:

- [Direct quiet stdClass ARRAY fields](coverage/semantics/string-offset-nested-unset-bool-cv-object-array-fields-post-review.json).
- [Fully qualified Boolean defaults](coverage/semantics/supplied-optional-fqn-bool-default-producer-reference-notice-review.json).
- [Nonnull FLOAT coalesce bases](coverage/semantics/string-offset-runtime-allocated-float-coalesce-tree-rhs-concat-base-initial-raw-leading-key-review.json).
- [Certified zero/FIELD2 defaults](coverage/semantics/deferred-float-number-tree-zero-full-ternary-redirect-wrapper-default-reception-review.json).

Direct dynamic array fields across nested-unset Warnings preserve COW, shared
references and staged retirement in the bounded quiet stdClass domain. Two native
originals ran once; a public normal comparison and a pending direct-source budget
bridge retain separate agreement cuts. All ten bounded checks passed and reaped;
original timeouts and fixture failures keep zero credit. Actual `6a3096be1` and its
sole SL509 load are independently clear from one saved cache. Wider fields and
lifetimes remain partial. The [family review](coverage/semantics/string-offset-nested-unset-bool-cv-object-array-fields-post-review.json)
and [artifact index](docs/ARTIFACTS.md) retain exact limits, failures and recovery.

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
| References | `recover46_reference_fqn_defaults_impl` / `recover47_reference_defaults_review` | FQN Boolean defaults (REF144): integrated and independently reviewed; supplied string defaults (REF145): native4 once and Unsupported baseline retained. |
| Compiler | `recover39_compiler_mixed_impl` / `recover38_compiler_dnf_review` | Scoped-self DNF (COMP347): author checks passed; independent validation remains in progress. |
| Quiet reference Get | `recover35_get_multiply_impl` / `recover33_get_multiply_review` | Multiplication: source comparisons passed; the overflow Unsupported control timeout is unresolved and carries zero credit. |
| String fields | `recover48_string_alias_array_impl` / `recover51_string_array_review` | Array-valued ALIAS properties: source-first scope assessment; new validation unrun. |
| Allocated string bases | `recover63_dynamic_coalesce_impl` / `recover52_dynamic_arith_review` | Nonnull FLOAT coalesce bases integrated and reviewed; full-ternary source witnesses reserved. |
| Enum/default reception | `recover41_enum_zero_impl` / `recover34_enum_zero_review` | Zero/FIELD2 defaults (319) are integrated and independently reviewed; wider defaults and lifetimes remain partial. |
| Output | `recover45_output_byte_impl` / `recover40_output_folded_review` | Emitted single-byte bitwise NOT in handler returns (160): saved source evidence accepted; state fixtures and WHOLE remain. |

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
