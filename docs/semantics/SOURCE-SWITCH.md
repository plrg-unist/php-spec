# Switch source increment

The switch compiler compiles the subject, folds the eligible leading case
conditions, then compiles all case conditions and bodies. It preserves the
order of constant-fold warnings, semicolon-case deprecations, and static errors.
At runtime, cases are compared in source order until the first match; a default
is selected only if none matches. Execution then falls through bodies until a
break, continue, return, or error. Typed loop depth gives `continue` targeting
a switch its matching compile warning. The subject remains live through the
chosen bodies: a CV or reference is reread after case effects, while a temporary
owns its value until normal or abrupt switch exit.

Compiled boolean subjects have a distinct branch path. The compiler emits an
authenticated `CODESWITCH_BOOL` fact for a constant true or false subject;
runtime compares each case through boolean conversion, including the NaN
warning. An evaluated variable or assignment subject uses ordinary loose
equality. `CODESWITCH_COMPARE` records the post-condition line, and source
recompilation checks the switch root and comparison descriptors together.

The rules are in `124-switch-compiler.watsup` and `125-switch-runtime.watsup`.
The pinned engine anchors are `determine_switch_jumptable_type` and
`zend_compile_switch` in `vendor/php-src/Zend/zend_compile.c`, plus comparison,
conditional jump, and free handlers in `Zend/zend_vm_def.h`.
[The review record](../../coverage/semantics/switch-review.json) distinguishes
the maintained source/compiler/paused tests from independent original-source
and ownership audits. Direct ordinary Stringable/string comparisons now suspend
through 392 while preserving the original subject and captured opposite pointer.
The [comparison increment](../../coverage/semantics/stringable-comparison-review.json)
checks delayed default, body-only fallthrough without later case evaluation, and
the same TypeError caught after caster restoration, followed by finally entry.
The caster first reenters a nested scalar Switch.

[Recursive comparison through 394](../../coverage/semantics/aggregate-stringable-comparison-review.json)
retains real enclosing array/property owners and the active left recursion guard
while a reached Stringable/string leaf casts. Early count/key/value differences
still short-circuit. Successive casters resume the same comparison; nested recursion
Error can be caught inside the caster, and a thrown TypeError reaches caller catch
then finally entry. The restart fixture reads the authentic compiled case marker,
including its folded line. The preceding cut remains frozen.
[Property-table comparison](../../coverage/semantics/materialized-stringable-comparison-review.json)
now covers retained stdClass table snapshots, initialized public declared-table
slots and successive casts. Identical tables win before the active-left guard;
ARRAY aliases expose the same table recursion domain. The same TypeError reaches
caller catch and then finally entry, with later properties/cases skipped. Six new
exact sources and 576 reached premises/28 raw steps pass. Mixed membership, guarded
projection, broader handlers and wider control remain required.
[Fiber comparison transfers](../../coverage/semantics/fiber-aggregate-stringable-comparison-review.json)
now retain the parked array guard through injected TypeError and caster finally
entry, then remove it on pair unwind before caller catch/finally entry. Same-table
equality precedes the guard; broader close/destructor lifetimes remain open.
