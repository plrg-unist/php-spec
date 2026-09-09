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

Evidence derives from `vendor/php-src/Zend/zend_operators.c` (`zend_compare`,
`zendi_smart_strcmp`, `_is_numeric_string_ex`) and `zend_hash.c`
(`zend_hash_compare_impl`); `zend_compile_greater` establishes evaluation order.
`tests/semantics/comparison.py` covers original source, compiler folding,
scanner boundaries, array identity/cycles, delayed operands and resumed states.
The full source campaign also includes retained phase/line originals and errors.
Objects, resources, callback-driven comparisons and engine stack exhaustion
remain pending; this module does not close the complete operator family.
