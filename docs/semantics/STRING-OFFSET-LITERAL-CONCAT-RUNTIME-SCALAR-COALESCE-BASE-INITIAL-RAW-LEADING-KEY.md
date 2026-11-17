# Folded literal CONCAT coalesce bases

A coalesce left operand consisting only of raw STRING literals and CONCAT nodes
preserves its selected INTERNED header and frozen initial raw leading CV offset
through a returning Warning handler, including when the right operand is an
emitted full ternary. Falsey `"0"` remains nonnull and selects the left operand.
Existing current/reference-key capture, owner and continuation bounds apply.

At the pinned PHP 8.5.10 target, `zend_ast_create_concat_op` folds these literal
trees before runtime; `zend_insert_literal` supplies the actual INTERNED operand.
Nested child CONCAT nodes retain source occurrences while their compiled facts
are absent. The rule in `425-string-offset-read-continuations.watsup` therefore
authenticates the folded root CODE, PSTRING read, header and precision together
with the exact full SOURCE subtree through `pcwalk`. It demands no child compiled
pools, CODE or precision descriptors. The literal-byte left classifier also
retains the existing raw STRING leaf route.

`zend_compile_coalesce`, `ZEND_COALESCE` and `ZEND_QM_ASSIGN` establish the
nonnull selection. The immediate emitted RHS source stays authenticated while
its deeper skipped facts remain undemanded. Existing literal RHS header proofs
remain mandatory. At frozen source531, mixed INT/FLOAT leaves reject. The later
[raw-integer extension](STRING-OFFSET-LITERAL-INTEGER-CONCAT-RUNTIME-SCALAR-COALESCE-BASE-INITIAL-RAW-LEADING-KEY.md)
promotes its reviewed integer scope. Metadata-only SOURCE substitutions, wrong
root values/precision and raw or REQUEST result carriers still reject.

Two original sources reuse two native executions collected once. Baseline
Unsupported2 and prelaw120 retain zero source credit. Author263/173 and
independent410/310 are separate first-pass SL508 fixture cuts; the peer compiler
and runtime finish within their original 120/180-second caps, with no failures.
Independent whole-source review then clears actual=joined `c021c2220bad`, whose
sole production SL509 load passes in 16.995046246 seconds with source credit0.
The immutable actual/SAME tuple binds those results; metadata adds no execution.

Mixed/coerced or wider producers, carriers, owners and lifetimes remain partial.
All exact holds, reserve93807cdd6/255 and inventory169/306 remain unchanged.
The [review record](../../coverage/semantics/string-offset-literal-concat-runtime-scalar-coalesce-base-initial-raw-leading-key-review.json)
links the frozen source manifest, independent counterexamples and external raw
evidence. These records establish this bounded behavior only; full core remains
unfinished.
