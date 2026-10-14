# Value comparisons

`52-comparison.watsup` defines `==`, `!=`, `<`, `<=`, `>`, `>=` and `<=>`
for null, booleans, integers, binary64 floats, byte strings and ordered arrays.
The checked source compiler folds eligible constants; ordinary evaluation uses
captured operands and delayed variable reads. `>` and `>=` evaluate operands
in original source order, then compare the resulting values in reverse order.
With NaN or arrays having missing keys, the three-way comparison can return
+1 in both directions; the `>` operator may therefore be false in both
directions. Negating a forward comparison is incorrect.

Null/string comparisons treat null as the empty string. Other boolean/null
comparisons use truth without emitting NaN conversion warnings. Number/string
comparison uses numeric parsing only for a complete numeric string and otherwise
compares formatted numeric bytes. String/string comparison additionally retains
integer overflow provenance from the numeric scanner: twenty significant digits
in the integer prefix set overflow before a decimal/exponent suffix is examined,
even when that suffix rescales the final float into integer range. Equal floats
from same-sign overflowed integer prefixes, and equal infinities, fall back to
original byte comparison. This follows the pinned engine, including its unusual
prefix behavior; the original draft disagreements remain in the ledger.

Array comparison first handles identical container identity, then recursion on
the left operand, element counts, and exact normalized key lookup in left
insertion order. Distinct insertion orders alone do not imply inequality.
Values behind references are dereferenced. A revisited left array raises
`Error: Nesting level too deep - recursive dependency?`; input roots survive
comparison and budget resumption. Strict identity remains a separate operation.

[Numeric object Notices](../../coverage/semantics/object-numeric-comparison-review.json)
now suspend ordinary source instances compared with int/float through module402
and the existing error-handler machinery. The failed cast captures the numeric
type; after handling, private 1/1.0 is compared with the captured opposing CV,
pre-unwrapped cell, property/array location or copied value. A newly read ordinary
object emits a second Notice against that saved number, without rereading the
original pointer afterward. Numeric conversion does not invoke `__toString`.
Aggregate cursors retain their original arrays/declared slots and guards across
the callback; only zero resumes later entries. Notice↔Stringable handoffs preserve
the same source consumer and selected-case continuation.

The raw handler is disabled during its own body and restored before subsequent
Notice dispatch. A handler throw can cancel the numeric continuation only when
previewing the remaining comparison yields a terminal order with no state change.
A future callback, observable default diagnostic, materialization, cache update or recursion
instead remains Unsupported. Documentary receiver/leaf images add no owner;
actual operands, cursor pins and callback selection retain their existing roots.
Internal/custom comparison handlers, legacy materialized callbacks without a
retained cursor and wider handler/lifetime behavior remain open.

Evidence derives from `vendor/php-src/Zend/zend_operators.c` (`zend_compare`,
`zendi_smart_strcmp`, `_is_numeric_string_ex`) and `zend_hash.c`
(`zend_hash_compare_impl`); `zend_compile_greater` establishes evaluation order.
`tests/semantics/comparison.py` covers original source, compiler folding,
scanner boundaries, array identity/cycles, delayed operands and resumed states.
The full source campaign also includes retained phase/line originals and errors.
Full object/resource handler coverage and engine stack exhaustion remain pending;
these bounded increments do not close the complete operator family.
