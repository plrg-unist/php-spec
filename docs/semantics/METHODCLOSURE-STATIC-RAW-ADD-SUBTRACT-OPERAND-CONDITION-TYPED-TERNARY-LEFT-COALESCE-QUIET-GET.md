# Quiet integer addition and subtraction

The quiet static USER methodclosure selector certificate admits Add/Subtract
when both closed typed children convert without warning to signed64 integers
and the mathematical result fits signed64. Results retain exact INT tags:
NULL/BOOL and numeric INT STRING children undergo numeric conversion before
arithmetic. STRING `00` therefore contributes zero despite being truthy as a
string. INT0 stays nonnull in COALESCE; a falsey arithmetic INT0 selects the SHORT
fallback and preserves that fallback's tag.

Two constructor-new operand clauses authenticate each root and both proper
SOURCE children, require typed `Some(value)` and two independent
`coerce_number(value) = COERCED (NINT i) false` results, then guard the direct
sum or difference with `long_range`. Two dedicated FULL fallbacks require old
byte-proof `None`, preserving every old `Some(bytes)` result. Every cycle
descends proper children. All old typed/byte helpers, shared trees, SHORT/truth,
non-NUL, receipt/46, cache and owner/lifetime bodies remain literal; no arithmetic
helper, runtime carrier or native evaluation fallback is added.

The target is pinned PHP 8.5.10 CLI NTS64. Zend `add_function_fast` and
`sub_function_fast`, their scalar-conversion slow routes and `fast_long_add_function`/
`fast_long_sub_function` return LONG for fitting integer results and DOUBLE on
overflow. The certificate excludes ADD array union through its typed scalar and
quiet NINT premises. Subtraction uses the direct difference: MIN−MIN is INT0,
even though negating MIN separately would overflow. MIN+MAX is INT(-1).

Four positive originals change only their selector lines, preserving callbacks,
profile, streams and cache/owner histories. A selected TRUE−NULL result supplies
INT1 to a real method name, distinguishing reversed subtraction. Two separate
originals intentionally contain MAX+1/MIN+(-1) and MIN−1/MAX−(-1) overflow forms.
All six originals run natively once; saved exact bytes/path/CWD/profile are
reused. Source-first SUM28 completed quiet integer results (Add15/Subtract13)
remain separate from complete SOURCE30 facts. All four deliberate overflows
produce the expected FLOAT bits; ten inherited fitting arithmetic observations
in those controls remain distinct. A collector assumption was corrected to
separate those observations, with no native/model/observer rerun or source change.

Actual-site, per-operator scalar/numeric, selected/skipped SOURCE, fences,
child-valid overflow, compatibility and authority fixtures retain the original
caps. The compatibility cut admits typed Add(0,0) while the old raw NOT/CONCAT
grammar and wider typed CONCAT parent still refuse it. No maintained assertion
tail changes or historical campaign renewal are needed. Fixtures, overflow
Unsupported controls and the production load carry zero source-agreement credit.
The [review](../../coverage/semantics/magic-property-methodclosure-static-raw-add-subtract-operand-condition-typed-ternary-left-coalesce-quiet-get-review.json)
binds source, validation and fixed integration identities.

FLOAT/numeric-float, output overflow, warnings, nonnumeric/NUL/CV/owning values,
wider raw parents/selectors and lifetimes remain partial. The full-core objective,
inventory and exact holds are unchanged; this is a bounded selector certificate.
