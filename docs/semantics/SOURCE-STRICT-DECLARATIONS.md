# Source strict_types declarations

This prerequisite admits checked `declare(strict_types=0|1);` declarations without a body and records lexical strictness in unit and function CODE. It preserves existing untyped calls, defaults, references and ownership. Typed parameter/return admission follows separately; other declare directives and registered builtin bodies remain explicit later core dependencies.

Compiler92 uses the existing parser-literal and lexical environment machinery. Source placement is checked against the original top-level statement list. Earlier Nop or Declare statements are allowed; nested strict declarations and block form fail. Declaration names are case-insensitive, values must be integer zero or one, and setting one is sticky across subsequent zero declarations. Diagnostics use the first declaration item's compiler line, including later-item failures. The compiler retains the original declaration in executable work.

Runtime93 consumes only strict-only declaration lists with an absent body. This step changes the work queue and no value, owner, environment or cache. Code strictness is established by compilation; the declaration does not mutate caller frames at runtime.

The public source guard requires the unit CODE flag to equal the existing compiler projection. A source declaration forces that projection even in a program without functions or calls. The no-declaration fast path requires a false unit flag. Existing function descriptor reconstruction checks each function's own CODE flag. No global same-file function-flag equality is imposed: future supported declare blocks can affect function compilation contexts separately.

The new Boolean metadata owns no roots. Suspended state checks reuse existing frame, alias, heap, default-cache and source-origin invariants. Arbitrary legitimate runtime values remain valid when the source flag is consistent. Five original unit-flag mutations incorrectly survived zero/full public resume before the guard repair. Function-flag mutations already rejected; their negative controls remain retained.

Registered builtin bodies already stop explicitly in call preparation. The compiler's builtin occupancy and special-write facts do not execute those bodies. Retained strict/weak strlen and in_array probes therefore remain builtin-execution boundaries rather than claimed coercion agreements. No typed receive, ARGSTRICT field, return metadata or reference-return admission is part of this change.

Final source/phase, flag-protocol, ownership/resumption and no-strict historical bridges are bound to the reviewed input manifest in the accompanying evidence. This prerequisite does not complete the call family or all declare directives.

The [independent review](../../coverage/semantics/strict-declaration-review.json)
binds final917/309b046c. Its21 retained source profiles contain18 native agreements
and three explicit encoding/type boundaries; seven additional builtin profiles
remain Unsupported. Two cache programs pass543 state/resumption assertions.
Three no-directive programs preserve entire909 states at seven cuts after removing
only new false CODE.STRICT fields. Retained and fresh17-control protocol runs each
pass168 assertions. Source sets overlap and are not added as distinct programs.

The paired compiler gate retains37 exact phase/line comparisons, two other-directive
boundaries and47 source projections. Historical910/912 preparation,913 unguarded
unit metadata and917/15db packaging precede final917/309b and remain distinct.
Typed parameter/return verification is the next increment; cached defaults must
retain successful evaluation before type checking, caller strictness governs
arguments and callee strictness governs returns. Full callable integration and
final all-source, full-syntax and fresh offline gates remain required.
