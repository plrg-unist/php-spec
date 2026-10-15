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

Module404 stages `+` when the left operand is a leading-numeric string and both
direct CVs already select live, initially untyped reference cells. Zend's
`add_function_slow` dereferences both operands before conversion; each scalar
numeric holder is filled before its warning. A handler's write to the converted
operand does not replace that holder, while the next conversion reads its already
selected referent. A second warning likewise retains its captured number even if
the handler returns false and changes the cell again. Selected pointers and scalar
holders add no owners. A supplied handler throw discards the addition without
delivering a result. Initial selection and pre-callback input snapshots are checked;
post-callback holders remain historical. Three exact originals and 321 genuine SL
premises retain their cuts in the [ADD ledger](../../coverage/semantics/arithmetic-warning-review.json).
Plain CVs, unlike physical slot classes, copied operands, right-only warning
ingress, owning/expired replacements, failed LEFT conversion and wider
arithmetic/exit paths remain required; existing integer-operator evidence is unchanged.

Failed RIGHT conversion on this selected-cell route now raises TypeError using
both live raw scalar types, rather than earlier numeric holders. The unfinished
marker is removed before ordinary caller Throwable search; the assignment stays
unchanged. Conversely, a completed RIGHT warning still delivers its cached number
even when the live pair would now fail conversion. Two exact originals and 82
author plus 77 independent genuine SL premises check these distinct routes,
source/phase/expiry guards, sole Error ownership and budget resumption in the
[ADD failure ledger](../../coverage/semantics/arithmetic-failure-review.json).

The same bounded CV/reference-cell route now stages leading-numeric-string `/`.
Zend's `div_function` dereferences both operands before conversion; each numeric
holder is filled before its warning. The divisor is tested after conversion, so a
handler-written zero raises DivisionByZeroError, while a second warning retains
captured zero even if its handler writes live7 and returns false. The DIV marker is
removed before ordinary numeric/error delivery: the real caller tail receives a
fresh Error at the operator line and the assignment remains unchanged. Two exact
originals and 130 author plus 94 independent genuine SL premises retain their cuts
in the [DIV ledger](../../coverage/semantics/division-warning-review.json). Initial
selection, fresh input snapshots, historical resume holders, sole Error ownership,
default Warning and budget resumption are checked. Wider operands, callbacks and
lifecycle paths remain required; the ADD bodies and evidence are unchanged.

Unary `+`/`-` now suspend leading-numeric warnings from defined non-reference
CVs through named handlers. Zend's `zend_compile_unary_pm` lowers to multiplication
by fixed `+1`/`-1`; the operand instruction line governs the warning. The converted
number is captured before dispatch, so handler writes cannot replace it.
Fresh capture/dispatch snapshots are authenticated; entered caller frames and
resumed holders stay historical and add no roots. A supplied throw discards the
unfinished marker. Its Throwable keeps its identity and null Previous; no result
reaches the destination.
Three exact originals and 227 author plus 96 independent genuine SL premises
check negative boundary float delivery, false fallback, public snapshot/message
rejection, ownership and budget resumption in the
[unary ledger](../../coverage/semantics/unary-warning-review.json). Other producers,
references/owning operands, callbacks and lifecycle forms remain required.

Bitwise NOT now retains a finite in-range fractional float's converted long before its
precision-loss deprecation. The bounded producer accepts a defined non-reference
CV and named handler. Fresh capture/dispatch equals the CV; saved callback frames
and resumed integer holders stay historical, without adding roots. Complement
follows callback return; a supplied throw discards the marker and preserves the
unchanged destination. Three exact originals and 227 author plus 97 independent
SL premises check live 99, negative truncation, false fallback on the operand line,
public snapshot/diagnostic rejection and budget resumption in the
[BITNOT ledger](../../coverage/semantics/bitnot-warning-review.json).
Range/NaN, other operands, callbacks and lifecycle forms remain required.

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
