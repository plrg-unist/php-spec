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

[Changed opposing operands](../../coverage/semantics/stringable-redispatch-comparison-review.json)
can now invoke a second ordinary Stringable cast against the saved first string.
Captured old cells remain distinct from rebound property slots, and successful
leaf equality resumes future entries and the selected body/fallthrough. The first
caster's finally finishes before the second enters; a supplied TypeError preserves
the aggregate guard through the second finally, then reaches caller catch/finally
after actual pair unwind. Wider object handlers and lifetimes remain open.

[Changed non-Stringable leaves](../../coverage/semantics/nonstringable-redispatch-review.json)
now finish when the second implicit comparison cast meets a live stdClass or
standard source object with no effective method. Signed nonzero order skips later
casters and resumes the original case scan. Array pins, retained property cells
and current writes stay distinct; first-caster supplied-error/finally and a fresh
comparison prove guard cleanup on both normal and throw paths.

[Finite Throwable leaves](../../coverage/semantics/throwable-string-comparison-review.json)
now format their internal handler atomically and persist the root cache only on
the actual case comparison. Count/key/earlier-value skips remain cold; nested
array equality resumes the selected body and fallthrough without later case
evaluation. Root source overrides retain the ordinary callback route.

[Numeric Notice leaves402](../../coverage/semantics/object-numeric-comparison-review.json)
now retain the actual case source and cursor while a failed object-to-int/float
cast invokes the error handler. Live slot/cell mutation and pinned old array
rows stay distinct; zero resumes later entries and body-only fallthrough, while
nonzero skips later casts. Notice→Stringable→Notice handoffs preserve the original
consumer. Thrown handlers now finish a
[bounded C remainder](../../coverage/semantics/pending-exception-comparison-review.json):
later registered callbacks and source casts are skipped, while excluded numeric
Notices may still display. The original error reaches caller catch/finally with
case bodies unentered; fresh comparison of the unchanged left observes the changed
right after unwind. Throwable formatting and wider effects remain bounded.

[Pending Throwable leaves](../../coverage/semantics/pending-throwable-comparison-review.json)
now skip the builtin or inherited internal string handler in that authenticated
numeric remainder. Signed nonzero order stops the original case comparison before
later default Notices. Cold/warm caches, previous links and the original thrown
identity survive; real post-catch formatting and fresh comparison prove cleanup.

[Builtin stdClass numeric leaves](../../coverage/semantics/stdclass-numeric-comparison-review.json)
also retain the original case, array/property cursor and guards through both
Notices. Restored SECOND float dispatch uses saved 1.0 rather than a changed
cell, including same-TypeError/finally cleanup and unchanged-left fresh comparison.

[Throwable numeric leaves](../../coverage/semantics/throwable-numeric-comparison-review.json)
retain builtin/source class images and saved float targets across restored
second Notices. Throwing the original compared Exception preserves its
previous link and cold cache through handler finally and caller catch/finally;
the unchanged left array then compares false against the changed right. Wider limits remain.

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
exact sources and 576 reached premises/28 raw steps pass. That cut left mixed
membership and guarded projection open; broader handlers/control remain required.
[Mixed ordinary tables](../../coverage/semantics/mixed-property-stringable-comparison-review.json)
now retain the old concrete generation across case casts while dynamic writes
create copied buckets. Later comparisons use the current map. Early skips, delayed
default/fallthrough, old-table recursion and the identical thrown TypeError through
caller catch/finally retain six exact sources and focused state evidence.
[Materialization during direct comparison](../../coverage/semantics/direct-table-comparison-review.json)
now keeps an outer direct case comparison on its original inline slots while a
nested comparison uses newly created tables and a separate recursion guard. The
same TypeError crosses both caster finally blocks and reaches caller catch/finally;
later cases remain unvisited. Three exact sources and focused state evidence pass.
[Fast projections in case casts](../../coverage/semantics/direct-projection-comparison-review.json)
now preserve that object guard without materializing cached tables. Projected
arrays have independent guards; the identical thrown TypeError crosses both
caster finally blocks and reaches caller catch/finally. Fresh comparisons on the
unchanged object and array identities confirm guard cleanup.
[Fiber comparison transfers](../../coverage/semantics/fiber-aggregate-stringable-comparison-review.json)
now retain the parked array guard through injected TypeError and caster finally
entry, then remove it on pair unwind before caller catch/finally entry. Same-table
equality precedes the guard; broader close/destructor lifetimes remain open.
