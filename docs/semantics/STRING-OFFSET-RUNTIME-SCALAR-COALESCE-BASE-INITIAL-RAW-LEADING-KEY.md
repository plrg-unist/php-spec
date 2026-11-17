# Emitted coalesce bases and initial raw leading keys

This bounded slice preserves an exact selected INTERNED string header when an
emitted ordinary NULL or STRING expression is the left operand of `??` and its
right operand is a raw string literal. The captured raw CV offset retains its
original bytes and integer prefix through a returning Warning handler, including
ordinary and initially referenced keys. Selection uses nullness: empty and `"0"`
strings remain nonnull.

The new base rule requires emitted left/root reads, the whole typed runtime
certificate, and the raw RHS literal's exact source, pool and INTERNED header even
when the left value is nonnull. The existing certificate retains immediate source
identities, actual CODE lines, precision, demanded child values and quiet full-state
results. Variable/dimension/property quiet-access left operands remain excluded;
source, ownership, key-cell and continuation guards are unchanged.

The pinned PHP 8.5.10 compiler's `zend_compile_coalesce` emits COALESCE followed by
the fallback's QM_ASSIGN; the VM COALESCE handler selects by type greater than
NULL. This models the observable value/header selection without importing opcode
storage strategies.

Two exact originals/native runs and two subsequent source agreements are separate
from 90 prelaw conditions, 250 author fixture conditions (118 derived), and 328
independent fixture conditions (228 derived). The prelaw Unsupported outcomes have
zero agreement credit. Every native ran once; later checks reused its exact bytes,
profile and observations. No execution failure occurred in this slice.

The independent whole-six review and one actual composition bind frozen source
`71c8f7f6a59ab324ba011ac8f5584561aa552b29` to actual/SAME
`c4e2fc12a7c937aa988bcd39a7e991efaf0fc7a9`. The sole joined production-SL load used
509 modules, passed in 16.882306845858693 seconds at cap60, and adds zero source
agreement. The [review record](../../coverage/semantics/string-offset-runtime-scalar-coalesce-base-initial-raw-leading-key-review.json)
contains the immutable tuple and external recovery pointers.

Wider producers, carriers, contexts and lifetimes remain partial. Complete core,
every exact hold, reserve93807cdd6/255 and inventory169/306/closed0+1 remain
unchanged.
