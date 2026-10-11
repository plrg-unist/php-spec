# Ordinary operators and casts

The source compiler and runtime now pair the ordinary `%`, `**`, `<<`, `>>`,
`&`, `|`, `^` and `.` operators, bitwise `~`, casts to bool/int/float/string/array,
and `(void)` with their checked source occurrences. This extends the existing
arithmetic, comparison and logical paths for current scalar and array values.
Object casts, resources, object protocols and request-environment access still
require their own value and execution models.

## Evaluation and diagnostics

Operands evaluate left to right. Direct compiled variable operands may retain a
delayed read until the final operator; computed names, dimensions and expression
results retain their own value-copy timing. The operator uses the compiler's
ending context for conversions and delayed reads. Parser-folded literal
concatenations used as variable names remain distinguishable from unary or
ternary expressions that merely produce the same bytes.

For two defined direct CV operands, implicit integer conversion in `%`, `<<`,
`>>` and mixed scalar `&`, `|`, `^` suspends through warning/deprecation handlers.
Conversions capture the number and original float-string before diagnostics.
`%` and shifts dereference the RHS after left conversion; bitwise operations
dereference both before conversion and retain their original numeric dispatch.
Borrowed reference pointers add no owner. Each notice reads the current handler
registry; a thrown handler prevents later conversion notices and the result.
The [review ledger](../../coverage/semantics/integer-operator-warning-review.json)
keeps source and genuine production-SL state checks at their tested revisions.
Evaluated literal/unary/ternary copies and reference-assignment/named byref-call
results now keep their original operands as real owners; selected pointers and
conversion snapshots add no owner. Rebinding the sole global owner preserves
an owning reference result, and two operands may own the same cell twice.
Bitwise conversion follows Zend's physical opcode order: CONST1, TMP2, VAR4,
CV8, with lower-ranked left slots swapped before conversion. Source evaluation
remains left to right. This determines callback order, saved integers and the
TypeError operand order; `%` and shifts retain left-first conversion.
The [COPY ledger](../../coverage/semantics/integer-operator-copy-review.json)
binds 37 source cases and 714 reached conditions, preserving the original swap mismatch.
Wider bitwise producer classes and object conversion remain open. Expired
pointers stay Unsupported; six earlier callback-unset native originals crashed with
signal11, with no diagnosed engine cause or agreement claim.

Concatenation has an additional compile/runtime distinction. The compiler visits
both operands before converting known scalar operands and queuing conversion
warnings. At execution, known array operands produce their conversion warnings
before delayed variable reads at the final operator. Captured operand roots stay
live throughout conversion and evaluation. This preserves warning order under
rebinding, singleton references, COW and cycles.

Arithmetic and bitwise conversion use the existing pure SpecTec numeric and byte
helpers, including signed 64-bit boundaries, binary64 values, string operands,
pinned power behavior and conversion diagnostics. Explicit casts keep their
separate rules: casts to int do not reuse implicit arithmetic notices; array casts
preserve array values with COW, turn null into an empty array, and wrap other
current scalar values at key zero. `(void)` evaluates and discards its operand,
retaining reads, warnings and side effects.

## Evidence and remaining work

`tests/semantics/ordinary.py` embeds 1,506 exact source inputs and checks 25 source
states with 2,875 assertions, including dense budgets 0–100. The source additions
retain 805 initial operator/cast originals, 28 concat timing originals, and 673
admitted expansion originals. Independent review adds 62 source controls for
operand timing, conversion order, array ownership and parser name provenance.
The [combined source report](../../coverage/semantics/source.json) records 4,407
exact comparisons and 25 outcome negatives. It and the
[state report](../../coverage/semantics/ordinary.json) bind the unchanged
`a8f6aa0cac996578befe8fa49621af2fdc214a44e4d9612a4cb8ce5dcee05691` identity
(799 inputs). The [independent audit](../../coverage/semantics/ordinary-campaign-audit.json)
checks complete ordered source bytes, observations and archive membership.

The expansion archive preserves all 680 originals. Its seven request-environment
boundaries remain explicit Unsupported results, excluded from admitted source
comparisons and recorded in the
[boundary archive](../../coverage/semantics/ordinary-request-environment-boundaries.json).
They remain implementation work. Unpack, destructuring, foreach, remaining
coalesce and quiet-write forms,
frames, objects and the other obligations in PLAN remain unfinished; these
operator checks do not close a constructor family or the complete PHP core.
